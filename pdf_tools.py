import os
import base64
import shutil
import pythoncom
from docx.shared import RGBColor
from docx2pdf import convert
from docx import Document


def display_pdf(pdf_path: str) -> str:
    """
    Generate an HTML iframe element that displays a PDF file embedded as base64-encoded data.
    This function reads a PDF file from the specified file path, encodes it to base64, and returns an HTML iframe element that embeds the PDF for in-browser viewing.
    Args:
        pdf_path (str): The file path to the PDF document to be displayed.
    Returns:
        pdf_display (str): An HTML string containing an iframe element with the base64-encoded PDF data.
    """
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    # Embed PDF in an iframe via base64
    b64 = base64.b64encode(pdf_bytes).decode()
    pdf_display = f"""
        <iframe
            src="data:application/pdf;base64,{b64}#navpanes=0"
            width="100%" height="800px"
            style="border: 1px solid #ccc; border-radius: 6px;">
        </iframe>
    """
    return pdf_display


def docx_to_pdf(docx_path: str, output_pdf_path: str) -> str:
    """
    Convert a .docx file to PDF using docx2pdf (requires Microsoft Word on
    Windows/Mac, or LibreOffice on Linux).

    Args:
        docx_path (str): Path to the source .docx file.
        output_pdf_path (str): Destination path for the output PDF.

    Returns:
        str: Path to the saved PDF file.

    Raises:
        FileNotFoundError: If docx_path does not exist.
        RuntimeError: If the conversion fails.
    """
    if not os.path.exists(docx_path):
        raise FileNotFoundError(f".docx not found: {docx_path}")

    try:
        pythoncom.CoInitialize()
        convert(docx_path, output_pdf_path)
    except Exception as e:
        raise RuntimeError(f"PDF conversion failed: {e}")
    finally:
        pythoncom.CoUninitialize()

    return output_pdf_path


def copy_docx(source_path: str, destination_path: str):
    """
    Copy a docx file from one location to another and rename it.

    Args:
        source_path (str): Path to the source docx file.
        destination_path (str): Destination path for the copied docx.

    Returns:
        str: Path to the copied PDF file.

    Raises:
        FileNotFoundError: If source_path does not exist.
    """
    if not os.path.exists(source_path):
        raise FileNotFoundError(f"Source PDF not found: {source_path}")

    shutil.copy2(source_path, destination_path)


def _set_run_green(run):
    """Set a run's font color to green."""
    run.font.color.rgb = RGBColor(0x2E, 0x8B, 0x57)


def _replace_text_in_runs(paragraph, original: str, rewritten: str):
    """
    Replace text across runs in a paragraph while preserving per-run formatting.
    Handles cases where the target text is split across multiple runs.

    Strategy:
        1. Try a simple single-run replacement first.
        2. If the text spans runs, consolidate into the first matching run, clear the rest, and preserve the first run's formatting.

    Args:
        paragraph: A python-docx Paragraph object.
        original (str): The original text to find.
        rewritten (str): The replacement text.
    """
    full_text = "".join(r.text for r in paragraph.runs)
    if original not in full_text:
        return

    # Single-run replacement
    for run in paragraph.runs:
        if original in run.text:
            run.text = run.text.replace(original, rewritten)
            _set_run_green(run)
            return

    # Multi-run fallback: consolidate into first run, clear the rest
    first_run = paragraph.runs[0]
    first_run.text = full_text.replace(original, rewritten)
    _set_run_green(first_run)
    for run in paragraph.runs[1:]:
        run.text = ""


def apply_changes_to_docx(
    docx_path: str,
    changes: list[dict],
) -> str:
    """
    Apply LLM-suggested bullet rewrites to a .docx resume, preserving formatting.

    Args:
        docx_path (str): Path to the master resume .docx.
        changes (list[dict]): List of {original, rewritten} dicts from the LLM.

    Returns:
        str: Path to the saved output .docx file.

    Raises:
        FileNotFoundError: If docx_path does not exist.
    """
    if not os.path.exists(docx_path):
        raise FileNotFoundError(f"Source .docx not found: {docx_path}")

    doc = Document(docx_path)

    for change in changes:
        original = change.get("original", "").strip()
        rewritten = change.get("rewritten", "").strip()
        if not original or not rewritten:
            continue

        for paragraph in doc.paragraphs:
            para_text = paragraph.text.strip()

            # Exact match
            if original == para_text:
                _replace_text_in_runs(paragraph, original, rewritten)
                break

    doc.save(docx_path)
