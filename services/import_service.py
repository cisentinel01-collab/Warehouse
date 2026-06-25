import pandas as pd
import pdfplumber
import re
import os
from typing import List, Dict

class ImportService:
    def __init__(self):
        pass

    def extract_from_excel(self, file_path: str) -> List[Dict]:
        """Extracts items, quantities, and prices from Excel with heuristic mapping."""
        try:
            df = pd.read_excel(file_path)
            results = []

            # Smart Mapping using substring matching
            mapping = {
                'name': ['اسم', 'صنف', 'item', 'description', 'details'],
                'quantity': ['كمية', 'عدد', 'qty', 'quantity', 'amount'],
                'price': ['سعر', 'سعر الوحدة', 'price', 'rate', 'cost'],
                'code': ['كود', 'رقم الصنف', 'code', 'sku', 'part']
            }

            # Find best column for each field
            col_map = {}
            for field, keywords in mapping.items():
                for col in df.columns:
                    if any(key.lower() in str(col).lower() for key in keywords):
                        col_map[field] = col
                        break

            for _, row in df.iterrows():
                if pd.isna(row.get(col_map.get('name'))): continue

                results.append({
                    'code': str(row.get(col_map.get('code'), '')).split('.')[0] if not pd.isna(row.get(col_map.get('code'))) else '',
                    'name': str(row.get(col_map.get('name'))),
                    'quantity': float(row.get(col_map.get('quantity'), 0)) if not pd.isna(row.get(col_map.get('quantity'))) else 0,
                    'price': float(row.get(col_map.get('price'), 0)) if not pd.isna(row.get(col_map.get('price'))) else 0
                })
            return results
        except Exception as e:
            print(f"Smart Excel Extraction Error: {e}")
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
