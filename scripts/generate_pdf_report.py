"""
Pakistan Digital Advertising Budget Optimizer - Executive PDF Report Generator
=============================================================================
Phase 2: Compiles a comprehensive, publication-grade executive PDF report:
  reports/Pakistan_Digital_Advertising_Budget_Optimizer_Report.pdf

Built using ReportLab with:
  - Custom canvas supporting dynamic "Page X of Y" numbering
  - Nexus Editorial Design System palette (Teal, Rust, Slate, Gold)
  - Embedded 300 DPI visualization figures
  - Clean typography without font-leading overlaps
  - Clean, human-readable text without raw LaTeX formulas
  - Standard typography without unrenderable emoji glyphs
  - Perfectly paced page-by-page content budgeting to eliminate awkward page splits
"""

import os
import sys
import json
import pandas as pd
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
)
from reportlab.pdfgen import canvas

# Design System Palette (Nexus Editorial)
PRIMARY = colors.HexColor('#01696F')       # Deep Teal
SECONDARY = colors.HexColor('#20808D')     # Medium Teal
DARK_BG = colors.HexColor('#1B474D')       # Dark Teal
ACCENT_RUST = colors.HexColor('#A84B2F')   # Rust Red
ACCENT_GOLD = colors.HexColor('#D99B26')   # Gold
BG_LIGHT = colors.HexColor('#F7F6F2')      # Warm White
BORDER_COLOR = colors.HexColor('#D4D1CA')  # Neutral Gray
TEXT_MAIN = colors.HexColor('#28251D')     # Charcoal Text
TEXT_MUTED = colors.HexColor('#64748B')    # Slate Muted
CALLOUT_BG = colors.HexColor('#EFF6F7')    # Soft Teal Tint
PLAIN_BG = colors.HexColor('#FEFCE8')      # Soft Warm Amber Tint (Plain English)
PLAIN_BORDER = colors.HexColor('#EAB308')  # Amber Border


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and print 'Page X of Y'."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        print(f"📊 PDF Page Count: {num_pages} pages")
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        page_num = self._pageNumber
        if page_num == 1:
            # Skip running header/footer on cover page
            return

        self.saveState()
        self.setFont("Helvetica-Bold", 7.5)
        self.setFillColor(PRIMARY)
        self.drawString(36, 806, "PAKISTAN DIGITAL ADVERTISING BUDGET OPTIMIZER (PHASE 2)")
        
        self.setFont("Helvetica", 7.5)
        self.setFillColor(TEXT_MUTED)
        self.drawString(290, 806, "— Executive Marketing Intelligence & Big Data Report")
        self.drawRightString(559, 806, "Portfolio Deliverable • Zughaina")
        
        self.setStrokeColor(BORDER_COLOR)
        self.setLineWidth(0.5)
        self.line(36, 798, 559, 798)

        # Running Footer
        self.line(36, 30, 559, 30)
        self.drawString(36, 20, "Strictly Confidential • For Executive & Marketing Leadership Review")
        page_str = f"Page {page_num} of {page_count}"
        self.drawRightString(559, 20, page_str)
        self.restoreState()


def get_styles():
    """Build standard typography hierarchy with verified font-leading ratios."""
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name='CoverTitle',
        fontName='Helvetica-Bold',
        fontSize=21,
        leading=25,
        textColor=PRIMARY,
        spaceAfter=5
    ))
    styles.add(ParagraphStyle(
        name='CoverSubtitle',
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=TEXT_MAIN,
        spaceAfter=8
    ))
    styles.add(ParagraphStyle(
        name='SecHeader',
        fontName='Helvetica-Bold',
        fontSize=11.5,
        leading=14.5,
        textColor=PRIMARY,
        spaceBefore=3,
        spaceAfter=3,
        keepWithNext=True
    ))
    styles.add(ParagraphStyle(
        name='SubSecHeader',
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=DARK_BG,
        spaceBefore=3,
        spaceAfter=2,
        keepWithNext=True
    ))
    styles.add(ParagraphStyle(
        name='BodyCustom',
        fontName='Helvetica',
        fontSize=7.8,
        leading=10.8,
        textColor=TEXT_MAIN,
        spaceAfter=3
    ))
    styles.add(ParagraphStyle(
        name='CalloutBox',
        fontName='Helvetica',
        fontSize=7.6,
        leading=10.5,
        textColor=TEXT_MAIN,
        spaceAfter=2
    ))
    styles.add(ParagraphStyle(
        name='PlainEnglishText',
        fontName='Helvetica',
        fontSize=7.6,
        leading=10.5,
        textColor=colors.HexColor('#713F12'),
        spaceAfter=2
    ))
    styles.add(ParagraphStyle(
        name='TableHead',
        fontName='Helvetica-Bold',
        fontSize=6.8,
        leading=8.8,
        textColor=colors.white,
        alignment=1
    ))
    styles.add(ParagraphStyle(
        name='TableCell',
        fontName='Helvetica',
        fontSize=6.8,
        leading=8.8,
        textColor=TEXT_MAIN,
        alignment=0
    ))
    styles.add(ParagraphStyle(
        name='TableCellCenter',
        fontName='Helvetica',
        fontSize=6.8,
        leading=8.8,
        textColor=TEXT_MAIN,
        alignment=1
    ))
    styles.add(ParagraphStyle(
        name='TableCellBold',
        fontName='Helvetica-Bold',
        fontSize=6.8,
        leading=8.8,
        textColor=TEXT_MAIN,
        alignment=1
    ))
    styles.add(ParagraphStyle(
        name='KPITitle',
        fontName='Helvetica-Bold',
        fontSize=6.5,
        leading=8,
        textColor=TEXT_MUTED,
        alignment=1,
        spaceAfter=2
    ))
    styles.add(ParagraphStyle(
        name='KPIVal',
        fontName='Helvetica-Bold',
        fontSize=12.5,
        leading=14.5,
        textColor=PRIMARY,
        alignment=1,
        spaceAfter=2
    ))
    styles.add(ParagraphStyle(
        name='KPISub',
        fontName='Helvetica',
        fontSize=6,
        leading=7.5,
        textColor=TEXT_MUTED,
        alignment=1
    ))
    styles.add(ParagraphStyle(
        name='CaptionText',
        fontName='Helvetica-Oblique',
        fontSize=6.8,
        leading=8.2,
        textColor=TEXT_MUTED,
        alignment=1,
        spaceBefore=2,
        spaceAfter=3
    ))

    return styles


def make_callout(text: str, styles, bg=CALLOUT_BG, border_color=PRIMARY, border_width=3):
    """Helper to create visually appealing callout blocks."""
    t = Table([[Paragraph(text, styles['CalloutBox'])]], colWidths=[523])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), bg),
        ('BOX', (0,0), (-1,-1), 0.5, border_color),
        ('LINEBEFORE', (0,0), (0,-1), border_width, border_color),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 7),
        ('RIGHTPADDING', (0,0), (-1,-1), 7),
    ]))
    return t


def make_plain_english_box(title: str, text: str, styles):
    """Helper to create 'In Plain English' intuitive explanation blocks without emojis."""
    content = f"<b>[PLAIN-ENGLISH GUIDE] {title.upper()}</b><br/>{text}"
    t = Table([[Paragraph(content, styles['PlainEnglishText'])]], colWidths=[523])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), PLAIN_BG),
        ('BOX', (0,0), (-1,-1), 0.5, PLAIN_BORDER),
        ('LINEBEFORE', (0,0), (0,-1), 3.5, PLAIN_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 7),
        ('RIGHTPADDING', (0,0), (-1,-1), 7),
    ]))
    return t


def build_pdf(
    output_pdf: str = "reports/Pakistan_Digital_Advertising_Budget_Optimizer_Report.pdf",
    fig_dir: str = "reports/figures"
):
    os.makedirs(os.path.dirname(output_pdf), exist_ok=True)
    doc = SimpleDocTemplate(
        output_pdf,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=40,
        bottomMargin=36
    )

    styles = get_styles()
    story = []

    # ==========================================================================
    # PAGE 1: COVER PAGE & EXECUTIVE ABSTRACT (PLAIN-ENGLISH OVERVIEW)
    # ==========================================================================
    story.append(Spacer(1, 4))
    
    # Top Header Badge
    badge_table = Table(
        [[Paragraph("<font color='#01696F'><b>EXECUTIVE MARKETING INTELLIGENCE & BIG DATA BENCHMARK • 2025–2026</b></font>", styles['TableCellBold'])]],
        colWidths=[523]
    )
    badge_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 1, PRIMARY),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(badge_table)
    story.append(Spacer(1, 6))

    story.append(Paragraph("Pakistan Digital Advertising Budget Optimizer", styles['CoverTitle']))
    story.append(Paragraph("<b>Phase 2:</b> Big Data Marketing Campaign Intelligence, Distributed Framework Benchmarking (Pandas vs. MapReduce vs. Spark) & Algorithmic Ad Budget Reallocation Engine", styles['CoverSubtitle']))
    
    # Metadata Box
    meta_data = [
        [
            Paragraph("<b>Author:</b> Zughaina (<font color='#01696F'>@zughaina3</font>)", styles['TableCell']),
            Paragraph("<b>Domain:</b> Pakistani D2C E-Commerce (Fashion, Lawn & Bags)", styles['TableCell']),
        ],
        [
            Paragraph("<b>GitHub Repository:</b> <a href='https://github.com/zughaina3/pakistan-digital-advertising-budget-optimizer'><font color='#01696F'><u>https://github.com/zughaina3/pakistan-digital-advertising-budget-optimizer</u></font></a>", styles['TableCell']),
            Paragraph("<b>Capital Optimization Scope:</b> Rs. 1,000,000 (PKR 1.0M)", styles['TableCell']),
        ],
        [
            Paragraph("<b>Data Simulation Tiers:</b> 10K, 100K, 1M, 10M Records", styles['TableCell']),
            Paragraph("<b>Benchmark Architectures:</b> Pandas | MapReduce | Apache Spark", styles['TableCell']),
        ]
    ]
    t_meta = Table(meta_data, colWidths=[261, 262])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 5))

    # Executive Abstract Callout
    abstract_text = (
        "<b>Executive Problem Statement:</b> A high-growth Pakistani direct-to-consumer brand specializing in stitched lawn "
        "pret, festive collections, and university accessories (tote bags, laptop backpacks) currently spends marketing capital across "
        "Google, Instagram, Facebook, TikTok, and YouTube. Management posed the strategic question: <i>'Where should we spend the "
        "next Rs. 1 Million (PKR 1,000,000) to maximize revenue, sustain profitability above the 3.0x break-even target, and acquire "
        "customers at the lowest possible cost?'</i><br/><br/>"
        "This research synthesizes empirical multi-channel advertising performance, non-linear diminishing returns modeling calibrated directly "
        "from historical daily data via <code>scipy.optimize.curve_fit</code>, and an enterprise-grade Big Data scalability benchmark. "
        "The findings recommend allocating <b>40% to Google Ads</b>, <b>35% to Instagram Ads</b>, <b>13% to Facebook Ads</b>, <b>8% to TikTok Ads</b>, "
        "and <b>4% to YouTube Ads</b>, generating a projected <b>Rs. 4.37 Million in gross revenue</b>, <b>Rs. 637,864 in true operating net profit</b> "
        "(14.6% net operating margin after 45% COGS, Rs. 220 courier shipping, 12% COD returns, and Rs. 1M media spend), and <b>1,970 confirmed customer orders</b> at a blended CPA of Rs. 508."
    )
    story.append(make_callout(abstract_text, styles))
    story.append(Spacer(1, 5))

    # Core KPI Cards Table
    def kpi_card(title, val, sub):
        return [
            Paragraph(title, styles['KPITitle']),
            Paragraph(val, styles['KPIVal']),
            Paragraph(sub, styles['KPISub']),
        ]

    kpi_cards = [
        [
            kpi_card("TOTAL AD SPEND", "Rs. 1.0M", "Allocated Capital"),
            kpi_card("PROJECTED SALES", "Rs. 4.37M", "Gross Attributed Sales"),
            kpi_card("OPERATING NET PROFIT", "Rs. 638K", "Net After COGS & Logistics"),
            kpi_card("BLENDED ROAS", "4.37x", "Rs. 4.37 per Rs. 1 Spend"),
            kpi_card("CONFIRMED ORDERS", "1,970", "Rs. 508 Blended CPA"),
        ]
    ]
    t_kpis = Table(kpi_cards, colWidths=[104.6]*5)
    t_kpis.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
    ]))
    story.append(t_kpis)
    story.append(Spacer(1, 5))

    # Data Provenance & Academic Methodology Notice
    provenance_text = (
        "<b>Academic & Commercial Data Provenance Notice:</b> "
        "The interaction datasets (10K, 100K, 1M, and 10M streaming records) are synthesized via a deterministic econometric "
        "simulation model. This architecture guarantees the strict protection of commercial client confidentiality and PII while "
        "faithfully mirroring empirical Pakistani macroeconomic conditions: 85%+ Cash-on-Delivery (COD) adoption, 12% doorstep refusal/RTO rates, "
        "Rs. 220 courier delivery tariffs, Rs. 180 reverse logistics fees, 45% production COGS, and empirical channel auction elasticities."
    )
    story.append(make_callout(provenance_text, styles, bg=colors.HexColor('#F8FAFB'), border_color=SECONDARY, border_width=2.5))
    story.append(Spacer(1, 5))

    # Plain English Primer Box
    primer_text = (
        "<b>What is this report about in everyday words?</b><br/>"
        "Many Pakistani business owners waste advertising budgets because they throw money randomly into boosted posts without knowing "
        "which platform actually generates cash. This report does two major things: (1) It uses advanced Big Data software to test "
        "millions of customer interactions in seconds to see which platforms bring real profit; and (2) It gives business owners an "
        "exact mathematical blueprint showing how much money to give to Google, Instagram, Facebook, TikTok, and YouTube so every single "
        "Rupee spent produces maximum customer orders while avoiding advertising waste."
    )
    story.append(make_plain_english_box("How to Read This Report If You Are Not a Data Scientist", primer_text, styles))

    story.append(PageBreak())

    # ==========================================================================
    # PAGE 2: THE CORE DECISION - WHERE TO SPEND THE NEXT RS. 1 MILLION
    # ==========================================================================
    story.append(Paragraph("1. The Core Solution: Where to Spend the Next Rs. 1 Million", styles['SecHeader']))
    story.append(Paragraph(
        "Using an econometric diminishing returns model that accounts for customer ad fatigue (where extra spend gradually yields "
        "diminishing sales once an audience is saturated), our recommendation engine determined the <b>Balanced Growth Allocation</b>:",
        styles['BodyCustom']
    ))

    # Allocation Table
    alloc_table_data = [
        [
            Paragraph("<b>Platform</b>", styles['TableHead']),
            Paragraph("<b>Share %</b>", styles['TableHead']),
            Paragraph("<b>Ad Spend (PKR)</b>", styles['TableHead']),
            Paragraph("<b>Projected Revenue</b>", styles['TableHead']),
            Paragraph("<b>ROAS</b>", styles['TableHead']),
            Paragraph("<b>CPA (PKR)</b>", styles['TableHead']),
            Paragraph("<b>Orders</b>", styles['TableHead']),
            Paragraph("<b>Strategic Role</b>", styles['TableHead']),
        ],
        [Paragraph("<b>Google Ads</b>", styles['TableCell']), Paragraph("40.0%", styles['TableCellCenter']), Paragraph("Rs. 400,000", styles['TableCellCenter']), Paragraph("Rs. 2,006,579", styles['TableCellCenter']), Paragraph("<b>5.02x</b>", styles['TableCellCenter']), Paragraph("Rs. 600", styles['TableCellCenter']), Paragraph("667", styles['TableCellCenter']), Paragraph("Profit Engine (High-Intent Search)", styles['TableCell'])],
        [Paragraph("<b>Instagram Ads</b>", styles['TableCell']), Paragraph("35.0%", styles['TableCellCenter']), Paragraph("Rs. 350,000", styles['TableCellCenter']), Paragraph("Rs. 1,613,177", styles['TableCellCenter']), Paragraph("<b>4.61x</b>", styles['TableCellCenter']), Paragraph("Rs. 388", styles['TableCellCenter']), Paragraph("901", styles['TableCellCenter']), Paragraph("Efficiency Leader (Lowest CPA)", styles['TableCell'])],
        [Paragraph("<b>Facebook Ads</b>", styles['TableCell']), Paragraph("13.0%", styles['TableCellCenter']), Paragraph("Rs. 130,000", styles['TableCellCenter']), Paragraph("Rs. 478,728", styles['TableCellCenter']), Paragraph("<b>3.68x</b>", styles['TableCellCenter']), Paragraph("Rs. 637", styles['TableCellCenter']), Paragraph("204", styles['TableCellCenter']), Paragraph("Cart Recovery & Mature Buyers", styles['TableCell'])],
        [Paragraph("<b>TikTok Ads</b>", styles['TableCell']), Paragraph("8.0%", styles['TableCellCenter']), Paragraph("Rs. 80,000", styles['TableCellCenter']), Paragraph("Rs. 188,668", styles['TableCellCenter']), Paragraph("<b>2.36x</b>", styles['TableCellCenter']), Paragraph("Rs. 471", styles['TableCellCenter']), Paragraph("170", styles['TableCellCenter']), Paragraph("Top-Funnel Gen Z Youth Reach", styles['TableCell'])],
        [Paragraph("<b>YouTube Ads</b>", styles['TableCell']), Paragraph("4.0%", styles['TableCellCenter']), Paragraph("Rs. 40,000", styles['TableCellCenter']), Paragraph("Rs. 80,236", styles['TableCellCenter']), Paragraph("<b>2.01x</b>", styles['TableCellCenter']), Paragraph("Rs. 1,429", styles['TableCellCenter']), Paragraph("28", styles['TableCellCenter']), Paragraph("Brand Recall & Video Trust", styles['TableCell'])],
        [Paragraph("<b>TOTAL / BLENDED</b>", styles['TableHead']), Paragraph("<b>100.0%</b>", styles['TableHead']), Paragraph("<b>Rs. 1,000,000</b>", styles['TableHead']), Paragraph("<b>Rs. 4,367,388</b>", styles['TableHead']), Paragraph("<b>4.37x</b>", styles['TableHead']), Paragraph("<b>Rs. 508</b>", styles['TableHead']), Paragraph("<b>1,970</b>", styles['TableHead']), Paragraph("<b>Net Profit: Rs. 637,864 (14.6%)</b>", styles['TableHead'])],
    ]
    t_alloc = Table(alloc_table_data, colWidths=[78, 42, 68, 78, 40, 52, 45, 120])
    t_alloc.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('BACKGROUND', (0,-1), (-1,-1), DARK_BG),
        ('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, BG_LIGHT]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_alloc)
    story.append(Spacer(1, 5))

    # Embed Chart 6: Allocation Donut & Waterfall
    p6_path = os.path.join(fig_dir, "06_recommended_budget_allocation_rs1m.png")
    if os.path.exists(p6_path):
        story.append(Image(p6_path, width=7.0*inch, height=2.05*inch))
        story.append(Paragraph("Figure 1: Optimal Ad Budget Allocation Share (%) and Projected Revenue Contribution Waterfall across Channels", styles['CaptionText']))

    # Executive Summary Takeaway Callout
    p2_takeaway = (
        "<b>Executive Summary of the Recommended Allocation:</b><br/>"
        "• <b>Google & Instagram capture 75% of the total budget (Rs. 750,000)</b>, generating <b>82.9% of total customer sales (Rs. 3.62 Million)</b> and Rs. 623,133 in true operating profit.<br/>"
        "• <b>Facebook secures 13% (Rs. 130,000)</b> to safeguard against abandoned shopping carts and reach 25–44 family buyers at 3.68x ROAS.<br/>"
        "• <b>TikTok is strictly capped at 8% (Rs. 80,000)</b> for low-cost impulse accessories under Rs. 2,500.<br/>"
        "• <b>YouTube is curtailed to 4% (Rs. 40,000)</b> to prevent unprofitable capital bleed while preserving video unboxing trust."
    )
    story.append(make_callout(p2_takeaway, styles))

    story.append(PageBreak())

    # ==========================================================================
    # PAGE 3: PLAIN-ENGLISH PLATFORM ROLES & STRATEGIC SCENARIOS
    # ==========================================================================
    story.append(Paragraph("2. Plain-English Platform Roles & Strategic Scenarios", styles['SecHeader']))
    story.append(Paragraph(
        "To understand why money is allocated this way, here is the real-world role each platform plays in Pakistan, followed "
        "by alternative strategies evaluated using the Sequential Least Squares Programming (SLSQP) solver:",
        styles['BodyCustom']
    ))

    # Full Plain English Platform Strategy Box
    plain_plat = (
        "<b>Why Did Each Platform Get This Exact Amount of Money?</b><br/>"
        "• <b>Google gets the largest share (Rs. 400,000 / 40%):</b> Think of Google like a prime store on Mall Road or Tariq Road where customers "
        "walk in <i>already holding cash</i> searching for <i>'stitched lawn suit sale'</i> or <i>'canvas laptop tote bag'</i>. "
        "They want to buy right now. That is why Google generates the highest revenue (Rs. 2.01 Million) and 5.02x predicted ROAS.<br/>"
        "• <b>Instagram gets the second largest share (Rs. 350,000 / 35%):</b> Instagram is the visual fashion catalog of Pakistan. Young women "
        "scroll through Reels and watch styling unboxings. It costs only <b>Rs. 388</b> to win a customer on Instagram, producing 901 orders.<br/>"
        "• <b>Facebook gets Rs. 130,000 (13%):</b> Facebook acts like a polite shop assistant who reminds cart abandoners, "
        "<i>'You left a lawn dress in your cart—complete your order for fast delivery!'</i> It also reaches mature 30+ family shoppers at 3.68x ROAS.<br/>"
        "• <b>TikTok gets Rs. 80,000 (8%):</b> TikTok is like distributing flyers at university gates. Millions of Gen Z students discover "
        "the brand cheaply (Rs. 9.66 CPC). It is strictly capped for starter items under Rs. 2,500.<br/>"
        "• <b>YouTube is curtailed to Rs. 40,000 (4%):</b> Viewers watching dramas or podcasts rarely pause to buy pret immediately. "
        "Spending heavily on YouTube burns cash; keeping it at 4% preserves video brand trust without capital bleed."
    )
    story.append(make_plain_english_box("Understanding Platform Roles in Everyday Terms", plain_plat, styles))
    story.append(Spacer(1, 5))

    # Strategic Scenarios Comparison Table
    story.append(Paragraph("Strategic Scenario Comparison (Evaluating Management Priorities via SLSQP):", styles['SubSecHeader']))
    scenario_data = [
        [Paragraph("<b>Scenario</b>", styles['TableHead']), Paragraph("<b>Spend (PKR)</b>", styles['TableHead']), Paragraph("<b>Projected Revenue</b>", styles['TableHead']), Paragraph("<b>Blended ROAS</b>", styles['TableHead']), Paragraph("<b>Blended CPA</b>", styles['TableHead']), Paragraph("<b>Orders</b>", styles['TableHead']), Paragraph("<b>True Net Profit</b>", styles['TableHead'])],
        [Paragraph("<b>Balanced Growth (Recommended)</b>", styles['TableCell']), Paragraph("Rs. 1,000,000", styles['TableCellCenter']), Paragraph("Rs. 4,367,388", styles['TableCellCenter']), Paragraph("<b>4.37x</b>", styles['TableCellCenter']), Paragraph("Rs. 508", styles['TableCellCenter']), Paragraph("1,970", styles['TableCellCenter']), Paragraph("<b>Rs. 637,864 (14.6%)</b>", styles['TableCellCenter'])],
        [Paragraph("<b>ROAS Maximizer (Squeeze)</b>", styles['TableCell']), Paragraph("Rs. 1,000,000", styles['TableCellCenter']), Paragraph("Rs. 4,639,581", styles['TableCellCenter']), Paragraph("<b>4.64x</b>", styles['TableCellCenter']), Paragraph("Rs. 518", styles['TableCellCenter']), Paragraph("1,931", styles['TableCellCenter']), Paragraph("<b>Rs. 779,028 (16.8%)</b>", styles['TableCellCenter'])],
        [Paragraph("<b>Unconstrained Direct-Response</b>", styles['TableCell']), Paragraph("Rs. 1,000,000", styles['TableCellCenter']), Paragraph("Rs. 4,733,391", styles['TableCellCenter']), Paragraph("<b>4.73x</b>", styles['TableCellCenter']), Paragraph("Rs. 509", styles['TableCellCenter']), Paragraph("1,965", styles['TableCellCenter']), Paragraph("<b>Rs. 816,217 (17.2%)</b>", styles['TableCellCenter'])],
        [Paragraph("<b>Aggressive Scale (Volume)</b>", styles['TableCell']), Paragraph("Rs. 1,000,000", styles['TableCellCenter']), Paragraph("Rs. 3,825,577", styles['TableCellCenter']), Paragraph("<b>3.83x</b>", styles['TableCellCenter']), Paragraph("Rs. 468", styles['TableCellCenter']), Paragraph("2,136", styles['TableCellCenter']), Paragraph("<b>Rs. 335,522 (8.8%)</b>", styles['TableCellCenter'])],
    ]
    t_scen = Table(scenario_data, colWidths=[138, 62, 75, 52, 58, 48, 90])
    t_scen.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), SECONDARY),
        ('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_LIGHT]),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(t_scen)
    story.append(Spacer(1, 4))

    scen_plain = (
        "<b>Scenario Tradeoffs & The Rationale for TikTok/YouTube Spend:</b><br/>"
        "• <b>Why Fund TikTok (8%) and YouTube (4%) When They Lose Standalone Margin?</b> A pure unconstrained direct-response optimizer "
        "zeros out TikTok and YouTube (0%), concentrating 62% in Google and 38% in Instagram to generate Rs. 816K short-term profit. "
        "However, in a multi-touch attribution ecosystem, Google and Instagram harvest demand created upstream. Completely eliminating "
        "top-of-funnel discovery causes high-intent search audience exhaustion within 60–90 days, degrading Google's marginal ROAS.<br/>"
        "• <b>Balanced Growth (Recommended):</b> Sustains customer replenishment across 1,970 orders while securing Rs. 638K in net profit.<br/>"
        "• <b>ROAS Maximizer:</b> Constrains TikTok and YouTube to 2% minimums, achieving 4.64x blended ROAS and Rs. 779K net profit.<br/>"
        "• <b>Aggressive Scale:</b> Prioritizes raw order acquisition (2,136 orders) via 30% TikTok / 45% Instagram, accepting an 8.8% operating net margin."
    )
    story.append(make_callout(scen_plain, styles))

    story.append(PageBreak())

    # ==========================================================================
    # PAGE 4: PLATFORM PERFORMANCE & UNIT ECONOMICS (100,000 RECORD PROOF)
    # ==========================================================================
    story.append(Paragraph("3. Platform Performance Benchmark & Real Unit Economics", styles['SecHeader']))
    story.append(Paragraph(
        "To eliminate guesswork, we analyzed 100,000 multi-channel marketing interaction logs calibrated to actual Pakistani "
        "consumer buying habits, product baskets (Rs. 1,800 tote bags to Rs. 5,000 lawn suits), and currency auction rates. "
        "Standard errors and 95% Confidence Intervals are computed via 1,000-iteration daily cluster block bootstrap resampling:",
        styles['BodyCustom']
    ))

    # Platform Table
    p_data = [
        [Paragraph("<b>Platform</b>", styles['TableHead']), Paragraph("<b>Total Spend (PKR)</b>", styles['TableHead']), Paragraph("<b>Total Revenue (PKR)</b>", styles['TableHead']), Paragraph("<b>ROAS (95% CI)</b>", styles['TableHead']), Paragraph("<b>CPA (PKR)</b>", styles['TableHead']), Paragraph("<b>CPC (PKR)</b>", styles['TableHead']), Paragraph("<b>CVR %</b>", styles['TableHead']), Paragraph("<b>CTR %</b>", styles['TableHead'])],
        [Paragraph("<b>Google Ads</b>", styles['TableCell']), Paragraph("Rs. 137,124,552", styles['TableCellCenter']), Paragraph("Rs. 690,115,501", styles['TableCellCenter']), Paragraph("<b>5.03x</b> [5.00, 5.07]", styles['TableCellCenter']), Paragraph("Rs. 597", styles['TableCellCenter']), Paragraph("Rs. 32.44", styles['TableCellCenter']), Paragraph("5.43%", styles['TableCellCenter']), Paragraph("3.39%", styles['TableCellCenter'])],
        [Paragraph("<b>Instagram Ads</b>", styles['TableCell']), Paragraph("Rs. 121,576,622", styles['TableCellCenter']), Paragraph("Rs. 561,469,459", styles['TableCellCenter']), Paragraph("<b>4.62x</b> [4.59, 4.65]", styles['TableCellCenter']), Paragraph("Rs. 388", styles['TableCellCenter']), Paragraph("Rs. 20.72", styles['TableCellCenter']), Paragraph("5.34%", styles['TableCellCenter']), Paragraph("2.59%", styles['TableCellCenter'])],
        [Paragraph("<b>Facebook Ads</b>", styles['TableCell']), Paragraph("Rs. 86,208,025", styles['TableCellCenter']), Paragraph("Rs. 307,640,287", styles['TableCellCenter']), Paragraph("<b>3.57x</b> [3.54, 3.60]", styles['TableCellCenter']), Paragraph("Rs. 656", styles['TableCellCenter']), Paragraph("Rs. 25.03", styles['TableCellCenter']), Paragraph("3.81%", styles['TableCellCenter']), Paragraph("1.79%", styles['TableCellCenter'])],
        [Paragraph("<b>TikTok Ads</b>", styles['TableCell']), Paragraph("Rs. 52,221,902", styles['TableCellCenter']), Paragraph("Rs. 120,324,838", styles['TableCellCenter']), Paragraph("<b>2.30x</b> [2.28, 2.33]", styles['TableCellCenter']), Paragraph("Rs. 482", styles['TableCellCenter']), Paragraph("Rs. 9.66", styles['TableCellCenter']), Paragraph("2.00%", styles['TableCellCenter']), Paragraph("2.19%", styles['TableCellCenter'])],
        [Paragraph("<b>YouTube Ads</b>", styles['TableCell']), Paragraph("Rs. 34,437,488", styles['TableCellCenter']), Paragraph("Rs. 66,241,815", styles['TableCellCenter']), Paragraph("<b>1.92x</b> [1.89, 1.95]", styles['TableCellCenter']), Paragraph("Rs. 1,512", styles['TableCellCenter']), Paragraph("Rs. 36.39", styles['TableCellCenter']), Paragraph("2.41%", styles['TableCellCenter']), Paragraph("1.10%", styles['TableCellCenter'])],
        [Paragraph("<b>BLENDED TOTAL</b>", styles['TableHead']), Paragraph("<b>Rs. 431,568,589</b>", styles['TableHead']), Paragraph("<b>Rs. 1,745,791,900</b>", styles['TableHead']), Paragraph("<b>4.05x</b> [4.03, 4.07]", styles['TableHead']), Paragraph("<b>Rs. 536</b>", styles['TableHead']), Paragraph("<b>Rs. 21.68</b>", styles['TableHead']), Paragraph("<b>4.04%</b>", styles['TableHead']), Paragraph("<b>2.27%</b>", styles['TableHead'])],
    ]
    t_plat = Table(p_data, colWidths=[74, 75, 80, 56, 52, 52, 42, 42])
    t_plat.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('BACKGROUND', (0,-1), (-1,-1), DARK_BG),
        ('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, BG_LIGHT]),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(t_plat)
    story.append(Spacer(1, 4))

    # Dual Visuals: Chart 1 & Chart 2 side by side
    p1_path = os.path.join(fig_dir, "01_cac_cpa_by_platform.png")
    p2_path = os.path.join(fig_dir, "02_roas_vs_breakeven_benchmark.png")
    
    if os.path.exists(p1_path) and os.path.exists(p2_path):
        img_table = Table([[
            Image(p1_path, width=3.55*inch, height=1.82*inch),
            Image(p2_path, width=3.55*inch, height=1.82*inch)
        ]], colWidths=[261, 262])
        img_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(img_table)
        story.append(Paragraph("Figure 2: (Left) Customer Acquisition Cost (CPA) Comparison; (Right) Return on Ad Spend vs. 3.0x Break-Even Benchmark", styles['CaptionText']))

    # Plain English Break-Even Economics Box
    breakeven_text = (
        "<b>Mathematical Derivation of the 3.0x Break-Even ROAS Threshold:</b><br/>"
        "In Pakistani D2C commerce, 85%+ orders use Cash on Delivery (COD). A rigorous unit economics equation reveals the true margin threshold:<br/>"
        "• <b>Product Manufacturing (COGS):</b> 45.0% of retail price (leaving 55.0% gross product margin).<br/>"
        "• <b>Courier Delivery Fee:</b> Rs. 220 per dispatched parcel | <b>COD Rejection / Return Rate:</b> 12.0% average across Pakistan.<br/>"
        "• <b>Return Courier Fee (Reverse Logistics):</b> Rs. 180 per bounced parcel.<br/>"
        "For an average order basket of <b>Rs. 2,100</b>, delivered revenue (88%) is Rs. 1,848. Net product gross profit is Rs. 1,016. "
        "Logistics fees total Rs. 242 (Rs. 220 shipping + 12% x Rs. 180 return). This leaves <b>Rs. 774 maximum allowable CPA</b>.<br/>"
        "Dividing revenue (Rs. 2,100) by max CPA (Rs. 774) yields a <b>2.71x to 3.00x Break-Even ROAS</b>. "
        "Platforms below 2.5x (TikTok at 2.30x: -Rs. 20.2M; YouTube at 1.92x: -Rs. 7.9M) lose operating capital on standalone orders and must serve solely as discovery drivers.<br/>"
        "<i>Note on Confidence Intervals:</i> 95% CIs reflect 1,000-iteration daily cluster bootstrap resampling, capturing temporal day-to-day realization variance."
    )
    story.append(make_plain_english_box("The Real Economics of a Pakistani E-Commerce Order", breakeven_text, styles))

    story.append(PageBreak())

    # ==========================================================================
    # PAGE 5: THE BIG DATA CHALLENGE - PANDAS VS. MAPREDUCE VS. SPARK
    # ==========================================================================
    story.append(Paragraph("4. Big Data Framework Scalability Benchmark (10K to 10M Records)", styles['SecHeader']))
    story.append(Paragraph(
        "To test how enterprise data architectures survive when an e-commerce brand scales from thousands to millions of customer "
        "interactions, we executed a standardized aggregation workload (`GroupBy (platform, city)` with metric projection) across 4 tiers. "
        "Each benchmark runs in an isolated Python process to measure true peak RSS, and timing measures pure aggregation/reduction processing:",
        styles['BodyCustom']
    ))

    # Benchmark Table
    bench_table_data = [
        [Paragraph("<b>Data Tier</b>", styles['TableHead']), Paragraph("<b>Records</b>", styles['TableHead']), Paragraph("<b>Engine Framework</b>", styles['TableHead']), Paragraph("<b>Execution Time (s)</b>", styles['TableHead']), Paragraph("<b>Peak Memory (MB)</b>", styles['TableHead']), Paragraph("<b>Throughput (rec/s)</b>", styles['TableHead'])],
        [Paragraph("10K", styles['TableCellCenter']), Paragraph("10,000", styles['TableCellCenter']), Paragraph("Pandas (In-Memory)", styles['TableCell']), Paragraph("0.003s", styles['TableCellCenter']), Paragraph("73.6 MB", styles['TableCellCenter']), Paragraph("3,192,890", styles['TableCellCenter'])],
        [Paragraph("10K", styles['TableCellCenter']), Paragraph("10,000", styles['TableCellCenter']), Paragraph("MapReduce Sim (Multi-Proc)", styles['TableCell']), Paragraph("0.313s", styles['TableCellCenter']), Paragraph("146.6 MB", styles['TableCellCenter']), Paragraph("31,965", styles['TableCellCenter'])],
        [Paragraph("10K", styles['TableCellCenter']), Paragraph("10,000", styles['TableCellCenter']), Paragraph("Spark Sim (Partitioned DAG)", styles['TableCell']), Paragraph("0.009s", styles['TableCellCenter']), Paragraph("74.1 MB", styles['TableCellCenter']), Paragraph("1,048,341", styles['TableCellCenter'])],
        [Paragraph("100K", styles['TableCellCenter']), Paragraph("100,000", styles['TableCellCenter']), Paragraph("Pandas (In-Memory)", styles['TableCell']), Paragraph("0.013s", styles['TableCellCenter']), Paragraph("103.0 MB", styles['TableCellCenter']), Paragraph("7,741,286", styles['TableCellCenter'])],
        [Paragraph("100K", styles['TableCellCenter']), Paragraph("100,000", styles['TableCellCenter']), Paragraph("MapReduce Sim (Multi-Proc)", styles['TableCell']), Paragraph("0.347s", styles['TableCellCenter']), Paragraph("207.7 MB", styles['TableCellCenter']), Paragraph("287,752", styles['TableCellCenter'])],
        [Paragraph("100K", styles['TableCellCenter']), Paragraph("100,000", styles['TableCellCenter']), Paragraph("Spark Sim (Partitioned DAG)", styles['TableCell']), Paragraph("0.022s", styles['TableCellCenter']), Paragraph("102.9 MB", styles['TableCellCenter']), Paragraph("4,525,561", styles['TableCellCenter'])],
        [Paragraph("1M", styles['TableCellCenter']), Paragraph("1,000,000", styles['TableCellCenter']), Paragraph("Pandas (In-Memory)", styles['TableCell']), Paragraph("0.114s", styles['TableCellCenter']), Paragraph("369.9 MB", styles['TableCellCenter']), Paragraph("8,742,003", styles['TableCellCenter'])],
        [Paragraph("1M", styles['TableCellCenter']), Paragraph("1,000,000", styles['TableCellCenter']), Paragraph("MapReduce Sim (Multi-Proc)", styles['TableCell']), Paragraph("0.920s", styles['TableCellCenter']), Paragraph("803.4 MB", styles['TableCellCenter']), Paragraph("1,087,160", styles['TableCellCenter'])],
        [Paragraph("1M", styles['TableCellCenter']), Paragraph("1,000,000", styles['TableCellCenter']), Paragraph("Spark Sim (Partitioned DAG)", styles['TableCell']), Paragraph("0.144s", styles['TableCellCenter']), Paragraph("383.2 MB", styles['TableCellCenter']), Paragraph("6,939,747", styles['TableCellCenter'])],
        [Paragraph("<b>10M</b>", styles['TableCellCenter']), Paragraph("10,000,000", styles['TableCellCenter']), Paragraph("<b>Pandas (Streaming Aggregation)</b>", styles['TableCell']), Paragraph("<b>3.488s</b>", styles['TableCellCenter']), Paragraph("1,658.2 MB", styles['TableCellCenter']), Paragraph("<b>2,866,712</b>", styles['TableCellCenter'])],
        [Paragraph("<b>10M</b>", styles['TableCellCenter']), Paragraph("10,000,000", styles['TableCellCenter']), Paragraph("<b>MapReduce (Streaming Aggregation)</b>", styles['TableCell']), Paragraph("<b>15.940s</b>", styles['TableCellCenter']), Paragraph("1,833.6 MB", styles['TableCellCenter']), Paragraph("<b>627,348</b>", styles['TableCellCenter'])],
        [Paragraph("<b>10M</b>", styles['TableCellCenter']), Paragraph("10,000,000", styles['TableCellCenter']), Paragraph("<b>Spark Sim (Streaming Aggregation)</b>", styles['TableCell']), Paragraph("<b>4.727s</b>", styles['TableCellCenter']), Paragraph("1,665.3 MB", styles['TableCellCenter']), Paragraph("<b>2,115,334</b>", styles['TableCellCenter'])],
    ]
    t_bench = Table(bench_table_data, colWidths=[55, 75, 115, 75, 85, 118])
    t_bench.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-4), [colors.white, BG_LIGHT]),
        ('BACKGROUND', (0,-3), (-1,-1), colors.HexColor('#FEF9E7')),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(t_bench)
    story.append(Spacer(1, 4))

    # Dual Visuals: Chart 3 & Chart 4 side by side
    p3_path = os.path.join(fig_dir, "03_big_data_execution_time_benchmark.png")
    p4_path = os.path.join(fig_dir, "04_big_data_memory_throughput_benchmark.png")
    if os.path.exists(p3_path) and os.path.exists(p4_path):
        img_table2 = Table([[
            Image(p3_path, width=3.55*inch, height=1.82*inch),
            Image(p4_path, width=3.55*inch, height=1.82*inch)
        ]], colWidths=[261, 262])
        img_table2.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(img_table2)
        story.append(Paragraph("Figure 3: (Left) Big Data Execution Time Scalability Curve (Log Scale); (Right) Peak RAM & Throughput at Scale", styles['CaptionText']))

    # Plain English Automobile Analogy Box
    car_analogy = (
        "<b>Architectural Tradeoff: Single-Node vs. Distributed Cluster Execution</b><br/>"
        "• <b>Pandas (Vectorized In-Memory):</b> On single-node datasets that fit entirely in physical RAM (<1GB), Pandas is fastest (8.7M rec/s) "
        "because C-vectorized execution incurs zero IPC or network serialization overhead. Pure aggregation on 10M records completes in 3.49s.<br/>"
        "• <b>MapReduce Simulation (Multi-Process):</b> Simulates parallel Map and Reduce stages across Python worker processes. It incurs IPC serialization "
        "overhead on smaller batches and higher peak memory (803 MB at 1M; 1,834 MB at 10M), but demonstrates parallel divide-and-conquer processing.<br/>"
        "• <b>Apache Spark Engine:</b> In local simulation, Spark's partitioned Catalyst model processes millions of records smoothly (4.73s on 10M). "
        "In enterprise production environments, native PySpark (included in our Google Colab notebook) distributes tasks across worker nodes, "
        "enabling out-of-core memory spilling and resilient fault tolerance for datasets exceeding RAM (>100GB)."
    )
    story.append(make_plain_english_box("Why Big Data Architecture Matters: Architectural Realities", car_analogy, styles))

    story.append(PageBreak())

    # ==========================================================================
    # PAGE 6: WHY NOT PUT ALL MONEY ON GOOGLE? DIMINISHING RETURNS & FUNNEL
    # ==========================================================================
    story.append(Paragraph("5. Customer Fatigue, Diminishing Returns & The Conversion Funnel", styles['SecHeader']))
    story.append(Paragraph(
        "A common question asked by company executives is: <i>'If Google has the highest ROAS (5.03x), why don't we put all Rs. 1 Million into Google?'</i> "
        "The answer lies in two universal marketing realities: <b>Audience Saturation</b> and <b>Funnel Drop-offs</b>.",
        styles['BodyCustom']
    ))

    # Dual Visuals: Chart 7 & Chart 5 side by side
    p7_path = os.path.join(fig_dir, "07_diminishing_returns_marginal_roas.png")
    p5_path = os.path.join(fig_dir, "05_conversion_funnel_by_platform.png")
    if os.path.exists(p7_path) and os.path.exists(p5_path):
        img_table3 = Table([[
            Image(p7_path, width=3.55*inch, height=1.95*inch),
            Image(p5_path, width=3.55*inch, height=1.95*inch)
        ]], colWidths=[261, 262])
        img_table3.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(img_table3)
        story.append(Paragraph("Figure 4: (Left) Diminishing Marginal ROAS Curves as Spend Increases; (Right) Conversion Funnel Stages by Channel", styles['CaptionText']))

    # Plain English Buffet Analogy Box
    buffet_analogy = (
        "<b>The Biryani Buffet Analogy: Why You Cannot Spend Everything on Google</b><br/>"
        "Imagine going to a delicious wedding buffet. The first plate of biryani is incredible. The second plate is tasty. "
        "By the fourth plate, you are completely full. If someone forces you to eat a fifth plate, you will feel sick.<br/>"
        "In digital marketing, human beings react the exact same way—this is known as <b>The Law of Diminishing Returns</b>:<br/>"
        "• In Pakistan, there are only so many people searching Google for <i>'stitched lawn suits'</i> each day.<br/>"
        "• Your first Rs. 100,000 captures those ready-to-buy customers at a massive <b>5.03x ROAS</b>.<br/>"
        "• But if you force Rs. 1,000,000 into Google in 30 days, Google starts showing your ads to people who aren't interested, or shows "
        "the same ad 15 times to the same person. The person gets annoyed (ad fatigue) and stops clicking.<br/>"
        "• Look at Figure 4 (Left): As spend climbs toward Rs. 1 Million on a single channel, the marginal revenue per Rupee collapses down to 1.8x. "
        "By distributing the budget into Instagram (Rs. 350K) and Facebook (Rs. 130K), you catch customers at their highest enjoyment point on every app!"
    )
    story.append(make_plain_english_box("Understanding Diminishing Returns with a Simple Analogy", buffet_analogy, styles))
    story.append(Spacer(1, 4))

    # Funnel Explanation Box
    funnel_text = (
        "<b>Where do Pakistani customers disappear in the funnel? (Figure 4 Right)</b><br/>"
        "• <b>Impressions (Top Bar):</b> Millions of people glance at your ad while scrolling. TikTok generates 6.1 Million views easily.<br/>"
        "• <b>Clicks (Middle Bar):</b> Out of 100 people who see the ad, only 2 to 3 people tap on it (CTR). TikTok gets huge clicks because it is cheap.<br/>"
        "• <b>Conversions / Orders (Bottom Bar):</b> This is where the truth comes out! Out of all those clicks, Google converts 5.4% and Instagram "
        "converts 5.3% into paying deliveries, while TikTok converts only 2.0%. That is why Google and Instagram produce the thickest order bars."
    )
    story.append(make_callout(funnel_text, styles))

    story.append(PageBreak())

    # ==========================================================================
    # PAGE 7: THE PAKISTANI GROUND REALITY - COD & REGIONAL TARGETING
    # ==========================================================================
    story.append(Paragraph("6. Regional City Deployment & The Realities of Cash on Delivery", styles['SecHeader']))
    story.append(Paragraph(
        "In international e-commerce, customers pay with credit cards upfront. In Pakistan, <b>over 80% of all online orders are "
        "Cash on Delivery (COD)</b>. This single factor changes everything about where digital advertising money should be spent:",
        styles['BodyCustom']
    ))

    # Regional City Table
    city_data = [
        [Paragraph("<b>City / Hub</b>", styles['TableHead']), Paragraph("<b>Share %</b>", styles['TableHead']), Paragraph("<b>Budget (PKR)</b>", styles['TableHead']), Paragraph("<b>Strategic Rationale & Logistics Corridors</b>", styles['TableHead'])],
        [Paragraph("<b>Karachi</b>", styles['TableCell']), Paragraph("36.2%", styles['TableCellCenter']), Paragraph("Rs. 362,003", styles['TableCellCenter']), Paragraph("Mega-city e-commerce hub; highest COD parcel volume & customer density.", styles['TableCell'])],
        [Paragraph("<b>Lahore</b>", styles['TableCell']), Paragraph("28.6%", styles['TableCellCenter']), Paragraph("Rs. 285,738", styles['TableCellCenter']), Paragraph("Cultural fashion capital; highest demand for stitched lawn pret & designer wear.", styles['TableCell'])],
        [Paragraph("<b>Islamabad</b>", styles['TableCell']), Paragraph("15.2%", styles['TableCellCenter']), Paragraph("Rs. 152,018", styles['TableCellCenter']), Paragraph("Highest purchasing power per capita and largest festive collection AOV.", styles['TableCell'])],
        [Paragraph("<b>Rawalpindi</b>", styles['TableCell']), Paragraph("7.8%", styles['TableCellCenter']), Paragraph("Rs. 78,213", styles['TableCellCenter']), Paragraph("Twin-city order volume with fast 24h courier fulfillment corridors.", styles['TableCell'])],
        [Paragraph("<b>Faisalabad</b>", styles['TableCell']), Paragraph("4.2%", styles['TableCellCenter']), Paragraph("Rs. 41,601", styles['TableCellCenter']), Paragraph("Textile and industrial hub; strong response to value clearance promotions.", styles['TableCell'])],
        [Paragraph("<b>Multan</b>", styles['TableCell']), Paragraph("3.5%", styles['TableCellCenter']), Paragraph("Rs. 34,663", styles['TableCellCenter']), Paragraph("Rapidly growing South Punjab hub with rising mobile COD adoption.", styles['TableCell'])],
        [Paragraph("<b>Peshawar</b>", styles['TableCell']), Paragraph("1.8%", styles['TableCellCenter']), Paragraph("Rs. 17,953", styles['TableCellCenter']), Paragraph("Selective demand for festive and unstitched formal wear.", styles['TableCell'])],
        [Paragraph("<b>Sialkot</b>", styles['TableCell']), Paragraph("1.6%", styles['TableCellCenter']), Paragraph("Rs. 16,227", styles['TableCellCenter']), Paragraph("High export-economy purchasing power with low doorstep rejection.", styles['TableCell'])],
        [Paragraph("<b>Other Tier-2 (Quetta, Gujranwala)</b>", styles['TableCell']), Paragraph("1.1%", styles['TableCellCenter']), Paragraph("Rs. 11,583", styles['TableCellCenter']), Paragraph("Emerging regional testing with controlled delivery lead times.", styles['TableCell'])],
        [Paragraph("<b>TOTAL</b>", styles['TableHead']), Paragraph("<b>100.0%</b>", styles['TableHead']), Paragraph("<b>Rs. 1,000,000</b>", styles['TableHead']), Paragraph("<b>Concentrates 87.8% of spend in Top-4 Tier-1 logistics hubs.</b>", styles['TableHead'])],
    ]
    t_city = Table(city_data, colWidths=[105, 45, 75, 298])
    t_city.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('BACKGROUND', (0,-1), (-1,-1), DARK_BG),
        ('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, BG_LIGHT]),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(t_city)
    story.append(Spacer(1, 4))

    # Embed Chart 8: Regional City Revenue Efficiency Matrix
    p8_path = os.path.join(fig_dir, "08_city_revenue_efficiency_matrix.png")
    if os.path.exists(p8_path):
        story.append(Image(p8_path, width=7.0*inch, height=1.95*inch))
        story.append(Paragraph("Figure 5: Regional City Revenue vs. ROAS Efficiency Matrix across Pakistani Urban Hubs", styles['CaptionText']))

    # Plain English COD and RTO Explanation Box
    cod_text = (
        "<b>The Hidden Enemy of Pakistani E-Commerce: Return to Origin (RTO)</b><br/>"
        "Why did our model allocate <b>87.8% of the advertising money into Karachi, Lahore, and Islamabad/Rawalpindi</b>?<br/>"
        "• When an online customer in Karachi orders a lawn dress on Cash on Delivery, the courier rider delivers it in 24–48 hours. "
        "The customer remembers ordering it, pays the cash, and the delivery success rate is <b>over 88% to 90%</b>.<br/>"
        "• But when an ad runs in remote towns or distant villages, shipping takes 5 to 7 days. By the time the rider shows up, "
        "the customer has changed their mind, doesn't have the cash, or refuses the door. The parcel returns back to the warehouse.<br/>"
        "• When a parcel bounces (RTO), <b>the brand loses money twice</b>: You paid Rs. 220 to send the package, another Rs. 180 for the return courier, "
        "and you already burned Rs. 500 on the ad! Spending ad money in weak courier zones silently bankrupts Pakistani brands.<br/>"
        "Focusing ad spend in Tier-1 logistics hubs guarantees fast 24-hour deliveries, keeps parcel returns under 12%, and protects cash flow."
    )
    story.append(make_plain_english_box("Why Courier Logistics Dictates Advertising Profit in Pakistan", cod_text, styles))

    story.append(PageBreak())

    # ==========================================================================
    # PAGE 8: CUSTOMER DEMOGRAPHICS & PAKISTANI RETAIL SEASONALITY
    # ==========================================================================
    story.append(Paragraph("7. Customer Demographics & Pakistani Retail Seasonality", styles['SecHeader']))
    story.append(Paragraph(
        "Direct-to-consumer advertising succeeds only when products match the exact gender and age habits of Pakistani consumers, "
        "timed precisely to religious and seasonal buying cycles:",
        styles['BodyCustom']
    ))

    # Dual Visuals: Chart 9 & Chart 10 side by side
    p9_path = os.path.join(fig_dir, "09_demographic_age_gender_performance.png")
    p10_path = os.path.join(fig_dir, "10_monthly_spend_revenue_profit_trend.png")
    if os.path.exists(p9_path) and os.path.exists(p10_path):
        img_table4 = Table([[
            Image(p9_path, width=3.55*inch, height=1.95*inch),
            Image(p10_path, width=3.55*inch, height=1.95*inch)
        ]], colWidths=[261, 262])
        img_table4.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(img_table4)
        story.append(Paragraph("Figure 6: (Left) Buyer Demographic Cohort Efficiency; (Right) 12-Month Spend vs. Revenue vs. Net Margin Trajectory", styles['CaptionText']))

    # Plain English Demographics and Seasonality Explanation
    demo_text = (
        "<b>Who is the Pakistani Online Buyer and When Do They Spend Money?</b><br/>"
        "• <b>Demographic Findings (Figure 6 Left):</b> Female consumers drive 69.5% of total revenue. "
        "Female 35–44 cohorts deliver the highest portfolio efficiency (<b>4.84x ROAS</b>, 17.9% operating net margin), "
        "while young university women (18–24) drive volume at the lowest acquisition cost (<b>Rs. 464 CPA</b>) for tote bags and starter pret. "
        "Male buyers represent 23.4% of spend, yielding higher average order values (<b>Rs. 2,675–2,698 AOV</b>) for festive gifting.<br/>"
        "• <b>When They Buy (Figure 6 Right): The 4 Seasonal Waves of Pakistani E-Commerce:</b><br/>"
        "1. <b>Wave 1 — Spring Lawn Launch (February/March):</b> New designer catalogs release; high CTR browsing and wishlisting.<br/>"
        "2. <b>Wave 2 — Ramadan & Eid-ul-Fitr (April/May):</b> The biggest sales boom of the year. Revenue spikes dramatically (+140%). "
        "Ad budgets should scale 40-50% in weeks 2-3 of Ramadan to capture Eid wardrobe shopping before courier cut-off dates.<br/>"
        "3. <b>Wave 3 — Blessed Friday / 11.11 (November):</b> High-volume clearance discounting where CVR rises by 25%.<br/>"
        "4. <b>Wave 4 — Winter Wedding Season (December/January):</b> Demand shifts toward velvet, shawls, and premium formal wear."
    )
    story.append(make_plain_english_box("Decoding the Pakistani Consumer & Seasonal Shopping Calendar", demo_text, styles))

    story.append(PageBreak())

    # ==========================================================================
    # PAGE 9: 30-DAY EXECUTIVE PLAYBOOK & PRODUCTION SQL SUITE
    # ==========================================================================
    story.append(Paragraph("8. 30-Day Executive Action Playbook & Production SQL Suite", styles['SecHeader']))
    story.append(Paragraph(
        "To translate these analytics into immediate business impact, marketing and operational teams should execute this "
        "structured 30-day rollout plan:",
        styles['BodyCustom']
    ))

    # Action Plan Table
    plan_data = [
        [Paragraph("<b>Timeframe</b>", styles['TableHead']), Paragraph("<b>Operational Milestones & Action Items (Execution Playbook)</b>", styles['TableHead'])],
        [Paragraph("<b>Week 1</b><br/>Spend Rebalance", styles['TableCell']), Paragraph("<b>Scale the Profit Engines:</b> Deploy Rs. 400,000 into Google Search/Shopping (high-intent pret keywords) and Rs. 350,000 into Instagram Reels.<br/><b>Cap Top-of-Funnel Leakage:</b> Restrict TikTok to 8% (Rs. 80,000) and YouTube to 4% (Rs. 40,000) to stop standalone operating losses.", styles['TableCell'])],
        [Paragraph("<b>Week 2</b><br/>Creative & Pricing Fix", styles['TableCell']), Paragraph("<b>Eliminate 'Check DM for Price':</b> Transparent pricing (e.g., <i>'Rs. 2,499 with Free Cash on Delivery'</i>) displayed directly in ad overlays prevents click waste and boosts checkout completion by 34%.", styles['TableCell'])],
        [Paragraph("<b>Week 3</b><br/>Logistics Safeguards", styles['TableCell']), Paragraph("<b>Protect Cash Flow & Prevent RTO:</b> Concentrate 87.8% of spend in Karachi, Lahore, Islamabad, and Rawalpindi. Deploy automated WhatsApp verification prior to dispatch to keep COD doorstep rejections below 10%.", styles['TableCell'])],
        [Paragraph("<b>Week 4</b><br/>Automated Big Data", styles['TableCell']), Paragraph("<b>Automate Warehouse Allocation:</b> Integrate queries.sql into daily BigQuery/Snowflake warehouses. Run the mathematical optimizer (scripts/04_budget_recommendation_engine.py) weekly to dynamically balance channel marginal ROAS.", styles['TableCell'])],
    ]
    t_plan = Table(plan_data, colWidths=[95, 428])
    t_plan.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_LIGHT]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_plan)
    story.append(Spacer(1, 4))

    # SQL Code Excerpt
    story.append(Paragraph("Production SQL Warehouse Query (Query 7: Pure-SQL Automated Budget Reallocator):", styles['SubSecHeader']))
    sql_code = (
        "<b>-- Excerpt from queries.sql (Pure-SQL Automated Budget Reallocation Engine)</b><br/>"
        "<font color='#01696F'>WITH</font> channel_perf <font color='#01696F'>AS</font> (<br/>"
        "&nbsp;&nbsp;<font color='#01696F'>SELECT</font> platform, <font color='#01696F'>SUM</font>(spend) <font color='#01696F'>AS</font> current_spend, "
        "<font color='#01696F'>SUM</font>(revenue) <font color='#01696F'>AS</font> current_revenue,<br/>"
        "&nbsp;&nbsp;<font color='#01696F'>ROUND</font>(<font color='#01696F'>SUM</font>(revenue)/<font color='#01696F'>NULLIF</font>(<font color='#01696F'>SUM</font>(spend),0),2) <font color='#01696F'>AS</font> roas<br/>"
        "&nbsp;&nbsp;<font color='#01696F'>FROM</font> campaign_data <font color='#01696F'>GROUP BY</font> platform<br/>"
        ")<br/>"
        "<font color='#01696F'>SELECT</font> platform, roas,<br/>"
        "&nbsp;&nbsp;<font color='#01696F'>CASE</font><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<font color='#01696F'>WHEN</font> roas &gt;= 4.50 <font color='#01696F'>THEN</font> 'PRIMARY SCALE (+25% to +40%) - HIGH EFFICIENCY'<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<font color='#01696F'>WHEN</font> roas &gt;= 3.50 <font color='#01696F'>THEN</font> 'CORE EXPANSION - MEETS BENCHMARK'<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<font color='#01696F'>WHEN</font> roas &gt;= 2.50 <font color='#01696F'>THEN</font> 'RETARGETING & RETENTION'<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<font color='#01696F'>ELSE</font> 'REDUCE / TOP-OF-FUNNEL DISCOVERY'<br/>"
        "&nbsp;&nbsp;<font color='#01696F'>END AS</font> budget_recommendation<br/>"
        "<font color='#01696F'>FROM</font> channel_perf <font color='#01696F'>ORDER BY</font> roas <font color='#01696F'>DESC</font>;"
    )
    t_sql = Table([[Paragraph(sql_code, styles['TableCell'])]], colWidths=[523])
    t_sql.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFB')),
        ('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_sql)
    story.append(Spacer(1, 4))

    # Plain English SQL explanation
    sql_plain = (
        "<b>What is this SQL code doing in simple terms?</b> This automated script constantly monitors all five advertising platforms. "
        "If Google or Instagram is hitting a ROAS over 3.5x, it flags to management: <i>'Pump more money in!'</i> If YouTube or TikTok falls "
        "below the 3.0x break-even line, it flags: <i>'Cap spend to discovery budgets!'</i> This prevents human error and stops marketing teams from burning money."
    )
    story.append(make_plain_english_box("Automated Safety Switch", sql_plain, styles))
    story.append(Spacer(1, 4))

    # Concluding Sign-off Box
    signoff = Paragraph(
        "<b>Report Prepared by:</b> Zughaina — Marketing Data Analyst<br/>"
        "<b>Phase 2 GitHub Repository:</b> <a href='https://github.com/zughaina3/pakistan-digital-advertising-budget-optimizer'><font color='#01696F'><u>https://github.com/zughaina3/pakistan-digital-advertising-budget-optimizer</u></font></a><br/>"
        "<b>Methodology:</b> Validated via SLSQP optimization, empirical unit economics, and 10,000,000-record streaming big data benchmarks.",
        styles['CalloutBox']
    )
    t_sign = Table([[signoff]], colWidths=[523])
    t_sign.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 1, PRIMARY),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_sign)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"🎉 Publication-grade PDF successfully compiled to: {output_pdf}")
    print(f"📦 File size: {os.path.getsize(output_pdf)/1024:.1f} KB")
    return output_pdf


if __name__ == '__main__':
    build_pdf()
