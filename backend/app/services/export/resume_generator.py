"""
ATS-Safe Resume Generator Service — Feature 3.
Generates:
1. ATS-safe PDF (single column, selectable text, standard headings, contact in body, no tables/textboxes)
2. High-resolution 2x+ image (PNG/JPG at 300 DPI)
3. ATS-safe DOCX export
Supports 3 templates:
- modern: Modern Executive
- classic: Classic Tech
- compact: Compact Engineering
"""
import io
import os
from typing import Dict, Any, Optional, List, Tuple
from app.schemas.schemas import ParsedResume

# ReportLab imports for ATS PDF
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, KeepTogether
from reportlab.lib.units import inch

# Pillow & PyMuPDF for high-res image
from PIL import Image
import fitz
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH


class ResumeGeneratorService:
    """Production ATS-safe PDF, Image and DOCX generator."""

    def generate_pdf(
        self,
        resume: ParsedResume,
        template: str = "modern",
    ) -> bytes:
        """
        Generate ATS-safe PDF.
        Strict single-column layout, standard section headings, selectable text,
        no tables, no text boxes, contact info in body.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            leftMargin=0.55 * inch,
            rightMargin=0.55 * inch,
            topMargin=0.55 * inch,
            bottomMargin=0.55 * inch,
        )

        styles = getSampleStyleSheet()

        # Template customizations
        if template == "classic":
            primary_color = colors.HexColor("#1A202C")
            heading_color = colors.HexColor("#2D3748")
            line_color = colors.HexColor("#CBD5E0")
            name_size = 20
            heading_size = 11
            body_size = 9.5
            font_name = "Times-Roman"
            font_bold = "Times-Bold"
            align_name = 1  # Centered
        elif template == "compact":
            primary_color = colors.HexColor("#0F172A")
            heading_color = colors.HexColor("#1E293B")
            line_color = colors.HexColor("#94A3B8")
            name_size = 18
            heading_size = 10.5
            body_size = 9.0
            font_name = "Helvetica"
            font_bold = "Helvetica-Bold"
            align_name = 0  # Left
        else:  # Modern Executive
            primary_color = colors.HexColor("#0F172A")
            heading_color = colors.HexColor("#1E3A8A")
            line_color = colors.HexColor("#3B82F6")
            name_size = 22
            heading_size = 11.5
            body_size = 9.5
            font_name = "Helvetica"
            font_bold = "Helvetica-Bold"
            align_name = 0  # Left

        # Base custom styles
        name_style = ParagraphStyle(
            "CandidateName",
            fontName=font_bold,
            fontSize=name_size,
            leading=name_size + 4,
            textColor=primary_color,
            alignment=align_name,
            spaceAfter=4,
        )

        contact_style = ParagraphStyle(
            "ContactInfo",
            fontName=font_name,
            fontSize=body_size - 0.5,
            leading=body_size + 3,
            textColor=colors.HexColor("#475569"),
            alignment=align_name,
            spaceAfter=8,
        )

        section_heading_style = ParagraphStyle(
            "SectionHeading",
            fontName=font_bold,
            fontSize=heading_size,
            leading=heading_size + 3,
            textColor=heading_color,
            spaceBefore=8,
            spaceAfter=3,
            keepWithNext=True,
        )

        subheading_style = ParagraphStyle(
            "SubHeading",
            fontName=font_bold,
            fontSize=body_size + 0.5,
            leading=body_size + 4,
            textColor=colors.HexColor("#1E293B"),
            spaceBefore=4,
            spaceAfter=2,
            keepWithNext=True,
        )

        date_sub_style = ParagraphStyle(
            "DateSub",
            fontName=font_name,
            fontSize=body_size - 0.5,
            leading=body_size + 2,
            textColor=colors.HexColor("#64748B"),
            spaceAfter=3,
        )

        body_style = ParagraphStyle(
            "Body",
            fontName=font_name,
            fontSize=body_size,
            leading=body_size + 4,
            textColor=colors.HexColor("#334155"),
            spaceAfter=3,
        )

        bullet_style = ParagraphStyle(
            "BulletPoint",
            fontName=font_name,
            fontSize=body_size,
            leading=body_size + 3.5,
            textColor=colors.HexColor("#334155"),
            leftIndent=14,
            firstLineIndent=-10,
            spaceAfter=2,
        )

        story = []

        # 1. CANDIDATE HEADER (In document body, ATS-friendly)
        name = resume.candidate.name or "Candidate Name"
        story.append(Paragraph(name, name_style))

        contact_parts = []
        if resume.candidate.email:
            contact_parts.append(resume.candidate.email)
        if resume.candidate.phone:
            contact_parts.append(resume.candidate.phone)
        if resume.candidate.location:
            contact_parts.append(resume.candidate.location)
        if resume.candidate.linkedin:
            contact_parts.append(resume.candidate.linkedin.replace("https://www.", "").replace("https://", ""))
        if resume.candidate.github:
            contact_parts.append(resume.candidate.github.replace("https://www.", "").replace("https://", ""))
        if resume.candidate.portfolio:
            contact_parts.append(resume.candidate.portfolio.replace("https://www.", "").replace("https://", ""))

        if contact_parts:
            story.append(Paragraph(" &bull; ".join(contact_parts), contact_style))

        story.append(HRFlowable(width="100%", thickness=1, color=line_color, spaceBefore=2, spaceAfter=6))

        # 2. PROFESSIONAL SUMMARY
        if resume.summary:
            story.append(Paragraph("PROFESSIONAL SUMMARY", section_heading_style))
            story.append(Paragraph(resume.summary, body_style))
            story.append(Spacer(1, 4))

        # 3. TECHNICAL SKILLS
        skills_groups = []
        if resume.skills.programming:
            skills_groups.append(f"<b>Languages:</b> {', '.join(resume.skills.programming)}")
        if resume.skills.frontend:
            skills_groups.append(f"<b>Frontend:</b> {', '.join(resume.skills.frontend)}")
        if resume.skills.backend:
            skills_groups.append(f"<b>Backend & Systems:</b> {', '.join(resume.skills.backend)}")
        if resume.skills.database:
            skills_groups.append(f"<b>Databases & Storage:</b> {', '.join(resume.skills.database)}")
        if resume.skills.cloud:
            skills_groups.append(f"<b>Cloud & DevOps:</b> {', '.join(resume.skills.cloud)}")
        if resume.skills.tools:
            skills_groups.append(f"<b>Tools & Architecture:</b> {', '.join(resume.skills.tools)}")

        if skills_groups:
            story.append(Paragraph("TECHNICAL SKILLS", section_heading_style))
            for group in skills_groups:
                story.append(Paragraph(group, body_style))
            story.append(Spacer(1, 4))

        # 4. WORK EXPERIENCE
        if resume.experience:
            story.append(Paragraph("WORK EXPERIENCE", section_heading_style))
            for exp in resume.experience:
                title_company = f"<b>{exp.title or 'Position'}</b> | {exp.company or 'Company'}"
                if exp.location:
                    title_company += f", {exp.location}"
                story.append(Paragraph(title_company, subheading_style))

                dates = ""
                if exp.start_date:
                    dates = f"{exp.start_date} – {exp.end_date or ('Present' if exp.is_current else '')}"
                if dates:
                    story.append(Paragraph(dates, date_sub_style))

                if exp.description:
                    story.append(Paragraph(exp.description, body_style))

                for bullet in exp.bullets:
                    clean_b = bullet.strip().lstrip("•-*▪● ").rstrip()
                    story.append(Paragraph(f"&bull; {clean_b}", bullet_style))

                story.append(Spacer(1, 4))

        # 5. EDUCATION
        if resume.education:
            story.append(Paragraph("EDUCATION", section_heading_style))
            for edu in resume.education:
                deg_field = f"<b>{edu.degree or 'Degree'}</b>"
                if edu.field_of_study:
                    deg_field += f" in {edu.field_of_study}"
                if edu.institution:
                    deg_field += f" &bull; {edu.institution}"
                story.append(Paragraph(deg_field, body_style))

                dates = ""
                if edu.start_date or edu.end_date:
                    dates = f"{edu.start_date or ''} – {edu.end_date or ''}".strip(" –")
                if edu.gpa:
                    dates += f" (GPA: {edu.gpa})"
                if dates:
                    story.append(Paragraph(dates, date_sub_style))

            story.append(Spacer(1, 4))

        # 6. PROJECTS
        if resume.projects:
            story.append(Paragraph("PROJECTS", section_heading_style))
            for proj in resume.projects:
                proj_title = f"<b>{proj.name}</b>"
                if proj.technologies:
                    proj_title += f" ({', '.join(proj.technologies)})"
                story.append(Paragraph(proj_title, subheading_style))

                if proj.description:
                    story.append(Paragraph(proj.description, body_style))

                for highlight in proj.highlights:
                    clean_h = highlight.strip().lstrip("•-*▪● ").rstrip()
                    story.append(Paragraph(f"&bull; {clean_h}", bullet_style))

                story.append(Spacer(1, 3))

        # 7. CERTIFICATIONS & ACHIEVEMENTS
        if resume.certifications:
            story.append(Paragraph("CERTIFICATIONS", section_heading_style))
            for cert in resume.certifications:
                story.append(Paragraph(f"&bull; {cert}", bullet_style))
            story.append(Spacer(1, 4))

        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes

    def generate_high_res_image(
        self,
        resume: ParsedResume,
        template: str = "modern",
        scale: float = 2.0,
        dpi: int = 300,
        image_format: str = "PNG",
    ) -> bytes:
        """
        Export as a high-resolution image (at least 2x / 300 DPI) so text stays sharp.
        Renders the ATS-safe PDF pages using PyMuPDF at high DPI and stitches vertically.
        """
        # Step 1: Render vector PDF first
        pdf_bytes = self.generate_pdf(resume, template=template)

        # Step 2: Open with PyMuPDF
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        page_images = []

        matrix = fitz.Matrix(scale, scale)
        for page in doc:
            pix = page.get_pixmap(matrix=matrix, alpha=False, dpi=dpi)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            page_images.append(img)
        doc.close()

        if not page_images:
            # Fallback blank image
            blank = Image.new("RGB", (1700, 2200), (255, 255, 255))
            buf = io.BytesIO()
            blank.save(buf, format="PNG")
            return buf.getvalue()

        # Stitch pages vertically with subtle separator
        total_width = max(img.width for img in page_images)
        total_height = sum(img.height for img in page_images) + (len(page_images) - 1) * 20

        combined = Image.new("RGB", (total_width, total_height), (245, 247, 250))
        y_offset = 0
        for img in page_images:
            x_offset = (total_width - img.width) // 2
            combined.paste(img, (x_offset, y_offset))
            y_offset += img.height + 20

        out_buf = io.BytesIO()
        combined.save(out_buf, format=image_format.upper(), quality=95)
        return out_buf.getvalue()

    def generate_docx(
        self,
        resume: ParsedResume,
        template: str = "modern",
    ) -> bytes:
        """
        Generate ATS-safe Microsoft Word (.docx) document.
        Uses clean single-column structure and standard Word paragraph styles.
        """
        doc = Document()

        # 0.7 inch margins
        for section in doc.sections:
            section.top_margin = Inches(0.65)
            section.bottom_margin = Inches(0.65)
            section.left_margin = Inches(0.65)
            section.right_margin = Inches(0.65)

        # Name
        name_p = doc.add_paragraph()
        if template == "classic":
            name_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        name_run = name_p.add_run(resume.candidate.name or "Candidate Name")
        name_run.font.name = "Arial"
        name_run.font.size = Pt(20)
        name_run.font.bold = True
        name_run.font.color.rgb = RGBColor(15, 23, 42)

        # Contact line
        contact_parts = []
        if resume.candidate.email:
            contact_parts.append(resume.candidate.email)
        if resume.candidate.phone:
            contact_parts.append(resume.candidate.phone)
        if resume.candidate.location:
            contact_parts.append(resume.candidate.location)
        if resume.candidate.linkedin:
            contact_parts.append(resume.candidate.linkedin.replace("https://www.", "").replace("https://", ""))
        if resume.candidate.github:
            contact_parts.append(resume.candidate.github.replace("https://www.", "").replace("https://", ""))

        if contact_parts:
            c_p = doc.add_paragraph()
            if template == "classic":
                c_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            c_run = c_p.add_run(" | ".join(contact_parts))
            c_run.font.size = Pt(9.5)
            c_run.font.color.rgb = RGBColor(71, 85, 105)

        def add_heading(title: str):
            h = doc.add_paragraph()
            h.paragraph_format.space_before = Pt(8)
            h.paragraph_format.space_after = Pt(2)
            run = h.add_run(title)
            run.font.name = "Arial"
            run.font.size = Pt(11.5)
            run.font.bold = True
            run.font.color.rgb = RGBColor(30, 58, 138)

        # Summary
        if resume.summary:
            add_heading("PROFESSIONAL SUMMARY")
            sp = doc.add_paragraph(resume.summary)
            sp.paragraph_format.space_after = Pt(4)

        # Technical Skills
        skills_groups = []
        if resume.skills.programming:
            skills_groups.append(("Languages", ", ".join(resume.skills.programming)))
        if resume.skills.frontend:
            skills_groups.append(("Frontend", ", ".join(resume.skills.frontend)))
        if resume.skills.backend:
            skills_groups.append(("Backend & Systems", ", ".join(resume.skills.backend)))
        if resume.skills.database:
            skills_groups.append(("Databases", ", ".join(resume.skills.database)))
        if resume.skills.cloud:
            skills_groups.append(("Cloud & DevOps", ", ".join(resume.skills.cloud)))

        if skills_groups:
            add_heading("TECHNICAL SKILLS")
            for cat, val in skills_groups:
                sk_p = doc.add_paragraph()
                r1 = sk_p.add_run(f"{cat}: ")
                r1.bold = True
                sk_p.add_run(val)
                sk_p.paragraph_format.space_after = Pt(2)

        # Work Experience
        if resume.experience:
            add_heading("WORK EXPERIENCE")
            for exp in resume.experience:
                ep = doc.add_paragraph()
                ep.paragraph_format.space_before = Pt(4)
                ep.paragraph_format.space_after = Pt(1)
                r_title = ep.add_run(f"{exp.title or 'Position'} | {exp.company or 'Company'}")
                r_title.bold = True

                dates = f"{exp.start_date or ''} - {exp.end_date or ('Present' if exp.is_current else '')}".strip(" -")
                if dates:
                    dp = doc.add_paragraph(dates)
                    dp.paragraph_format.space_after = Pt(2)

                for b in exp.bullets:
                    clean_b = b.strip().lstrip("•-*▪● ").rstrip()
                    bp = doc.add_paragraph(clean_b, style="List Bullet")
                    bp.paragraph_format.space_after = Pt(2)

        # Education
        if resume.education:
            add_heading("EDUCATION")
            for edu in resume.education:
                ed_p = doc.add_paragraph()
                deg_r = ed_p.add_run(f"{edu.degree or 'Degree'} {f'in {edu.field_of_study}' if edu.field_of_study else ''} - {edu.institution or ''}")
                deg_r.bold = True

        # Projects
        if resume.projects:
            add_heading("PROJECTS")
            for proj in resume.projects:
                pp = doc.add_paragraph()
                p_r = pp.add_run(proj.name)
                p_r.bold = True
                if proj.technologies:
                    pp.add_run(f" ({', '.join(proj.technologies)})")
                for h in proj.highlights:
                    doc.add_paragraph(h.strip().lstrip("•-*▪● ").rstrip(), style="List Bullet")

        out_stream = io.BytesIO()
        doc.save(out_stream)
        return out_stream.getvalue()


# Global singleton
resume_generator = ResumeGeneratorService()
