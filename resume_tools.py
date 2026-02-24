import os
import json
from dotenv import load_dotenv

from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.documents import Document
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from prompts import resume_score_prompt, resume_tailor_prompt
from config import PATHS
from pdf_tools import docx_to_pdf, copy_docx, apply_changes_to_docx

# Loading Environment Variables
load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

# Loading config constants
MASTER_RESUME_DOCX_PATH = PATHS["MASTER_RESUME_DOCX_PATH"]
MASTER_RESUME_PDF_PATH = PATHS["MASTER_RESUME_PDF_PATH"]
RESUME_DIR = PATHS["RESUME_DIR"]
TAILORED_DIR = PATHS["TAILORED_DIR"]

# Loading Model
MODEL = "llama-3.1-8b-instant"
LLM = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
    temperature=0,
    model_kwargs={"response_format": {"type": "json_object"}},
)


def prepare_data(master_resume_pdf_path: str, job_description: str) -> tuple[str, str]:
    """
    Load and extract text content from a resume PDF and a job description string.

    Args:
        master_resume_pdf_path (str): File path to the master resume PDF.
        job_description (str): Raw job description text.

    Returns:
        tuple[str, str]: A tuple of (pdf_context, jd_context) where both are plain strings ready to be injected into a prompt template.
    """
    # Load pdf
    pdf_loader = PyMuPDFLoader(master_resume_pdf_path)
    pdf_docs = pdf_loader.load()
    pdf_context = "\n\n".join(d.page_content for d in pdf_docs)

    # Load Job Description text
    jd_text_context = Document(
        page_content=job_description, metadata={"source": "in-memory string"}
    ).page_content

    return pdf_context, jd_text_context


def get_resume_score(pdf_context: str, jd_text_context: str) -> str:
    """
    Score a resume against a job description using an LLM and return the result as a JSON string.

    Args:
        pdf_context (str): Extracted text content from the resume PDF.
        jd_text_context (str): Raw job description text.

    Returns:
        str: A JSON-formatted string containing:
            - score (int): Match score from 0 to 100.
            - scoreRationale (str): 1-2 sentence explanation of the score.
            - keywordGaps (list[str]): Keywords present in the JD but missing from the resume.
    """
    prompt = ChatPromptTemplate.from_template(resume_score_prompt)

    chain = prompt | LLM | StrOutputParser()
    result = chain.invoke(
        {"resume_context": pdf_context, "jd_context": jd_text_context}
    )

    return result


def get_resume_change_suggestions(pdf_context: str, jd_text_context: str) -> str:
    """
    Suggest resume bullet point rewrites tailored to a job description using an LLM.

    Args:
        pdf_context (str): Extracted text content from the resume PDF.
        jd_text_context (str): Raw job description text.

    Returns:
        str: A JSON-formatted string containing a list of bullet rewrite objects, each with:
            - original (str): The original bullet point from the resume.
            - rewritten (str): The improved version tailored to the job description.
    """
    prompt = ChatPromptTemplate.from_template(resume_tailor_prompt)

    chain = prompt | LLM | StrOutputParser()
    result = chain.invoke(
        {"resume_context": pdf_context, "jd_context": jd_text_context}
    )
    return result


def get_tailored_resume_path(job_id: int, company: str, title: str) -> str:
    """
    Generate a standardised file path for a tailored resume with the format {jobid}_{company}_{title}.docx.

    Args:
        job_id (int): The job ID from jobs.csv.
        company (str): Company name.
        title (str): Job title.

    Returns:
        str: file path e.g. /path/to/tailored/001_google_software_engineer.docx
    """

    filename = f"{job_id:03d}_{company}_{title}.docx"
    filepath = os.path.join(TAILORED_DIR, filename)

    return filepath


def edit_resume(
    changes: list[dict],
    job_id: int,
    company: str,
    title: str,
) -> str:
    """
    Apply LLM-suggested bullet rewrites while preserving formatting, and export back to PDF.

    Args:
        changes (list[dict]): List of {original, rewritten} dicts from the LLM.
        job_id (int): The job ID from jobs.csv.
        company (str): Company name.
        title (str): Job title.


    Returns:
        output_pdf_path (str): Destination path for the tailored .pdf file.

    Raises:
        RuntimeError: If docx to pdf conversion or PDF export fails.
    """
    if not os.path.exists(MASTER_RESUME_DOCX_PATH):
        raise FileNotFoundError(
            f"Master resume docx not found: {MASTER_RESUME_DOCX_PATH}"
        )

    # Step 1: Get tailored resume .docx path
    tailored_resume_docx_path = get_tailored_resume_path(job_id, company, title)

    # Step 2: Copy master resume docx to tailored resume path as the tailored resume file name
    copy_docx(MASTER_RESUME_DOCX_PATH, tailored_resume_docx_path)

    # Step 3: Apply LLM changes to the converted .docx
    apply_changes_to_docx(tailored_resume_docx_path, changes)

    # Step 4: Convert .docx to .pdf
    tailored_resume_pdf_path = tailored_resume_docx_path.replace(".docx", ".pdf")
    docx_to_pdf(tailored_resume_docx_path, tailored_resume_pdf_path)

    # Step 5: Always clean up the temp files
    if os.path.exists(tailored_resume_docx_path):
        os.remove(tailored_resume_docx_path)

    return tailored_resume_pdf_path


def tailor_resume(
    job_description: str,
    job_id: int,
    company: str,
    title: str,
) -> tuple[dict, list]:
    """
    Orchestrates the full resume tailoring pipeline for a given job description.

    Extracts resume and JD text, scores the resume against the JD, and generates
    bullet point rewrite suggestions — returning both as parsed Python objects.

    Args:
        job_description (str): Raw job description text.
        job_id (int): The job ID from jobs.csv.
        company (str): Company name.
        title (str): Job title.

    Returns:
        tuple[dict, list]: A tuple of (score_json, changes_list) where:
            - score_json (dict): Parsed score response containing:
                - score (int): Match score from 0 to 100.
                - scoreRationale (str): 1-2 sentence explanation of the score.
                - keywordGaps (list[str]): Keywords missing from the resume.
            - changes_list (list[dict]): Parsed list of bullet rewrite suggestions, each containing:
                - original (str): The original bullet point from the resume.
                - rewritten (str): The improved, JD-aligned version.
    """
    # Prepare data and invoke LLM calls
    pdf_context, jd_text_context = prepare_data(MASTER_RESUME_PDF_PATH, job_description)
    original_resume_score = get_resume_score(pdf_context, jd_text_context)
    resume_change_suggestions = get_resume_change_suggestions(
        pdf_context, jd_text_context
    )

    # Convert to JSON
    score_json = json.loads(original_resume_score)
    changes_list = json.loads(resume_change_suggestions)

    # Make edits to master resume
    tailored_resume_path = edit_resume(changes_list, job_id, company, title)

    return score_json, changes_list, tailored_resume_path
