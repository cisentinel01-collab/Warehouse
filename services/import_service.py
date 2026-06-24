import pandas as pd
import pdfplumber
import re
import os
from typing import List, Dict

class ImportService:
    def __init__(self):
        pass

    def extract_from_excel(self, file_path: str) -> List[Dict]:
        """Extracts items, quantities, and prices from Excel."""
        try:
            df = pd.read_excel(file_path)
            # Basic normalization: find columns that look like Name, Qty, Price
            results = []

            # Map common Arabic/English headers
            mapping = {
                'اسم الصنف': 'name', 'item': 'name', 'description': 'name', 'الصنف': 'name',
                'الكمية': 'quantity', 'qty': 'quantity', 'quantity': 'quantity', 'العدد': 'quantity',
                'السعر': 'price', 'price': 'price', 'سعر الوحدة': 'price', 'unit price': 'price',
                'الكود': 'code', 'code': 'code', 'barcode': 'code'
            }

            df.columns = [str(c).strip().lower() for c in df.columns]

            for index, row in df.iterrows():
                extracted = {}
                for col in df.columns:
                    for key, val in mapping.items():
                        if key.lower() in col:
                            extracted[val] = row[col]

                if extracted.get('name') and extracted.get('quantity'):
                    results.append({
                        'code': str(extracted.get('code', '')),
                        'name': str(extracted.get('name', '')),
                        'quantity': float(extracted.get('quantity', 0)),
                        'price': float(extracted.get('price', 0))
                    })
            return results
        except Exception as e:
            print(f"Excel Extraction Error: {e}")
            return []

    def extract_from_pdf(self, file_path: str) -> List[Dict]:
        """Extracts table data from PDF invoices."""
        results = []
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    tables = page.extract_tables()
                    for table in tables:
                        # Skip empty or small tables
                        if not table or len(table) < 2: continue

                        # Logic to find header row and map columns
                        headers = [str(c).strip() for c in table[0] if c]
                        for row in table[1:]:
                            # Simple heuristic: Item Name is usually the longest text
                            # Quantity and Price are numbers
                            extracted = {'name': '', 'quantity': 0, 'price': 0, 'code': ''}

                            for cell in row:
                                if not cell: continue
                                cell_str = str(cell).strip()

                                # Is it a number?
                                if re.match(r'^\d+(\.\d+)?$', cell_str):
                                    num = float(cell_str)
                                    if extracted['quantity'] == 0:
                                        extracted['quantity'] = num
                                    elif extracted['price'] == 0:
                                        extracted['price'] = num
                                elif len(cell_str) > 3:
                                    if not extracted['name']:
                                        extracted['name'] = cell_str
                                    elif not extracted['code']:
                                        extracted['code'] = cell_str

                            if extracted['name'] and extracted['quantity'] > 0:
                                results.append(extracted)
            return results
        except Exception as e:
            print(f"PDF Extraction Error: {e}")
            return []
