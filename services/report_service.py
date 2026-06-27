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

            doc = SimpleDocTemplate(filename, pagesize=A4)
            elements = []
            styles = getSampleStyleSheet()

            # RTL/LTR Logic for PDF
            is_ar = tr_manager.current_language == 'ar'

            def fmt(txt):
                if not txt: return ""
                if not is_ar: return str(txt)
                import arabic_reshaper
                from bidi.algorithm import get_display
                reshaped = arabic_reshaper.reshape(str(txt))
                return get_display(reshaped)

            # Header
            # Logo Handling
            logo_path = "logo/logo.png"
            if os.path.exists(logo_path):
                img = Image(logo_path, width=100, height=50)
                elements.append(img)

            elements.append(Paragraph(f"<b>{fmt(settings.company_name)}</b>", styles['Title']))
            elements.append(Paragraph(fmt(tr("inventory_report")), styles['Heading2']))
            elements.append(Paragraph(fmt(f"{tr('date')}: {datetime.now().strftime('%Y-%m-%d %H:%M')}"), styles['Normal']))
            elements.append(Spacer(1, 12))

            # Data
            items = self.db.query(Item).filter(Item.active == True).all()
            headers = [tr("item_code"), tr("item_name"), tr("current_stock"), tr("unit")]
            if is_ar: headers.reverse()

            data = [[fmt(h) for h in headers]]
            for i in items:
                row = [i.code, i.name, str(i.current_stock), i.uom_id if hasattr(i, 'uom_id') else ""]
                if is_ar: row.reverse()
                data.append([fmt(cell) for cell in row])

            if len(data) > 1:
                t = Table(data)
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'), # For Arabic we'd need a TrueType font like Cairo
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
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
