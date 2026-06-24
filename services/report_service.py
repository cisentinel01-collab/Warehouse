from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from sqlalchemy.orm import Session
from models.inventory import Item, Settings
import os

class ReportService:
    def __init__(self, db: Session):
        self.db = db

    def generate_inventory_report(self):
        settings = self.db.query(Settings).first() or Settings()
        filename = f"reports/inventory_{os.getpid()}.pdf"
        if not os.path.exists("reports"): os.makedirs("reports")

        doc = SimpleDocTemplate(filename, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()

        # Header
        elements.append(Paragraph(f"<b>{settings.company_name}</b>", styles['Title']))
        elements.append(Paragraph("تقرير جرد المخازن", styles['Heading2']))
        elements.append(Spacer(1, 12))

        # Data
        items = self.db.query(Item).all()
        data = [["كود الصنف", "اسم الصنف", "المخزون", "الوحدة"]]
        for i in items:
            data.append([i.code, i.name, str(i.current_stock), i.uom.name if i.uom else ""])

        t = Table(data)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(t)
        doc.build(elements)
        return filename

    def generate_inventory_excel(self):
        import pandas as pd
        items = self.db.query(Item).all()
        data = [{
            'الكود': i.code,
            'الاسم': i.name,
            'الرصيد': i.current_stock,
            'الفئة': i.category
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
