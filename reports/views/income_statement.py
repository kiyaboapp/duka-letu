from django.http import HttpResponse
from django.shortcuts import render
from reports.views.base import BaseReportView
from reports.services.accounting import AccountingService
from reports.services.expenses import ExpenseService
from decimal import Decimal


class IncomeStatementView(BaseReportView):
    template_name = 'reports/income_statement.html'
    default_preset = 'this_month'

    def get_context(self, request, period):
        acct = AccountingService(period.start, period.end)
        data = acct.to_income_statement()
        return {'data': data}

    def get(self, request):
        from reports.forms import ReportPeriodForm
        from reports.periods import ReportPeriod
        form = ReportPeriodForm(request.GET or None)
        period = form.resolved_period(self.default_preset) if form.is_valid() else ReportPeriod.resolve(default_preset=self.default_preset)
        ctx = self.get_context(request, period)
        ctx['form'] = form
        ctx['period'] = period
        if request.GET.get('format') == 'pdf':
            return self._render_pdf(ctx, period)
        return render(request, self.template_name, ctx)

    def _render_pdf(self, ctx, period):
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        import io
        from datetime import datetime

        data = ctx['data']
        buf = io.BytesIO()

        # Brand Color: Indigo
        BRAND = colors.Color(79/255, 70/255, 229/255)
        LIGHT_BG = colors.Color(248/255, 250/255, 252/255)

        # ── Header & Footer ───────────────────────────────────────────────────
        def header_footer(canvas, doc):
            canvas.saveState()
            # Indigo Letterhead stylized box
            canvas.setFillColor(BRAND)
            canvas.rect(2*cm, A4[1]-2.5*cm, 0.4*cm, 1.2*cm, fill=1, stroke=0)

            canvas.setFont('Helvetica-Bold', 16)
            canvas.setFillColor(colors.black)
            canvas.drawString(2.6*cm, A4[1]-1.8*cm, "Upendo Stationery")

            canvas.setFont('Helvetica', 9)
            canvas.setFillColor(colors.grey)
            canvas.drawString(2.6*cm, A4[1]-2.2*cm, "Stationery, Office Supplies & General Supplies | Dar es Salaam, Tanzania")

            # Decorative line
            canvas.setStrokeColor(BRAND)
            canvas.setLineWidth(1.5)
            canvas.line(2*cm, A4[1]-2.8*cm, A4[0]-2*cm, A4[1]-2.8*cm)

            # Footer
            canvas.setFont('Helvetica-Oblique', 8)
            canvas.setFillColor(colors.grey)
            canvas.drawString(2*cm, 1*cm, f"Accountant's Report | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            canvas.drawRightString(A4[0]-2*cm, 1*cm, f"Page {doc.page}")
            canvas.restoreState()

        doc = SimpleDocTemplate(
            buf, 
            pagesize=A4, 
            topMargin=3.5*cm, 
            bottomMargin=2*cm, 
            leftMargin=2*cm, 
            rightMargin=2*cm
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('Title', parent=styles['Heading1'], alignment=0, fontSize=14, spaceAfter=2, textColor=BRAND)
        subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'], alignment=0, fontSize=9, textColor=colors.grey)

        bold = ParagraphStyle('Bold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10)
        right_bold = ParagraphStyle('RightBold', parent=bold, alignment=2)
        normal = ParagraphStyle('Normal', parent=styles['Normal'], fontSize=10)
        right_normal = ParagraphStyle('RightNormal', parent=normal, alignment=2)
        indent = ParagraphStyle('Indent', parent=normal, leftIndent=12)

        def fmt(v):
            return f"{v:,.0f}" if v >= 0 else f"({abs(v):,.0f})"

        elements = []
        elements.append(Paragraph("INCOME STATEMENT", title_style))
        elements.append(Paragraph(f"For the period ended {period.end.strftime('%d %B %Y')}", subtitle_style))
        elements.append(Spacer(1, 0.6*cm))

        # ── Financial Highlights Box ──────────────────────────────────────────
        margin_style = ParagraphStyle('Margin', parent=normal, fontSize=8, textColor=colors.grey)
        
        net_sales = data['net_sales']
        gross_profit = data['gross_profit']
        net_profit = data['net_profit']
        
        gross_margin_pct = (gross_profit / net_sales * 100).quantize(Decimal('0.1')) if net_sales else Decimal('0')
        net_margin_pct = (net_profit / net_sales * 100).quantize(Decimal('0.1')) if net_sales else Decimal('0')

        summary_data = [
            [Paragraph("NET SALES", margin_style), Paragraph("GROSS MARGIN", margin_style), Paragraph("NET PROFIT", margin_style)],
            [Paragraph(fmt(net_sales), bold), Paragraph(f"{gross_margin_pct}%", bold), Paragraph(fmt(net_profit), bold)]
        ]
        summary_table = Table(summary_data, colWidths=[5.6*cm, 5.7*cm, 5.7*cm])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), LIGHT_BG),
            ('BOX', (0,0), (-1,-1), 0.5, BRAND),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 1*cm))

        # ── Accounting Table Structure (Description | Details | Total) ────────
        rows = []
        # Header Row
        rows.append([Paragraph('DESCRIPTION', bold), Paragraph('DETAILS', right_bold), Paragraph('TOTAL (TZS)', right_bold)])
        rows.append(['', '', ''])

        # Section: Revenue
        rows.append([Paragraph('REVENUE', bold), '', ''])
        rows.append([Paragraph('Direct Sales', indent), fmt(data['direct_sales']), ''])
        rows.append([Paragraph('Credit Sales', indent), fmt(data['credit_sales']), ''])
        rows.append([Paragraph('Less: Returns Inward', indent), f"({fmt(data['return_inwards'])})", ''])
        rows.append([Paragraph('Net Sales Revenue', bold), '', Paragraph(fmt(data['net_sales']), right_bold)])
        rows.append(['', '', ''])

        # Section: COGS
        rows.append([Paragraph('COST OF GOODS SOLD', bold), '', ''])
        rows.append([Paragraph('Opening Stock', indent), fmt(data['opening_stock']), ''])
        rows.append([Paragraph('Add: Purchases', indent), fmt(data['purchases']), ''])
        rows.append([Paragraph('Less: Returns Outward', indent), f"({fmt(data['return_outwards'])})", ''])
        rows.append([Paragraph('Total Cost of Goods Available', indent), fmt(data['cogas']), ''])
        rows.append([Paragraph('Less: Closing Stock', indent), f"({fmt(data['closing_stock'])})", ''])
        rows.append([Paragraph('Cost of Goods Sold', bold), '', Paragraph(fmt(data['cogs']), right_bold)])
        rows.append(['', '', ''])

        # Gross Profit
        rows.append([Paragraph('GROSS PROFIT', bold), '', Paragraph(fmt(data['gross_profit']), right_bold)])
        rows.append(['', '', ''])

        # Section: Expenses
        rows.append([Paragraph('OPERATING EXPENSES', bold), '', ''])
        
        expense_start_row = len(rows)
        for name, amount in data.get('expense_lines', {}).items():
            rows.append([Paragraph(name, indent), fmt(amount), ''])
        expense_end_row = len(rows) - 1

        rows.append([Paragraph('Total Operating Expenses', bold), '', Paragraph(fmt(data['total_expenses']), right_bold)])
        rows.append(['', '', ''])

        # Net Profit with specialized double underline rows
        rows.append([Paragraph('NET PROFIT / (LOSS)', bold), '', Paragraph(fmt(data['net_profit']), right_bold)])
        rows.append(['', '', '']) # Tiny row for the second line of the double-underline

        # Column widths: Description (9cm), Details (4cm), Totals (4cm)
        t = Table(rows, colWidths=[9*cm, 4*cm, 4*cm])

        # Build Table Style dynamically based on row indices
        ts = TableStyle([
            ('FONT', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),

            # Header line
            ('LINEBELOW', (0,0), (-1,0), 1.5, BRAND),

            # Subtle section background shading
            ('BACKGROUND', (0,2), (-1,2), LIGHT_BG), # Revenue Header
            ('BACKGROUND', (0,8), (-1,8), LIGHT_BG), # COGS Header
            ('BACKGROUND', (0,17), (-1,17), LIGHT_BG), # Expenses Header

            # Accounting Underlines (Details column)
            ('LINEBELOW', (1,5), (1,5), 0.5, colors.black), # Below Returns Inward
            ('LINEBELOW', (1,11), (1,11), 0.5, colors.black), # Below Returns Outward
            ('LINEBELOW', (1,13), (1,13), 0.5, colors.black), # Below Closing Stock

            # Main Totals Underlines (Total column)
            ('LINEBELOW', (2,6), (2,6), 1, colors.black), # Net Sales
            ('LINEBELOW', (2,14), (2,14), 1, colors.black), # COGS
            ('LINEBELOW', (2,16), (2,16), 1, colors.black), # Gross Profit
            ('LINEBELOW', (2,-3), (2,-3), 1, colors.black), # Total Expenses

            # ── PROFESSIONAL DOUBLE UNDERLINE ──
            ('LINEBELOW', (2, -2), (2, -2), 0.5, colors.black), # First line
            ('LINEBELOW', (2, -1), (2, -1), 0.5, colors.black), # Second line
        ])
        
        # Alternating row colors for expenses
        for i in range(expense_start_row, expense_end_row + 1):
            if i % 2 == 0:
                ts.add('BACKGROUND', (0, i), (-1, i), colors.Color(250/255, 251/255, 253/255))

        # Set height of the tiny row at the bottom to create the double-underline gap
        t._argH[-1] = 0.1*cm 

        t.setStyle(ts)
        elements.append(t)
        
        # ── Signature Block ───────────────────────────────────────────────────
        elements.append(Spacer(1, 2*cm))
        sig_data = [
            [Paragraph("__________________________", normal), "", Paragraph("__________________________", normal)],
            [Paragraph("Prepared By (Accountant)", normal), "", Paragraph("Authorized By (Management)", normal)],
            [Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d')}", normal), "", Paragraph("Date: ____________________", normal)]
        ]
        sig_table = Table(sig_data, colWidths=[7*cm, 3*cm, 7*cm])
        sig_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('TOPPADDING', (0,0), (-1,-1), 10),
        ]))
        elements.append(sig_table)

        doc.build(elements, onFirstPage=header_footer, onLaterPages=header_footer)

        buf.seek(0)
        resp = HttpResponse(buf, content_type='application/pdf')
        resp['Content-Disposition'] = f'attachment; filename="income_statement_{period.end}.pdf"'
        return resp

