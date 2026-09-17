from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


OUTPUT_PATH = "doc/fictitious_health_insurance_policies.pdf"
COMPANY_DOCUMENTS = [
    (
        "Cedarline Health Assurance",
        "Practical coverage for growing families and local communities.",
        [
            ("Member promise", "Explain benefits in plain language and provide a named service contact for complex cases."),
            ("Coverage policy", "Preventive screenings are covered in full when delivered by an in-network provider; specialist care may require a referral."),
            ("Access standard", "Routine primary-care appointments should be available within 10 business days in participating service areas."),
            ("Service commitment", "Written complaints receive acknowledgment within two business days and a decision within 30 calendar days."),
        ],
    ),
    (
        "Harborwell Mutual",
        "Coordinated care with a steady hand during major health events.",
        [
            ("Member promise", "A care coordinator is available for members managing multiple specialists, prescriptions, or hospital transitions."),
            ("Coverage policy", "Discharge planning, medication reconciliation, and post-discharge follow-up are included when arranged through the care team."),
            ("Access standard", "Urgent nurse-line calls are answered 24 hours a day, seven days a week; emergencies should be directed to 911."),
            ("Service commitment", "Case-management outreach begins within one business day after an eligible hospital notification."),
        ],
    ),
    (
        "Meridian Bloom Health",
        "Whole-person care that treats mental and physical health as connected.",
        [
            ("Member promise", "Behavioral-health support is presented as a standard part of care, without stigma or separate navigation burdens."),
            ("Coverage policy", "Covered outpatient therapy, psychiatry, and substance-use services follow the member's plan cost share and network rules."),
            ("Access standard", "The digital behavioral-health directory displays current availability, language capabilities, and telehealth options when known."),
            ("Service commitment", "Urgent behavioral-health requests are triaged the same day; crisis situations are directed to local emergency resources."),
        ],
    ),
    (
        "Lumen Prairie Insurance",
        "Clear decisions, visible criteria, and useful digital tools.",
        [
            ("Member promise", "Members can view claim status, prior-authorization status, estimated cost, and appeal deadlines in one secure portal."),
            ("Coverage policy", "A prior authorization request includes the clinical criteria used, the documents received, and the expected review timeframe."),
            ("Access standard", "Standard authorization decisions are targeted within five business days after all required information is received."),
            ("Service commitment", "A denial notice states the specific reason, relevant plan provision, reconsideration option, and independent review rights where applicable."),
        ],
    ),
    (
        "Solstice Community Health",
        "Affordable access with neighborhood partnerships and accountable stewardship.",
        [
            ("Member promise", "Care navigation considers transportation, language, disability access, and other practical barriers to receiving care."),
            ("Coverage policy", "Community health workers and approved social-support referrals may be included as care-coordination benefits when authorized by the plan."),
            ("Access standard", "Members may request interpreter services at no additional charge for covered care and important plan communications."),
            ("Service commitment", "Provider-directory corrections are investigated within 15 business days, with confirmed updates posted promptly."),
        ],
    ),
]


def build_styles():
    # Keep typography and spacing in one place so every policy section stays consistent.
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="CoverTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=25,
            leading=30,
            textColor=colors.HexColor("#12304A"),
            alignment=TA_CENTER,
            spaceAfter=12,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Subtitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=11,
            leading=16,
            textColor=colors.HexColor("#496273"),
            alignment=TA_CENTER,
            spaceAfter=18,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SectionTitle",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=20,
            textColor=colors.HexColor("#12304A"),
            spaceBefore=2,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CompanyName",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=15,
            textColor=colors.HexColor("#007C83"),
            spaceBefore=5,
            spaceAfter=4,
        )
    )
    styles.add(
        ParagraphStyle(
            name="BodySmall",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=8.8,
            leading=12,
            textColor=colors.HexColor("#243746"),
            spaceAfter=5,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Label",
            parent=styles["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=8.8,
            leading=12,
            textColor=colors.HexColor("#12304A"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="Footer",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=7.5,
            textColor=colors.HexColor("#6D7D87"),
            alignment=TA_CENTER,
        )
    )
    return styles


def header_footer(canvas, document):
    # Add a consistent portfolio header and page number to each generated page.
    canvas.saveState()
    width, height = letter
    canvas.setStrokeColor(colors.HexColor("#D6E3E5"))
    canvas.setLineWidth(0.6)
    canvas.line(0.7 * inch, height - 0.53 * inch, width - 0.7 * inch, height - 0.53 * inch)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.setFillColor(colors.HexColor("#007C83"))
    canvas.drawString(0.7 * inch, height - 0.38 * inch, "NORTHSTAR HEALTH POLICY PORTFOLIO")
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(colors.HexColor("#6D7D87"))
    canvas.drawRightString(width - 0.7 * inch, 0.42 * inch, f"Illustrative policy brief  |  Page {document.page}")
    canvas.restoreState()


def paragraph(text, styles, style="BodySmall"):
    return Paragraph(text, styles[style])


def company_block(name, tagline, policy_lines, styles):
    # Render each insurer as a compact bordered policy summary for easy comparison.
    rows = [[paragraph(name, styles, "CompanyName")]]
    rows.append([paragraph(f"<i>{tagline}</i>", styles)])
    for label, text in policy_lines:
        rows.append([paragraph(f"<b>{label}:</b> {text}", styles)])
    table = Table(rows, colWidths=[6.9 * inch], hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EAF4F3")),
                ("BOX", (0, 0), (-1, -1), 0.7, colors.HexColor("#B9D8D7")),
                ("INNERPADDING", (0, 0), (-1, -1), 7),
                ("LEFTPADDING", (0, 0), (-1, -1), 9),
                ("RIGHTPADDING", (0, 0), (-1, -1), 9),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return table


def build_company_documents():
    # Create one independently readable PDF for each fictional insurance company.
    styles = build_styles()
    for company_name, tagline, policy_lines in COMPANY_DOCUMENTS:
        output_path = f"doc/{company_name}.pdf"
        document = BaseDocTemplate(
            output_path,
            pagesize=letter,
            leftMargin=0.8 * inch,
            rightMargin=0.8 * inch,
            topMargin=0.72 * inch,
            bottomMargin=0.62 * inch,
            title=f"{company_name} Policy Document",
            author=company_name,
        )
        frame = Frame(document.leftMargin, document.bottomMargin, document.width, document.height, id="normal")
        document.addPageTemplates([PageTemplate(id="policy", frames=frame, onPage=header_footer)])
        story = [
            Spacer(1, 0.35 * inch),
            paragraph(company_name, styles, "CoverTitle"),
            paragraph("Health Insurance Policy Document", styles, "Subtitle"),
            company_block(company_name, tagline, policy_lines, styles),
            Spacer(1, 0.22 * inch),
            paragraph("Policy governance", styles, "SectionTitle"),
            paragraph(
                "Member information is protected and used only for permitted care, payment, operations, and legal purposes. "
                "Members may request accessibility accommodations, a supervisor review, or an appeal of an adverse benefit decision. "
                "Coverage remains subject to the applicable plan certificate, exclusions, authorization rules, and governing law.",
                styles,
            ),
            Spacer(1, 0.18 * inch),
            paragraph("Document control", styles, "SectionTitle"),
            paragraph(
                "Version: 1.0 | Effective date: September 17, 2026 | Review cycle: Annual",
                styles,
            ),
            Spacer(1, 0.14 * inch),
            paragraph(
                "Fictional content notice: This company and policy are fictional and are provided for demonstration purposes. "
                "This document is not an insurance contract, benefit determination, legal advice, or a substitute for official plan materials.",
                styles,
            ),
        ]
        document.build(story)


def build_pdf():
    # Build the PDF with explicit page breaks to guarantee the requested three-page layout.
    styles = build_styles()
    document = BaseDocTemplate(
        OUTPUT_PATH,
        pagesize=letter,
        leftMargin=0.8 * inch,
        rightMargin=0.8 * inch,
        topMargin=0.72 * inch,
        bottomMargin=0.62 * inch,
        title="Fictitious Health Insurance Company Policies",
        author="Northstar Health Policy Portfolio",
    )
    frame = Frame(document.leftMargin, document.bottomMargin, document.width, document.height, id="normal")
    document.addPageTemplates([PageTemplate(id="policy", frames=frame, onPage=header_footer)])

    story = [
        Spacer(1, 0.34 * inch),
        paragraph("Fictitious Health Insurance\nCompany Policy Portfolio", styles, "CoverTitle"),
        paragraph("A three-page reference brief for five fictional insurers", styles, "Subtitle"),
        paragraph("Portfolio purpose", styles, "SectionTitle"),
        paragraph(
            "This reference document presents fictional operating policies for five made-up health insurance companies. "
            "Each profile describes a member promise, coverage approach, access standard, and service commitment. "
            "The profiles are designed for demonstrations, document retrieval exercises, and policy-comparison prototypes.",
            styles,
        ),
        Spacer(1, 0.08 * inch),
        paragraph("Shared policy principles", styles, "SectionTitle"),
        paragraph(
            "All five companies commit to plain-language member communications, protection of personal health information, "
            "reasonable accessibility accommodations, and an appeal pathway for adverse benefit decisions. Coverage is "
            "subject to the applicable plan certificate, exclusions, authorization rules, and governing law.",
            styles,
        ),
        Spacer(1, 0.1 * inch),
        company_block(
            "1. Cedarline Health Assurance",
            "Practical coverage for growing families and local communities.",
            [
                ("Member promise", "Explain benefits in plain language and provide a named service contact for complex cases."),
                ("Coverage policy", "Preventive screenings are covered in full when delivered by an in-network provider; specialist care may require a referral."),
                ("Access standard", "Routine primary-care appointments should be available within 10 business days in participating service areas."),
                ("Service commitment", "Written complaints receive acknowledgment within two business days and a decision within 30 calendar days."),
            ],
            styles,
        ),
        Spacer(1, 0.12 * inch),
        company_block(
            "2. Harborwell Mutual",
            "Coordinated care with a steady hand during major health events.",
            [
                ("Member promise", "A care coordinator is available for members managing multiple specialists, prescriptions, or hospital transitions."),
                ("Coverage policy", "Discharge planning, medication reconciliation, and post-discharge follow-up are included when arranged through the care team."),
                ("Access standard", "Urgent nurse-line calls are answered 24 hours a day, seven days a week; emergencies should be directed to 911."),
                ("Service commitment", "Case-management outreach begins within one business day after an eligible hospital notification."),
            ],
            styles,
        ),
        PageBreak(),
        paragraph("Company Policies", styles, "SectionTitle"),
        paragraph("Profiles three and four focus on digital access, behavioral health, and transparent utilization review.", styles),
        Spacer(1, 0.08 * inch),
        company_block(
            "3. Meridian Bloom Health",
            "Whole-person care that treats mental and physical health as connected.",
            [
                ("Member promise", "Behavioral-health support is presented as a standard part of care, without stigma or separate navigation burdens."),
                ("Coverage policy", "Covered outpatient therapy, psychiatry, and substance-use services follow the member's plan cost share and network rules."),
                ("Access standard", "The digital behavioral-health directory displays current availability, language capabilities, and telehealth options when known."),
                ("Service commitment", "Urgent behavioral-health requests are triaged the same day; crisis situations are directed to local emergency resources."),
            ],
            styles,
        ),
        Spacer(1, 0.14 * inch),
        company_block(
            "4. Lumen Prairie Insurance",
            "Clear decisions, visible criteria, and useful digital tools.",
            [
                ("Member promise", "Members can view claim status, prior-authorization status, estimated cost, and appeal deadlines in one secure portal."),
                ("Coverage policy", "A prior authorization request includes the clinical criteria used, the documents received, and the expected review timeframe."),
                ("Access standard", "Standard authorization decisions are targeted within five business days after all required information is received."),
                ("Service commitment", "A denial notice states the specific reason, relevant plan provision, reconsideration option, and independent review rights where applicable."),
            ],
            styles,
        ),
        Spacer(1, 0.25 * inch),
        paragraph("Utilization review safeguard", styles, "SectionTitle"),
        paragraph(
            "Clinical review is performed by qualified personnel using current evidence and the member's documented circumstances. "
            "Administrative convenience alone is not a sufficient reason to deny a medically necessary covered service. "
            "Members may submit additional records or request an authorized representative during an appeal.",
            styles,
        ),
        PageBreak(),
        paragraph("Company Policy and Governance", styles, "SectionTitle"),
        paragraph("The fifth profile completes the portfolio and establishes controls that apply across the fictional group.", styles),
        Spacer(1, 0.08 * inch),
        company_block(
            "5. Solstice Community Health",
            "Affordable access with neighborhood partnerships and accountable stewardship.",
            [
                ("Member promise", "Care navigation considers transportation, language, disability access, and other practical barriers to receiving care."),
                ("Coverage policy", "Community health workers and approved social-support referrals may be included as care-coordination benefits when authorized by the plan."),
                ("Access standard", "Members may request interpreter services at no additional charge for covered care and important plan communications."),
                ("Service commitment", "Provider-directory corrections are investigated within 15 business days, with confirmed updates posted promptly."),
            ],
            styles,
        ),
        Spacer(1, 0.22 * inch),
        paragraph("Portfolio-wide governance rules", styles, "SectionTitle"),
        paragraph(
            "<b>Privacy:</b> Member information is collected, used, and disclosed only for permitted operational, treatment, payment, "
            "and legal purposes, with access limited by role. &nbsp; "
            "<b>Equity:</b> Policies are administered without discrimination and reasonable accommodations are considered through the established service channel. &nbsp; "
            "<b>Records:</b> Claim, authorization, and complaint records are retained according to the applicable retention schedule. &nbsp; "
            "<b>Escalation:</b> A member may request a supervisor, file a formal grievance, or pursue an external review when available under the plan.",
            styles,
        ),
        Spacer(1, 0.16 * inch),
        paragraph("Document control", styles, "SectionTitle"),
        paragraph(
            "Document owner: Northstar Health Policy Portfolio | Version: 1.0 | Effective date: September 17, 2026 | Review cycle: Annual",
            styles,
        ),
        Spacer(1, 0.15 * inch),
        paragraph(
            "Fictional content notice: Cedarline Health Assurance, Harborwell Mutual, Meridian Bloom Health, Lumen Prairie Insurance, "
            "Solstice Community Health, and Northstar Health Policy Portfolio are fictional entities created for demonstration purposes. "
            "This document is not an insurance contract, benefit determination, legal advice, or a substitute for official plan materials.",
            styles,
        ),
    ]
    document.build(story)


if __name__ == "__main__":
    build_pdf()
    build_company_documents()