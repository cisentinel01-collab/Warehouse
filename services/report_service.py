from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from sqlalchemy.orm import Session
from models.inventory import Item, Settings, StockLot
from datetime import datetime, timedelta
import os

class ReportService:
    def __init__(self, db: Session):
        self.db = db

    def generate_inventory_report(self):
        from utils.translation_manager import tr, tr_manager
        try:
            settings = self.db.query(Settings).first() or Settings()
            filename = f"reports/inventory_{os.getpid()}.pdf"
            if not os.path.exists("reports"): os.makedirs("reports")

            doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
            elements = []
            styles = getSampleStyleSheet()
            is_ar = tr_manager.current_language == 'ar'

            def fmt(txt):
                if not txt: return ""
                if not is_ar: return str(txt)
                import arabic_reshaper
                from bidi.algorithm import get_display
                reshaped = arabic_reshaper.reshape(str(txt))
                return get_display(reshaped)

            # Modern Header Table
            logo_path = "logo/logo.png"
            header_data = []
            if os.path.exists(logo_path):
                logo = Image(logo_path, width=120, height=60)
                company_info = [
                    [Paragraph(f"<b>{fmt(settings.company_name)}</b>", styles['Title'])],
                    [Paragraph(fmt(settings.address or ""), styles['Normal'])],
                    [Paragraph(fmt(f"{tr('phone')}: {settings.phone or ''}"), styles['Normal'])]
                ]
                comp_table = Table(company_info)
                if is_ar:
                    header_data = [[comp_table, logo]]
                else:
                    header_data = [[logo, comp_table]]

            if header_data:
                h_table = Table(header_data, colWidths=[350, 150] if not is_ar else [150, 350])
                h_table.setStyle(TableStyle([
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('LINEBELOW', (0,0), (-1,-1), 3, colors.HexColor('#d4af37'))
                ]))
                elements.append(h_table)

            elements.append(Spacer(1, 25))
            elements.append(Paragraph(fmt(tr("inventory_report").upper()), styles['Heading2']))
            elements.append(Paragraph(fmt(f"{tr('date')}: {datetime.now().strftime('%Y-%m-%d %H:%M')}"), styles['Normal']))
            elements.append(Spacer(1, 20))

            # Pro-Level Data Fetching (Move up for Summary calculation)
            items = self.db.query(Item).filter(Item.active == True).all()

            # Summary Analytics Top Bar (Pro Max)
            total_items = len(items)
            total_qty = sum(i.current_stock for i in items)
            summary_top = [[fmt(f"{tr('total_items')}: {total_items}"), fmt(f"Total On-Hand: {total_qty}")]]
            if is_ar: summary_top[0].reverse()
            st_table = Table(summary_top, colWidths=[250, 250])
            st_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#ecf0f1')),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTSIZE', (0,0), (-1,-1), 10)
            ]))
            elements.append(st_table)
            elements.append(Spacer(1, 15))

            # Pro-Level Data Table
            headers = [tr("item_code"), tr("item_name"), tr("category"), tr("current_stock"), tr("unit")]
            if is_ar: headers.reverse()

            data = [[fmt(h) for h in headers]]
            for i in items:
                row = [i.code, i.name, i.category or "-", str(i.current_stock), i.unit or "-"]
                if is_ar: row.reverse()
                data.append([fmt(cell) for cell in row])

            if len(data) > 1:
                t = Table(data, repeatRows=1, colWidths=[100, 180, 100, 80, 70])
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f2f3f4')),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.HexColor('#ecf0f1')])
                ]))
                elements.append(t)
            else:
                elements.append(Paragraph(fmt("No items found."), styles['Normal']))

            doc.build(elements)
            return filename
        except Exception as e:
            from app_logging.app_logger import app_logger
            app_logger.error(f"Report generation error: {e}")
            raise

    def generate_inventory_excel(self):
        import pandas as pd
        from utils.translation_manager import tr
        items = self.db.query(Item).filter(Item.active == True).all()
        data = [{
            tr('item_code'): i.code,
            tr('item_name'): i.name,
            tr('current_stock'): i.current_stock,
            tr('category'): i.category
        } for i in items]
        df = pd.DataFrame(data)
        filename = f"reports/inventory_{os.getpid()}.xlsx"
        df.to_excel(filename, index=False)
        return filename

    def get_movements(self, start_date, end_date):
        from models.inventory import Movement
        query = self.db.query(Movement)
        if start_date: query = query.filter(Movement.date >= start_date)
        if end_date: query = query.filter(Movement.date <= end_date)
        return query.all()
