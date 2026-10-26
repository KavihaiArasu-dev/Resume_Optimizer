"""
Unit and Integration Tests for ResumeParser and Document Extraction.
Tests PDF, DOCX, TXT, text paste, OCR fallback, and structured section parsing.
"""
import pytest
import os
import tempfile
from app.services.parser.resume_parser import resume_parser
from app.schemas.schemas import ParsedResume
from tests.sample_data import SAMPLE_PAIRS


@pytest.mark.asyncio
async def test_parse_raw_text():
    """Verify parsing direct pasted raw text into structured JSON."""
    raw_text = SAMPLE_PAIRS[0]["resume"]
    parsed = resume_parser.parse_raw_text(raw_text)

    assert isinstance(parsed, ParsedResume)
    assert parsed.candidate.name == "Alex Morgan"
    assert parsed.candidate.email == "alex.morgan@email.com"
    assert "San Francisco" in parsed.candidate.location
    assert "555" in parsed.candidate.phone
    assert len(parsed.experience) >= 2
    assert len(parsed.education) >= 1
    assert len(parsed.skills.programming) > 0
    assert "TypeScript" in parsed.skills.programming or "Javascript" in parsed.skills.programming or "Python" in parsed.skills.programming
    assert len(parsed.projects) >= 1


@pytest.mark.asyncio
async def test_parse_txt_file():
    """Verify parsing a temporary .txt resume file."""
    raw_text = SAMPLE_PAIRS[1]["resume"]
    with tempfile.NamedTemporaryFile("w+", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write(raw_text)
        temp_path = f.name

    try:
        parsed = await resume_parser.parse_resume(temp_path, "txt")
        assert parsed.candidate.name == "Jordan Lee"
        assert parsed.candidate.email == "jordan.lee@analytics.com"
        assert len(parsed.experience) >= 2
        assert "Tableau" in parsed.skills.tools or "Tableau" in parsed.skills.data or len(parsed.skills.programming) > 0
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


@pytest.mark.asyncio
async def test_parse_docx_file():
    """Verify parsing a Word .docx resume file using python-docx."""
    from docx import Document

    raw_text = SAMPLE_PAIRS[3]["resume"]
    doc = Document()
    for line in raw_text.split("\n"):
        doc.add_paragraph(line)

    with tempfile.NamedTemporaryFile("wb", suffix=".docx", delete=False) as f:
        temp_path = f.name
    doc.save(temp_path)

    try:
        parsed = await resume_parser.parse_resume(temp_path, "docx")
        assert parsed.candidate.name == "Marcus Vance"
        assert "marcus.vance@infra.dev" in parsed.candidate.email
        assert len(parsed.experience) >= 1
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


@pytest.mark.asyncio
async def test_ocr_fallback_mechanism():
    """Verify OCR fallback executes gracefully when PDF has no selectable text."""
    # Test OCR fallback with a non-selectable / mock image PDF
    import fitz
    doc = fitz.open()
    page = doc.new_page(width=612, height=792)  # Empty blank page with no selectable text
    # Draw a line so it's a valid PDF with no text stream
    page.draw_line(fitz.Point(50, 50), fitz.Point(500, 50))

    with tempfile.NamedTemporaryFile("wb", suffix=".pdf", delete=False) as f:
        temp_pdf = f.name
    doc.save(temp_pdf)
    doc.close()

    try:
        # Should gracefully invoke OCR fallback and return fallback structure without crashing
        parsed = await resume_parser.parse_resume(temp_pdf, "pdf")
        assert isinstance(parsed, ParsedResume)
    finally:
        if os.path.exists(temp_pdf):
            os.remove(temp_pdf)


def test_contact_extraction_regex():
    """Verify precise email, phone, location, linkedin, and github extraction."""
    text = (
        "Jane Doe\n"
        "jane.doe@example.com | (123) 456-7890 | Austin, TX\n"
        "linkedin.com/in/janedoe | github.com/janedoe | https://janedoe.me\n"
    )
    contact = resume_parser.extract_contact_info(text)
    assert contact.name == "Jane Doe"
    assert contact.email == "jane.doe@example.com"
    assert "456-7890" in contact.phone
    assert "Austin, TX" in contact.location
    assert "linkedin.com/in/janedoe" in contact.linkedin
    assert "github.com/janedoe" in contact.github
