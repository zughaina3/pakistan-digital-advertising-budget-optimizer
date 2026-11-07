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
        fontSize=22,
        leading=26,
        textColor=PRIMARY,
        spaceAfter=6
    ))
    styles.add(ParagraphStyle(
        name='CoverSubtitle',
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=TEXT_MAIN,
        spaceAfter=10
    ))
    styles.add(ParagraphStyle(
        name='SecHeader',
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=PRIMARY,
        spaceBefore=4,
        spaceAfter=4,
        keepWithNext=True
    ))
    styles.add(ParagraphStyle(
        name='SubSecHeader',
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=12.5,
        textColor=DARK_BG,
        spaceBefore=4,
        spaceAfter=3,
        keepWithNext=True
    ))
    styles.add(ParagraphStyle(
        name='BodyCustom',
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=TEXT_MAIN,
        spaceAfter=4
    ))
    styles.add(ParagraphStyle(
        name='CalloutBox',
        fontName='Helvetica',
        fontSize=7.8,
        leading=10.8,
        textColor=TEXT_MAIN,
        spaceAfter=2
    ))
    styles.add(ParagraphStyle(
        name='PlainEnglishText',
        fontName='Helvetica',
        fontSize=7.8,
        leading=10.8,
        textColor=colors.HexColor('#713F12'),
        spaceAfter=2
    ))
    styles.add(ParagraphStyle(
        name='TableHead',
        fontName='Helvetica-Bold',
        fontSize=7,
        leading=9,
        textColor=colors.white,
        alignment=1
    ))
    styles.add(ParagraphStyle(
        name='TableCell',
        fontName='Helvetica',
        fontSize=7,
        leading=9,
        textColor=TEXT_MAIN,
        alignment=0
    ))
    styles.add(ParagraphStyle(
        name='TableCellCenter',
        fontName='Helvetica',
        fontSize=7,
        leading=9,
        textColor=TEXT_MAIN,
        alignment=1
    ))
    styles.add(ParagraphStyle(
        name='TableCellBold',
        fontName='Helvetica-Bold',
        fontSize=7,
        leading=9,
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
        spaceAfter=3
    ))
    styles.add(ParagraphStyle(
        name='KPIVal',
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=15,
        textColor=PRIMARY,
        alignment=1,
        spaceAfter=3
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
        fontSize=7,
        leading=8.5,
        textColor=TEXT_MUTED,
        alignment=1,
        spaceBefore=2,
        spaceAfter=4
    ))

    return styles


def make_callout(text: str, styles, bg=CALLOUT_BG, border_color=PRIMARY, border_width=3):
    """Helper to create visually appealing callout blocks."""
    t = Table([[Paragraph(text, styles['CalloutBox'])]], colWidths=[523])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), bg),
        ('BOX', (0,0), (-1,-1), 0.5, border_color),
        ('LINEBEFORE', (0,0), (0,-1), border_width, border_color),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
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
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
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
        topMargin=42,
        bottomMargin=38
    )

    styles = get_styles()
    story = []

    # ==========================================================================
    # PAGE 1: COVER PAGE & EXECUTIVE ABSTRACT (PLAIN-ENGLISH OVERVIEW)
    # ==========================================================================
    story.append(Spacer(1, 6))
    
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
    story.append(Spacer(1, 8))

    story.append(Paragraph("Pakistan Digital Advertising Budget Optimizer", styles['CoverTitle']))
    story.append(Paragraph("<b>Phase 2:</b> Big Data Marketing Campaign Intelligence, Distributed Framework Benchmarking (Pandas vs. MapReduce vs. Spark) & Algorithmic Ad Budget Reallocation Engine", styles['CoverSubtitle']))
    
    # Metadata Box
    meta_data = [
        [
            Paragraph("<b>Author:</b> Zughaina (<font color='#01696F'>@zughaina3</font>)", styles['TableCell']),
            Paragraph("<b>Domain:</b> Pakistani D2C E-Commerce (Fashion, Lawn & Bags)", styles['TableCell']),
        ],
        [
            Paragraph("<b>Phase 2 GitHub:</b> <a href='https://github.com/zughaina3/pakistan-digital-advertising-budget-optimizer'><font color='#01696F'><u>https://github.com/zughaina3/pakistan-digital-advertising-budget-optimizer</u></font></a>", styles['TableCell']),
            Paragraph("<b>Capital Optimization Scope:</b> Rs. 1,000,000 (PKR 1.0M)", styles['TableCell']),
        ],
        [
            Paragraph("<b>Phase 1 Portfolio:</b> <a href='https://github.com/zughaina3/pakistan-digital-marketing-intelligence'><font color='#01696F'><u>https://github.com/zughaina3/pakistan-digital-marketing-intelligence</u></font></a>", styles['TableCell']),
            Paragraph("<b>Benchmark Architectures:</b> Pandas | MapReduce | Apache Spark", styles['TableCell']),
        ]
    ]
    t_meta = Table(meta_data, colWidths=[261, 262])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 7))

    # Executive Abstract Callout
    abstract_text = (
        "<b>Executive Problem Statement:</b> A high-growth Pakistani direct-to-consumer brand specializing in stitched lawn "
        "pret, festive collections, and university accessories (tote bags, laptop backpacks) currently spends marketing capital across "
        "Facebook, Instagram, Google, TikTok, and YouTube. Management posed the strategic question: <i>'Where should we spend the "
        "next Rs. 1 Million (PKR 1,000,000) to maximize revenue, sustain profitability above the 3.0x break-even target, and acquire "
        "customers at the lowest possible cost?'</i><br/><br/>"
        "This research synthesizes empirical multi-channel advertising performance, non-linear diminishing returns modeling, and an "
        "enterprise-grade Big Data scalability benchmark. The findings recommend allocating <b>35% to Google Ads</b>, <b>30% to Instagram Ads</b>, "
        "<b>20% to Facebook Ads</b>, <b>10% to TikTok Ads</b>, and <b>5% to YouTube Ads</b>, generating a projected <b>Rs. 3.09 Million in gross revenue</b>, "
        "<b>Rs. 2.09 Million in net contribution margin</b>, and <b>1,750 confirmed customer orders</b> at a blended CPA of Rs. 571."
    )
    story.append(make_callout(abstract_text, styles))
    story.append(Spacer(1, 7))

    # Core KPI Cards Table (Fixes font-leading overlap with individual Paragraph flowables)
    def kpi_card(title, val, sub):
        return [
            Paragraph(title, styles['KPITitle']),
            Paragraph(val, styles['KPIVal']),
            Paragraph(sub, styles['KPISub']),
        ]

    kpi_cards = [
        [
            kpi_card("TOTAL AD SPEND", "Rs. 1.0M", "Allocated Capital"),
            kpi_card("PROJECTED SALES", "Rs. 3.09M", "Gross Attributed Sales"),
            kpi_card("NET PROFIT MARGIN", "Rs. 2.09M", "Net After Media Spend"),
            kpi_card("BLENDED ROAS", "3.09x", "Rs. 3.09 per Rs. 1 Spend"),
            kpi_card("CONFIRMED ORDERS", "1,750", "Rs. 571 Blended CPA"),
        ]
    ]
    t_kpis = Table(kpi_cards, colWidths=[104.6]*5)
    t_kpis.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_kpis)
    story.append(Spacer(1, 7))

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
        [Paragraph("<b>Google Ads</b>", styles['TableCell']), Paragraph("35.0%", styles['TableCellCenter']), Paragraph("Rs. 350,000", styles['TableCellCenter']), Paragraph("Rs. 1,247,085", styles['TableCellCenter']), Paragraph("<b>3.56x</b>", styles['TableCellCenter']), Paragraph("Rs. 594", styles['TableCellCenter']), Paragraph("589", styles['TableCellCenter']), Paragraph("Profit Engine (High-Intent Search)", styles['TableCell'])],
        [Paragraph("<b>Instagram Ads</b>", styles['TableCell']), Paragraph("30.0%", styles['TableCellCenter']), Paragraph("Rs. 300,000", styles['TableCellCenter']), Paragraph("Rs. 1,018,957", styles['TableCellCenter']), Paragraph("<b>3.40x</b>", styles['TableCellCenter']), Paragraph("Rs. 455", styles['TableCellCenter']), Paragraph("659", styles['TableCellCenter']), Paragraph("Efficiency Leader (Lowest CPA)", styles['TableCell'])],
        [Paragraph("<b>Facebook Ads</b>", styles['TableCell']), Paragraph("20.0%", styles['TableCellCenter']), Paragraph("Rs. 200,000", styles['TableCellCenter']), Paragraph("Rs. 519,327", styles['TableCellCenter']), Paragraph("<b>2.60x</b>", styles['TableCellCenter']), Paragraph("Rs. 735", styles['TableCellCenter']), Paragraph("272", styles['TableCellCenter']), Paragraph("Cart Recovery & Older Buyers", styles['TableCell'])],
        [Paragraph("<b>TikTok Ads</b>", styles['TableCell']), Paragraph("10.0%", styles['TableCellCenter']), Paragraph("Rs. 100,000", styles['TableCellCenter']), Paragraph("Rs. 218,786", styles['TableCellCenter']), Paragraph("<b>2.19x</b>", styles['TableCellCenter']), Paragraph("Rs. 503", styles['TableCellCenter']), Paragraph("199", styles['TableCellCenter']), Paragraph("Top-Funnel Gen Z Youth Discovery", styles['TableCell'])],
        [Paragraph("<b>YouTube Ads</b>", styles['TableCell']), Paragraph("5.0%", styles['TableCellCenter']), Paragraph("Rs. 50,000", styles['TableCellCenter']), Paragraph("Rs. 86,234", styles['TableCellCenter']), Paragraph("<b>1.72x</b>", styles['TableCellCenter']), Paragraph("Rs. 1,613", styles['TableCellCenter']), Paragraph("31", styles['TableCellCenter']), Paragraph("Unboxing Recall & Retargeting", styles['TableCell'])],
        [Paragraph("<b>TOTAL / BLENDED</b>", styles['TableHead']), Paragraph("<b>100.0%</b>", styles['TableHead']), Paragraph("<b>Rs. 1,000,000</b>", styles['TableHead']), Paragraph("<b>Rs. 3,090,388</b>", styles['TableHead']), Paragraph("<b>3.09x</b>", styles['TableHead']), Paragraph("<b>Rs. 571</b>", styles['TableHead']), Paragraph("<b>1,750</b>", styles['TableHead']), Paragraph("<b>Net Margin: Rs. 2,090,388</b>", styles['TableHead'])],
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
    story.append(Spacer(1, 6))

    # Embed Chart 6: Allocation Donut & Waterfall (sized to 2.1 inches so it fits cleanly)
    p6_path = os.path.join(fig_dir, "06_recommended_budget_allocation_rs1m.png")
    if os.path.exists(p6_path):
        story.append(Image(p6_path, width=7.0*inch, height=2.1*inch))
        story.append(Paragraph("Figure 1: Optimal Ad Budget Allocation Share (%) and Projected Revenue Contribution Waterfall across Channels", styles['CaptionText']))

    # Executive Summary Takeaway Callout (Cleanly sized for Page 2)
    p2_takeaway = (
        "<b>Executive Summary of the Recommended Allocation:</b><br/>"
        "• <b>Google & Instagram capture 65% of the total budget (Rs. 650,000)</b>, generating <b>73% of total customer sales (Rs. 2.27 Million)</b>.<br/>"
        "• <b>Facebook secures 20% (Rs. 200,000)</b> to safeguard against abandoned shopping carts and reach 25–44 family buyers.<br/>"
        "• <b>TikTok is strictly capped at 10% (Rs. 100,000)</b> for low-cost impulse accessories under Rs. 2,500.<br/>"
        "• <b>YouTube is curtailed to 5% (Rs. 50,000)</b> to prevent unprofitable capital bleed while preserving video unboxing reach."
    )
    story.append(make_callout(p2_takeaway, styles))

    story.append(PageBreak())

    # ==========================================================================
    # PAGE 3: PLAIN-ENGLISH PLATFORM ROLES & STRATEGIC SCENARIOS
    # ==========================================================================
    story.append(Paragraph("2. Plain-English Platform Roles & Strategic Scenarios", styles['SecHeader']))
    story.append(Paragraph(
        "To understand why money is allocated this way, here is the real-world role each platform plays in Pakistan, followed "
        "by alternative strategies depending on company priorities:",
        styles['BodyCustom']
    ))

    # Full Plain English Platform Strategy Box
    plain_plat = (
        "<b>Why Did Each Platform Get This Exact Amount of Money?</b><br/>"
        "• <b>Google gets the largest share (Rs. 350,000 / 35%):</b> Think of Google like a shop on Mall Road or Tariq Road where customers "
        "walk in <i>already holding cash in their hands</i> searching for <i>'stitched lawn suit sale'</i> or <i>'canvas laptop tote bag'</i>. "
        "They want to buy right now. That is why Google generates the highest revenue (Rs. 1.25 Million) and healthy 3.56x ROAS.<br/>"
        "• <b>Instagram gets the second largest share (Rs. 300,000 / 30%):</b> Instagram is the ultimate visual fashion catalog. Young Pakistani "
        "women scroll through Reels and look at dress styling and bag aesthetic. It costs only <b>Rs. 455</b> to win a paying customer on Instagram "
        "(the cheapest customer acquisition in Pakistan), producing 659 customer orders.<br/>"
        "• <b>Facebook gets Rs. 200,000 (20%):</b> Facebook acts like a polite shop assistant who taps a customer on the shoulder and says, "
        "<i>'You left a lawn dress in your cart—would you like to complete your order?'</i> It also reaches older family buyers aged 30+.<br/>"
        "• <b>TikTok gets Rs. 100,000 (10%):</b> TikTok is like handing out flyers outside a college campus. Millions of teenagers see the brand "
        "for very little money, but most do not have credit cards. It is strictly used for affordable accessories under Rs. 2,000.<br/>"
        "• <b>YouTube is capped at Rs. 50,000 (5%):</b> People watching YouTube videos want to finish their drama or vlog; they almost never "
        "stop to buy clothes right then. Spending too much on YouTube burns money without bringing direct sales."
    )
    story.append(make_plain_english_box("Understanding Platform Roles in Everyday Terms", plain_plat, styles))
    story.append(Spacer(1, 6))

    # Strategic Scenarios Comparison Table
    story.append(Paragraph("Strategic Scenario Comparison (Evaluating Management Priorities):", styles['SubSecHeader']))
    scenario_data = [
        [Paragraph("<b>Scenario</b>", styles['TableHead']), Paragraph("<b>Spend (PKR)</b>", styles['TableHead']), Paragraph("<b>Projected Revenue</b>", styles['TableHead']), Paragraph("<b>Blended ROAS</b>", styles['TableHead']), Paragraph("<b>Blended CPA</b>", styles['TableHead']), Paragraph("<b>Orders</b>", styles['TableHead']), Paragraph("<b>Net Margin</b>", styles['TableHead'])],
        [Paragraph("<b>Balanced Growth (Recommended)</b>", styles['TableCell']), Paragraph("Rs. 1,000,000", styles['TableCellCenter']), Paragraph("Rs. 3,090,388", styles['TableCellCenter']), Paragraph("<b>3.09x</b>", styles['TableCellCenter']), Paragraph("Rs. 571", styles['TableCellCenter']), Paragraph("1,750", styles['TableCellCenter']), Paragraph("<b>Rs. 2,090,388</b>", styles['TableCellCenter'])],
        [Paragraph("<b>ROAS Maximizer (Squeeze)</b>", styles['TableCell']), Paragraph("Rs. 1,000,000", styles['TableCellCenter']), Paragraph("Rs. 3,385,210", styles['TableCellCenter']), Paragraph("<b>3.39x</b>", styles['TableCellCenter']), Paragraph("Rs. 540", styles['TableCellCenter']), Paragraph("1,852", styles['TableCellCenter']), Paragraph("<b>Rs. 2,385,210</b>", styles['TableCellCenter'])],
        [Paragraph("<b>Aggressive Scale (Volume)</b>", styles['TableCell']), Paragraph("Rs. 1,000,000", styles['TableCellCenter']), Paragraph("Rs. 2,740,150", styles['TableCellCenter']), Paragraph("<b>2.74x</b>", styles['TableCellCenter']), Paragraph("Rs. 495", styles['TableCellCenter']), Paragraph("2,020", styles['TableCellCenter']), Paragraph("<b>Rs. 1,740,150</b>", styles['TableCellCenter'])],
    ]
    t_scen = Table(scenario_data, colWidths=[140, 65, 75, 55, 60, 50, 78])
    t_scen.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), SECONDARY),
        ('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_LIGHT]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_scen)
    story.append(Spacer(1, 5))

    scen_plain = (
        "<b>Scenario Tradeoffs in Plain English:</b><br/>"
        "• <b>Balanced Growth (Recommended):</b> Gives you Rs. 2.09 Million profit while introducing your brand to 1,750 new Pakistani buyers.<br/>"
        "• <b>ROAS Maximizer:</b> Pumps 80% into only Google and Instagram. Squeezes slightly more cash (Rs. 2.38M), but ignores young customers on TikTok.<br/>"
        "• <b>Aggressive Scale:</b> Pumps money into TikTok to chase 2,020 orders. But profit drops to Rs. 1.74M because many clickers don't buy."
    )
    story.append(make_callout(scen_plain, styles))

    story.append(PageBreak())

    # ==========================================================================
    # PAGE 4: PLATFORM PERFORMANCE & UNIT ECONOMICS (100,000 RECORD PROOF)
    # ==========================================================================
    story.append(Paragraph("3. Platform Performance Benchmark & Real Unit Economics", styles['SecHeader']))
    story.append(Paragraph(
        "To eliminate guesswork, we analyzed 100,000 multi-channel marketing interaction logs calibrated to actual Pakistani "
        "consumer buying habits, product baskets (Rs. 1,800 tote bags to Rs. 5,000 lawn suits), and currency auction rates:",
        styles['BodyCustom']
    ))

    # Platform Table
    p_data = [
        [Paragraph("<b>Platform</b>", styles['TableHead']), Paragraph("<b>Total Spend (PKR)</b>", styles['TableHead']), Paragraph("<b>Total Revenue (PKR)</b>", styles['TableHead']), Paragraph("<b>ROAS</b>", styles['TableHead']), Paragraph("<b>CPA (PKR)</b>", styles['TableHead']), Paragraph("<b>CPC (PKR)</b>", styles['TableHead']), Paragraph("<b>CVR %</b>", styles['TableHead']), Paragraph("<b>CTR %</b>", styles['TableHead'])],
        [Paragraph("<b>Google Ads</b>", styles['TableCell']), Paragraph("Rs. 138,332,574", styles['TableCellCenter']), Paragraph("Rs. 639,068,558", styles['TableCellCenter']), Paragraph("<b>4.62x</b>", styles['TableCellCenter']), Paragraph("Rs. 590", styles['TableCellCenter']), Paragraph("Rs. 28.47", styles['TableCellCenter']), Paragraph("4.82%", styles['TableCellCenter']), Paragraph("3.37%", styles['TableCellCenter'])],
        [Paragraph("<b>Instagram Ads</b>", styles['TableCell']), Paragraph("Rs. 120,303,613", styles['TableCellCenter']), Paragraph("Rs. 519,446,716", styles['TableCellCenter']), Paragraph("<b>4.32x</b>", styles['TableCellCenter']), Paragraph("Rs. 449", styles['TableCellCenter']), Paragraph("Rs. 18.13", styles['TableCellCenter']), Paragraph("4.04%", styles['TableCellCenter']), Paragraph("2.58%", styles['TableCellCenter'])],
        [Paragraph("<b>Facebook Ads</b>", styles['TableCell']), Paragraph("Rs. 86,401,197", styles['TableCellCenter']), Paragraph("Rs. 259,803,998", styles['TableCellCenter']), Paragraph("<b>3.01x</b>", styles['TableCellCenter']), Paragraph("Rs. 731", styles['TableCellCenter']), Paragraph("Rs. 21.92", styles['TableCellCenter']), Paragraph("3.00%", styles['TableCellCenter']), Paragraph("1.79%", styles['TableCellCenter'])],
        [Paragraph("<b>TikTok Ads</b>", styles['TableCell']), Paragraph("Rs. 51,905,787", styles['TableCellCenter']), Paragraph("Rs. 124,782,807", styles['TableCellCenter']), Paragraph("<b>2.40x</b>", styles['TableCellCenter']), Paragraph("Rs. 502", styles['TableCellCenter']), Paragraph("Rs. 8.46", styles['TableCellCenter']), Paragraph("1.69%", styles['TableCellCenter']), Paragraph("2.18%", styles['TableCellCenter'])],
        [Paragraph("<b>YouTube Ads</b>", styles['TableCell']), Paragraph("Rs. 35,327,102", styles['TableCellCenter']), Paragraph("Rs. 63,896,396", styles['TableCellCenter']), Paragraph("<b>1.81x</b>", styles['TableCellCenter']), Paragraph("Rs. 1,620", styles['TableCellCenter']), Paragraph("Rs. 31.97", styles['TableCellCenter']), Paragraph("1.97%", styles['TableCellCenter']), Paragraph("1.09%", styles['TableCellCenter'])],
        [Paragraph("<b>BLENDED TOTAL</b>", styles['TableHead']), Paragraph("<b>Rs. 432,270,273</b>", styles['TableHead']), Paragraph("<b>Rs. 1,606,998,475</b>", styles['TableHead']), Paragraph("<b>3.72x</b>", styles['TableHead']), Paragraph("<b>Rs. 580</b>", styles['TableHead']), Paragraph("<b>Rs. 19.06</b>", styles['TableHead']), Paragraph("<b>3.29%</b>", styles['TableHead']), Paragraph("<b>2.26%</b>", styles['TableHead'])],
    ]
    t_plat = Table(p_data, colWidths=[78, 75, 80, 45, 55, 55, 45, 45])
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
    story.append(Spacer(1, 5))

    # Dual Visuals: Chart 1 & Chart 2 side by side (height 1.8 inches)
    p1_path = os.path.join(fig_dir, "01_cac_cpa_by_platform.png")
    p2_path = os.path.join(fig_dir, "02_roas_vs_breakeven_benchmark.png")
    
    if os.path.exists(p1_path) and os.path.exists(p2_path):
        img_table = Table([[
            Image(p1_path, width=3.55*inch, height=1.85*inch),
            Image(p2_path, width=3.55*inch, height=1.85*inch)
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
        "<b>Why is 3.0x ROAS the Magic Break-Even Line in Pakistani E-Commerce?</b><br/>"
        "Take a typical <b>Rs. 3,000 stitched lawn suit</b> sold online:<br/>"
        "• <b>Fabric, Lace & Stitching (COGS):</b> Rs. 1,050 (35% of price)<br/>"
        "• <b>Courier Delivery & Cash-Collection Fee:</b> Rs. 350 (12% of price)<br/>"
        "• <b>Packaging & Warehouse Labor:</b> Rs. 200 (7% of price)<br/>"
        "• <b>Return-to-Origin (RTO) buffer (for packages customers reject):</b> Rs. 400 (13% of price)<br/>"
        "• <b>Target Net Profit:</b> Rs. 1,000 (33% of price)<br/>"
        "This means you can only afford to spend a maximum of <b>Rs. 1,000 on advertising</b> to acquire that customer. "
        "Rs. 3,000 divided by Rs. 1,000 = <b>3.0x ROAS</b>. If your ad ROAS drops below 3.0x (like YouTube at 1.81x or TikTok at 2.40x), "
        "your fabric and courier costs eat up all the money, and your business bleeds cash on every shipment!"
    )
    story.append(make_plain_english_box("The Real Economics of a Pakistani E-Commerce Order", breakeven_text, styles))

    story.append(PageBreak())

    # ==========================================================================
    # PAGE 5: THE BIG DATA CHALLENGE - PANDAS VS. MAPREDUCE VS. SPARK
    # ==========================================================================
    story.append(Paragraph("4. Big Data Framework Scalability Benchmark (10K to 10M Records)", styles['SecHeader']))
    story.append(Paragraph(
        "To test how enterprise data architectures survive when an e-commerce brand scales from thousands to millions of customer "
        "interactions, we executed a standardized aggregation workload (`GroupBy (platform, city)` with metric projection) across 4 tiers:",
        styles['BodyCustom']
    ))

    # Benchmark Table
    bench_table_data = [
        [Paragraph("<b>Data Tier</b>", styles['TableHead']), Paragraph("<b>Records</b>", styles['TableHead']), Paragraph("<b>Engine Framework</b>", styles['TableHead']), Paragraph("<b>Execution Time (s)</b>", styles['TableHead']), Paragraph("<b>Peak Memory (MB)</b>", styles['TableHead']), Paragraph("<b>Throughput (rec/s)</b>", styles['TableHead'])],
        [Paragraph("10K", styles['TableCellCenter']), Paragraph("10,000", styles['TableCellCenter']), Paragraph("Pandas", styles['TableCell']), Paragraph("0.007s", styles['TableCellCenter']), Paragraph("0.7 MB", styles['TableCellCenter']), Paragraph("1,513,298", styles['TableCellCenter'])],
        [Paragraph("10K", styles['TableCellCenter']), Paragraph("10,000", styles['TableCellCenter']), Paragraph("MapReduce", styles['TableCell']), Paragraph("0.383s", styles['TableCellCenter']), Paragraph("2.8 MB", styles['TableCellCenter']), Paragraph("26,090", styles['TableCellCenter'])],
        [Paragraph("10K", styles['TableCellCenter']), Paragraph("10,000", styles['TableCellCenter']), Paragraph("Apache Spark", styles['TableCell']), Paragraph("0.030s", styles['TableCellCenter']), Paragraph("0.9 MB", styles['TableCellCenter']), Paragraph("329,993", styles['TableCellCenter'])],
        [Paragraph("100K", styles['TableCellCenter']), Paragraph("100,000", styles['TableCellCenter']), Paragraph("Pandas", styles['TableCell']), Paragraph("0.016s", styles['TableCellCenter']), Paragraph("6.0 MB", styles['TableCellCenter']), Paragraph("6,415,157", styles['TableCellCenter'])],
        [Paragraph("100K", styles['TableCellCenter']), Paragraph("100,000", styles['TableCellCenter']), Paragraph("MapReduce", styles['TableCell']), Paragraph("0.507s", styles['TableCellCenter']), Paragraph("25.3 MB", styles['TableCellCenter']), Paragraph("197,250", styles['TableCellCenter'])],
        [Paragraph("100K", styles['TableCellCenter']), Paragraph("100,000", styles['TableCellCenter']), Paragraph("Apache Spark", styles['TableCell']), Paragraph("0.042s", styles['TableCellCenter']), Paragraph("7.6 MB", styles['TableCellCenter']), Paragraph("2,373,175", styles['TableCellCenter'])],
        [Paragraph("1M", styles['TableCellCenter']), Paragraph("1,000,000", styles['TableCellCenter']), Paragraph("Pandas", styles['TableCell']), Paragraph("0.119s", styles['TableCellCenter']), Paragraph("71.4 MB", styles['TableCellCenter']), Paragraph("8,401,972", styles['TableCellCenter'])],
        [Paragraph("1M", styles['TableCellCenter']), Paragraph("1,000,000", styles['TableCellCenter']), Paragraph("MapReduce", styles['TableCell']), Paragraph("2.431s", styles['TableCellCenter']), Paragraph("252.8 MB", styles['TableCellCenter']), Paragraph("411,309", styles['TableCellCenter'])],
        [Paragraph("1M", styles['TableCellCenter']), Paragraph("1,000,000", styles['TableCellCenter']), Paragraph("Apache Spark", styles['TableCell']), Paragraph("0.164s", styles['TableCellCenter']), Paragraph("76.8 MB", styles['TableCellCenter']), Paragraph("6,096,081", styles['TableCellCenter'])],
        [Paragraph("<b>10M</b>", styles['TableCellCenter']), Paragraph("10,000,000", styles['TableCellCenter']), Paragraph("<b>Pandas</b>", styles['TableCell']), Paragraph("<b>1.119s</b>", styles['TableCellCenter']), Paragraph("71.4 MB", styles['TableCellCenter']), Paragraph("<b>8,935,487</b>", styles['TableCellCenter'])],
        [Paragraph("<b>10M</b>", styles['TableCellCenter']), Paragraph("10,000,000", styles['TableCellCenter']), Paragraph("<b>MapReduce</b>", styles['TableCell']), Paragraph("<b>23.167s</b>", styles['TableCellCenter']), Paragraph("252.9 MB", styles['TableCellCenter']), Paragraph("431,640", styles['TableCellCenter'])],
        [Paragraph("<b>10M</b>", styles['TableCellCenter']), Paragraph("10,000,000", styles['TableCellCenter']), Paragraph("<b>Apache Spark</b>", styles['TableCell']), Paragraph("<b>1.659s</b>", styles['TableCellCenter']), Paragraph("76.8 MB", styles['TableCellCenter']), Paragraph("<b>6,027,594</b>", styles['TableCellCenter'])],
    ]
    t_bench = Table(bench_table_data, colWidths=[55, 75, 95, 85, 95, 118])
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
    story.append(Spacer(1, 5))

    # Dual Visuals: Chart 3 & Chart 4 side by side (height 1.85 inches)
    p3_path = os.path.join(fig_dir, "03_big_data_execution_time_benchmark.png")
    p4_path = os.path.join(fig_dir, "04_big_data_memory_throughput_benchmark.png")
    if os.path.exists(p3_path) and os.path.exists(p4_path):
        img_table2 = Table([[
            Image(p3_path, width=3.55*inch, height=1.85*inch),
            Image(p4_path, width=3.55*inch, height=1.85*inch)
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
        "<b>The Vehicle Analogy: Understanding Pandas vs. MapReduce vs. Spark</b><br/>"
        "• <b>Pandas is like a Ferrari Sports Car:</b> It is ridiculously fast for small trips. If you have 10,000 or 100,000 rows on your laptop, "
        "Pandas finishes in 0.01 seconds. But a Ferrari has no trunk space! As soon as your company gets 50 million rows, Pandas runs out of memory "
        "and crashes completely (the famous 'Out of Memory' crash).<br/>"
        "• <b>MapReduce is like a Fleet of Heavy Cargo Trucks:</b> It divides a massive mountain of data into little boxes and carries them across "
        "multiple computers. It will NEVER crash, even with 100 billion rows! But it is slow (took 23 seconds for 10M rows) because the trucks have "
        "to stop at every weigh station and write data to hard disks.<br/>"
        "• <b>Apache Spark is like a High-Speed Electric Bullet Train:</b> It connects multiple carriages together (so it never runs out of space) "
        "while keeping all data in ultra-fast RAM memory (like Pandas). That is why Spark chewed through 10 Million rows in only "
        "<b>1.65 seconds</b> at 6 Million records per second. It is the enterprise gold standard."
    )
    story.append(make_plain_english_box("Why Big Data Architecture Matters: The Vehicle Analogy", car_analogy, styles))

    story.append(PageBreak())

    # ==========================================================================
    # PAGE 6: WHY NOT PUT ALL MONEY ON GOOGLE? DIMINISHING RETURNS & FUNNEL
    # ==========================================================================
    story.append(Paragraph("5. Customer Fatigue, Diminishing Returns & The Conversion Funnel", styles['SecHeader']))
    story.append(Paragraph(
        "A common question asked by company executives is: <i>'If Google has the highest ROAS (4.62x), why don't we put all Rs. 1 Million into Google?'</i> "
        "The answer lies in two universal marketing realities: <b>Audience Saturation</b> and <b>Funnel Drop-offs</b>.",
        styles['BodyCustom']
    ))

    # Dual Visuals: Chart 7 & Chart 5 side by side (height 2.0 inches)
    p7_path = os.path.join(fig_dir, "07_diminishing_returns_marginal_roas.png")
    p5_path = os.path.join(fig_dir, "05_conversion_funnel_by_platform.png")
    if os.path.exists(p7_path) and os.path.exists(p5_path):
        img_table3 = Table([[
            Image(p7_path, width=3.55*inch, height=2.0*inch),
            Image(p5_path, width=3.55*inch, height=2.0*inch)
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
        "• Your first Rs. 100,000 captures those ready-to-buy customers at a massive <b>4.62x ROAS</b>.<br/>"
        "• But if you force Rs. 1,000,000 into Google in 30 days, Google starts showing your ads to people who aren't interested, or shows "
        "the same ad 15 times to the same person. The person gets annoyed (ad fatigue) and stops clicking.<br/>"
        "• Look at Figure 4 (Left): As spend climbs toward Rs. 1 Million on a single channel, the extra revenue per Rupee collapses down to 1.8x. "
        "By distributing the budget into Instagram (Rs. 300K) and Facebook (Rs. 200K), you catch customers at their highest enjoyment point on every app!"
    )
    story.append(make_plain_english_box("Understanding Diminishing Returns with a Simple Analogy", buffet_analogy, styles))
    story.append(Spacer(1, 5))

    # Funnel Explanation Box
    funnel_text = (
        "<b>Where do Pakistani customers disappear in the funnel? (Figure 4 Right)</b><br/>"
        "• <b>Impressions (Top Bar):</b> Millions of people glance at your ad while scrolling. TikTok generates 6.1 Million views easily.<br/>"
        "• <b>Clicks (Middle Bar):</b> Out of 100 people who see the ad, only 2 to 3 people tap on it (CTR). TikTok gets huge clicks because it is cheap.<br/>"
        "• <b>Conversions / Orders (Bottom Bar):</b> This is where the truth comes out! Out of all those clicks, Google converts 4.8% and Instagram "
        "converts 4.0% into paying deliveries, while TikTok converts only 1.7%. That is why Google and Instagram produce the thickest order bars."
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
        [Paragraph("<b>Karachi</b>", styles['TableCell']), Paragraph("35.0%", styles['TableCellCenter']), Paragraph("Rs. 350,000", styles['TableCellCenter']), Paragraph("Mega-city e-commerce hub; highest COD order density and lowest transit failure rate.", styles['TableCell'])],
        [Paragraph("<b>Lahore</b>", styles['TableCell']), Paragraph("28.0%", styles['TableCellCenter']), Paragraph("Rs. 280,000", styles['TableCellCenter']), Paragraph("Cultural fashion capital; highest demand for stitched lawn pret & designer unstitched.", styles['TableCell'])],
        [Paragraph("<b>Islamabad / Rawalpindi</b>", styles['TableCell']), Paragraph("21.0%", styles['TableCellCenter']), Paragraph("Rs. 210,000", styles['TableCellCenter']), Paragraph("Highest purchasing power per capita and largest average order values (AOV).", styles['TableCell'])],
        [Paragraph("<b>Faisalabad</b>", styles['TableCell']), Paragraph("6.0%", styles['TableCellCenter']), Paragraph("Rs. 60,000", styles['TableCellCenter']), Paragraph("Textile hub; strong response to clearance promotions and daily essentials.", styles['TableCell'])],
        [Paragraph("<b>Multan & South Punjab</b>", styles['TableCell']), Paragraph("5.0%", styles['TableCellCenter']), Paragraph("Rs. 50,000", styles['TableCellCenter']), Paragraph("Rapidly growing tier-2 festive wear and university tote bag adoption.", styles['TableCell'])],
        [Paragraph("<b>Peshawar & KPK</b>", styles['TableCell']), Paragraph("3.0%", styles['TableCellCenter']), Paragraph("Rs. 30,000", styles['TableCellCenter']), Paragraph("Selective premium formal demand.", styles['TableCell'])],
        [Paragraph("<b>Other Tier-2 Hubs</b>", styles['TableCell']), Paragraph("2.0%", styles['TableCellCenter']), Paragraph("Rs. 20,000", styles['TableCellCenter']), Paragraph("Emerging regional testing (Sialkot, Gujranwala, Quetta).", styles['TableCell'])],
        [Paragraph("<b>TOTAL</b>", styles['TableHead']), Paragraph("<b>100.0%</b>", styles['TableHead']), Paragraph("<b>Rs. 1,000,000</b>", styles['TableHead']), Paragraph("<b>Concentrates 84% of spend in Tier-1 logistics hubs.</b>", styles['TableHead'])],
    ]
    t_city = Table(city_data, colWidths=[105, 45, 75, 298])
    t_city.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('BACKGROUND', (0,-1), (-1,-1), DARK_BG),
        ('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, BG_LIGHT]),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(t_city)
    story.append(Spacer(1, 5))

    # Embed Chart 8: Regional City Revenue Efficiency Matrix (height 2.0 inches)
    p8_path = os.path.join(fig_dir, "08_city_revenue_efficiency_matrix.png")
    if os.path.exists(p8_path):
        story.append(Image(p8_path, width=7.0*inch, height=2.0*inch))
        story.append(Paragraph("Figure 5: Regional City Revenue vs. ROAS Efficiency Matrix across Pakistani Urban Hubs", styles['CaptionText']))

    # Plain English COD and RTO Explanation Box
    cod_text = (
        "<b>The Hidden Enemy of Pakistani E-Commerce: Return to Origin (RTO)</b><br/>"
        "Why did our model allocate <b>84% of the advertising money into Karachi, Lahore, and Islamabad/Rawalpindi</b>?<br/>"
        "• When an online customer in Karachi orders a lawn dress on Cash on Delivery, the courier rider delivers it in 24–48 hours. "
        "The customer remembers ordering it, pays the cash, and the delivery success rate is <b>over 88% to 90%</b>.<br/>"
        "• But when an ad runs in remote towns or distant villages, shipping takes 5 to 7 days. By the time the rider shows up, "
        "the customer has changed their mind, doesn't have the cash, or refuses the door. The parcel returns back to the warehouse.<br/>"
        "• When a parcel bounces (RTO), <b>the brand loses money twice</b>: You paid Rs. 350 to send the package, another Rs. 200 for the return courier, "
        "and you already burned Rs. 500 on the Facebook ad! Spending ad money in weak courier zones silently bankrupts Pakistani brands.<br/>"
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

    # Dual Visuals: Chart 9 & Chart 10 side by side (height 2.0 inches)
    p9_path = os.path.join(fig_dir, "09_demographic_age_gender_performance.png")
    p10_path = os.path.join(fig_dir, "10_monthly_spend_revenue_profit_trend.png")
    if os.path.exists(p9_path) and os.path.exists(p10_path):
        img_table4 = Table([[
            Image(p9_path, width=3.55*inch, height=2.0*inch),
            Image(p10_path, width=3.55*inch, height=2.0*inch)
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
        "• <b>Who Buys (Figure 6 Left):</b> Female consumers aged <b>18 to 34 represent 72% of all orders</b> and generate the highest ROAS (4.4x). "
        "Young university women (18–24) drive massive volume for tote bags and casual stitched pret under Rs. 2,500. "
        "Working professionals and young mothers (25–34) command the highest basket sizes (buying 3-piece unstitched and festive lawn). "
        "Male buyers represent only 28% of transactions, primarily purchasing gifts before Eid or buying men's kurtas during festive campaigns.<br/>"
        "• <b>When They Buy (Figure 6 Right): The 4 Seasonal Waves of Pakistani E-Commerce:</b><br/>"
        "1. <b>Wave 1 — Spring Lawn Launch (February/March):</b> Brands release new seasonal catalogs. Consumers actively browse; high CTRs.<br/>"
        "2. <b>Wave 2 — Ramadan & Eid-ul-Fitr (April/May):</b> The biggest sales boom of the year! Revenue spikes by over <b>+140%</b>. "
        "Advertising budgets should be increased by 50% during the second and third weeks of Ramadan to capture Eid wardrobe shopping.<br/>"
        "3. <b>Wave 3 — Blessed Friday / 11.11 (November):</b> The massive clearance festival where shoppers hunt for heavy discounts.<br/>"
        "4. <b>Wave 4 — Winter Wedding Season (December/January):</b> Demand shifts toward velvet, shawls, and premium party wear."
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
        [Paragraph("<b>Timeframe</b>", styles['TableHead']), Paragraph("<b>Operational Milestones & Action Items (What To Do Tomorrow)</b>", styles['TableHead'])],
        [Paragraph("<b>Week 1</b><br/>Spend Rebalance", styles['TableCell']), Paragraph("<b>Cap YouTube immediately:</b> Cut YouTube direct spend to 5% (Rs. 50,000) and turn off non-converting video campaigns.<br/><b>Fund the Profit Engines:</b> Reallocate Rs. 350,000 into Google Shopping / Search and Rs. 300,000 into Instagram Reels showcasing product videos.", styles['TableCell'])],
        [Paragraph("<b>Week 2</b><br/>Creative & Pricing Fix", styles['TableCell']), Paragraph("<b>Eliminate 'Check DM for Price':</b> As discovered in Phase 1, hiding prices in DMs kills checkout conversions by 34%. Put clear prices (e.g., <i>'Rs. 2,499 with Free Cash on Delivery'</i>) right in the ad image and headline to boost click-to-order rates.", styles['TableCell'])],
        [Paragraph("<b>Week 3</b><br/>Logistics Safeguards", styles['TableCell']), Paragraph("<b>Protect Cash Flow:</b> Apply +20% bid adjustments to Karachi, Lahore, and Islamabad. Set up automated WhatsApp order confirmation messages before shipping to reduce courier return (RTO) rates to under 10%.", styles['TableCell'])],
        [Paragraph("<b>Week 4</b><br/>Automated Big Data", styles['TableCell']), Paragraph("<b>Deploy Automated Pipelines:</b> Integrate queries.sql into daily BigQuery/Snowflake warehouses. Run the budget allocation script (scripts/04_budget_recommendation_engine.py) weekly to automatically shift money to whichever ad is winning.", styles['TableCell'])],
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
    story.append(Spacer(1, 5))

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
        "&nbsp;&nbsp;&nbsp;&nbsp;<font color='#01696F'>WHEN</font> roas &gt;= 3.50 <font color='#01696F'>THEN</font> 'INCREASE BUDGET (+15% to +35%) - HIGH EFFICIENCY'<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<font color='#01696F'>WHEN</font> roas &gt;= 3.00 <font color='#01696F'>THEN</font> 'MAINTAIN / OPTIMIZE'<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<font color='#01696F'>ELSE</font> 'REDUCE BUDGET (-30% to -50%) - UNDERPERFORMING'<br/>"
        "&nbsp;&nbsp;<font color='#01696F'>END AS</font> budget_recommendation<br/>"
        "<font color='#01696F'>FROM</font> channel_perf <font color='#01696F'>ORDER BY</font> roas <font color='#01696F'>DESC</font>;"
    )
    t_sql = Table([[Paragraph(sql_code, styles['TableCell'])]], colWidths=[523])
    t_sql.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFB')),
        ('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_sql)
    story.append(Spacer(1, 5))

    # Plain English SQL explanation
    sql_plain = (
        "<b>What is this SQL code doing in simple terms?</b> This automated script constantly monitors all five advertising platforms. "
        "If Google or Instagram is hitting a ROAS over 3.5x, it flags to management: <i>'Pump more money in!'</i> If YouTube or TikTok falls "
        "below the 3.0x break-even line, it flags: <i>'Cut spend immediately!'</i> This prevents human error and stops marketing teams from burning money."
    )
    story.append(make_plain_english_box("Automated Safety Switch", sql_plain, styles))
    story.append(Spacer(1, 5))

    # Concluding Sign-off Box
    signoff = Paragraph(
        "<b>Report Prepared by:</b> Zughaina — Senior Marketing Data Analyst<br/>"
        "<b>Phase 2 GitHub Repository:</b> <a href='https://github.com/zughaina3/pakistan-digital-advertising-budget-optimizer'><font color='#01696F'><u>https://github.com/zughaina3/pakistan-digital-advertising-budget-optimizer</u></font></a><br/>"
        "<b>Phase 1 Portfolio Link:</b> <a href='https://github.com/zughaina3/pakistan-digital-marketing-intelligence'><font color='#01696F'><u>https://github.com/zughaina3/pakistan-digital-marketing-intelligence</u></font></a><br/>"
        "<b>Data Architecture:</b> Fully verified across 10,000,000 records using Apache Spark & Pandas on multi-core architecture.",
        styles['CalloutBox']
    )
    t_sign = Table([[signoff]], colWidths=[523])
    t_sign.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 1, PRIMARY),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
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
