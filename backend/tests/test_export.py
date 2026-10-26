"""
Unit and Integration Tests for ATS-Safe Export.
Tests PDF generation, 2x High-Resolution image rendering, and DOCX generation across templates.
"""
import pytest
from app.services.export.resume_generator import resume_generator
from app.services.parser.resume_parser import resume_parser
from tests.sample_data import SAMPLE_PAIRS


def test_ats_pdf_export_all_templates():
    """Verify ATS-safe PDF generation across Modern Executive, Classic Tech, and Compact templates."""
    resume = resume_parser.parse_raw_text(SAMPLE_PAIRS[0]["resume"])

    for template in ["modern", "classic", "compact"]:
        pdf_bytes = resume_generator.generate_pdf(resume, template=template)
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 2000
        # Check standard PDF magic header
        assert pdf_bytes.startswith(b"%PDF")


def test_high_res_image_export():
    """Verify high-resolution (2x+ / 300 DPI) image generation."""
    resume = resume_parser.parse_raw_text(SAMPLE_PAIRS[1]["resume"])

    # High-resolution PNG
    png_bytes = resume_generator.generate_high_res_image(
        resume, template="modern", scale=2.0, dpi=300, image_format="PNG"
    )
    assert isinstance(png_bytes, bytes)
    assert len(png_bytes) > 5000
    # Check PNG magic signature: \x89PNG\r\n\x1a\n
    assert png_bytes.startswith(b"\x89PNG")


def test_docx_export():
    """Verify clean ATS-safe Microsoft Word (.docx) generation."""
    resume = resume_parser.parse_raw_text(SAMPLE_PAIRS[2]["resume"])

    docx_bytes = resume_generator.generate_docx(resume, template="classic")
    assert isinstance(docx_bytes, bytes)
    assert len(docx_bytes) > 2000
    # Check ZIP magic signature for docx (PK\x03\x04)
    assert docx_bytes.startswith(b"PK")
