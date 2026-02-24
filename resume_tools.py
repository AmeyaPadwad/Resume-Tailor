import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.documents import Document
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from prompts import resume_score_prompt, resume_tailor_prompt

# Loading Environment Variables
load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

# Loading Model
MODEL = "llama-3.1-8b-instant"
LLM = ChatGroq(
    model="llama-3.1-8b-instant", api_key=os.environ["GROQ_API_KEY"], temperature=0
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


def tailor_resume(master_resume_pdf_path, job_description):
    pdf_context, jd_text_context = prepare_data(master_resume_pdf_path, job_description)
    original_resume_score = get_resume_score(pdf_context, jd_text_context)
    resume_change_suggestions = get_resume_change_suggestions(
        pdf_context, jd_text_context
    )

    return original_resume_score, resume_change_suggestions
