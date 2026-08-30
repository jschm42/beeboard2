"""PDF Generation Service for BeeBoard Bestandsbuch (Treatment register)."""

import io
from datetime import date, datetime
from typing import List, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
)

from app.models.treatment import Treatment


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and draw total page count (Seite X von Y)."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count: int):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))

        # Footer line
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(15 * mm, 12 * mm, landscape(A4)[0] - 15 * mm, 12 * mm)

        # Footer texts
        footer_text_left = "BeeBoard — Bestandsbuch über die Anwendung von Arzneimitteln"
        page_text = f"Seite {self._pageNumber} von {page_count}"
        
        self.drawString(15 * mm, 8 * mm, footer_text_left)
        self.drawRightString(landscape(A4)[0] - 15 * mm, 8 * mm, page_text)
        self.restoreState()


def format_date_str(d: Optional[date]) -> str:
    if not d:
        return ""
    return d.strftime("%d.%m.%Y")


def format_period_str(start_d: Optional[date], end_d: Optional[date]) -> str:
    if not start_d:
        return "-"
    if not end_d or end_d == start_d:
        return format_date_str(start_d)
    return f"{format_date_str(start_d)} – {format_date_str(end_d)}"


def generate_bestandsbuch_pdf(
    treatments: List[Treatment],
    apiary_name: str,
    beekeeper_name: str,
    location_name: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> bytes:
    """Generates an official Bestandsbuch PDF report in A4 Landscape format."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=15 * mm,
        rightMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=18 * mm
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=17,
        textColor=colors.HexColor("#1e293b")
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#64748b")
    )
    meta_label = ParagraphStyle(
        'MetaLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#475569")
    )
    meta_val = ParagraphStyle(
        'MetaVal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#0f172a")
    )
    table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.white,
        alignment=0
    )
    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor("#1e293b")
    )
    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor("#0f172a")
    )
    table_cell_mono = ParagraphStyle(
        'TableCellMono',
        parent=styles['Normal'],
        fontName='Courier-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor("#b45309")
    )
    legal_style = ParagraphStyle(
        'LegalStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#334155")
    )

    story = []

    # 1. Header & Title
    story.append(Paragraph("Bestandsbuch über die Anwendung von Tierarzneimitteln bei Bienen", title_style))
    story.append(Paragraph("Nachweis gemäß Tierarzneimittel-Nachweisverordnung (TAMV) / Behandlungsjournal", subtitle_style))
    story.append(Spacer(1, 4 * mm))

    # 2. Meta Info Box
    period_display = "Gesamter Zeitraum"
    if start_date and end_date:
        period_display = f"{format_date_str(start_date)} bis {format_date_str(end_date)}"
    elif start_date:
        period_display = f"Ab {format_date_str(start_date)}"
    elif end_date:
        period_display = f"Bis {format_date_str(end_date)}"

    meta_data = [
        [
            Paragraph("<b>Imkerei:</b>", meta_label), Paragraph(apiary_name or "-", meta_val),
            Paragraph("<b>Standort:</b>", meta_label), Paragraph(location_name or "Alle Standorte", meta_val),
        ],
        [
            Paragraph("<b>Inhaber / Imker:</b>", meta_label), Paragraph(beekeeper_name or "-", meta_val),
            Paragraph("<b>Berichtszeitraum:</b>", meta_label), Paragraph(period_display, meta_val),
        ],
        [
            Paragraph("<b>Erstellungsdatum:</b>", meta_label), Paragraph(datetime.now().strftime("%d.%m.%Y %H:%M Uhr"), meta_val),
            Paragraph("<b>Einträge:</b>", meta_label), Paragraph(f"{len(treatments)} Behandlungen", meta_val),
        ]
    ]

    meta_table = Table(meta_data, colWidths=[30 * mm, 95 * mm, 30 * mm, 112 * mm])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#f1f5f9")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 4 * mm))

    # 3. Main Treatments Table
    # Column widths total = 267 mm (A4 landscape 297mm - 30mm margins)
    col_widths = [
        30 * mm,  # Datum / Zeitraum
        22 * mm,  # Volk
        30 * mm,  # Standort
        42 * mm,  # Arzneimittel / Methode
        38 * mm,  # Hersteller / Info
        22 * mm,  # Menge & Einheit
        25 * mm,  # Art d. Anwendung
        26 * mm,  # Bearbeiter
        32 * mm   # Notizen / Wartezeit
    ]

    table_data = [[
        Paragraph("Datum / Zeitraum", table_header),
        Paragraph("Volk", table_header),
        Paragraph("Standort", table_header),
        Paragraph("Arzneimittel / Methode", table_header),
        Paragraph("Hersteller / Chargen", table_header),
        Paragraph("Menge", table_header),
        Paragraph("Applikation", table_header),
        Paragraph("Bearbeiter", table_header),
        Paragraph("Notizen", table_header),
    ]]

    if not treatments:
        table_data.append([
            Paragraph("Keine Behandlungen im ausgewählten Zeitraum erfasst.", table_cell),
            Paragraph("", table_cell),
            Paragraph("", table_cell),
            Paragraph("", table_cell),
            Paragraph("", table_cell),
            Paragraph("", table_cell),
            Paragraph("", table_cell),
            Paragraph("", table_cell),
            Paragraph("", table_cell),
        ])
    else:
        for t in treatments:
            period_str = format_period_str(t.date, t.end_date)
            hive_name = t.hive.name if t.hive else "-"
            loc_name = t.hive.location.name if t.hive and t.hive.location else "-"
            method_name = t.treatment_method.name if t.treatment_method else "-"
            mfg_info = t.treatment_method.manufacturer_info or "-" if t.treatment_method else "-"
            # Truncate long manufacturer info gracefully in table cell
            if len(mfg_info) > 60:
                mfg_info = mfg_info[:57] + "..."
            
            unit = t.treatment_method.unit if t.treatment_method else ""
            amount_str = f"{t.amount} {unit}"
            app_type = t.application_type.name if t.application_type else "-"
            treated_by_str = t.treated_by or (f"{t.created_by.first_name} {t.created_by.last_name}".strip() if t.created_by else "-") or "-"
            notes_str = t.notes or "-"

            table_data.append([
                Paragraph(period_str, table_cell_bold),
                Paragraph(hive_name, table_cell_bold),
                Paragraph(loc_name, table_cell),
                Paragraph(method_name, table_cell_bold),
                Paragraph(mfg_info, table_cell),
                Paragraph(amount_str, table_cell_mono),
                Paragraph(app_type, table_cell),
                Paragraph(treated_by_str, table_cell),
                Paragraph(notes_str, table_cell),
            ])

    t_table = Table(table_data, colWidths=col_widths, repeatRows=1)
    
    t_style = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#334155")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
    ]

    # Alternating row colors
    for i in range(1, len(table_data)):
        if i % 2 == 0:
            t_style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor("#f8fafc")))
        else:
            t_style.append(('BACKGROUND', (0, i), (-1, i), colors.white))

    t_table.setStyle(TableStyle(t_style))
    story.append(t_table)
    story.append(Spacer(1, 6 * mm))

    # 4. Confirmation & Signature Section (kept together to avoid breaking across page)
    sig_data = [
        [
            Paragraph("<b>Bestätigung:</b> Hiermit wird die Richtigkeit und Vollständigkeit der erfassten Behandlungen und die Einhaltung der Vorgaben (u.a. Wartezeiten) bestätigt.", legal_style),
            ""
        ],
        [
            Paragraph("<br/><br/>Ort, Datum: _____________________________________", legal_style),
            Paragraph("<br/><br/>Unterschrift des Imkers / Betriebsinhabers: _____________________________________", legal_style)
        ]
    ]
    sig_table = Table(sig_data, colWidths=[130 * mm, 137 * mm])
    sig_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('SPAN', (0, 0), (1, 0)),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
    ]))

    story.append(KeepTogether([sig_table]))

    doc.build(story, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer.getvalue()
