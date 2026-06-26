import pandas as pd
import pdfplumber
import re
import os
from typing import List, Dict

class ImportService:
    def __init__(self):
        pass

    def extract_from_excel(self, file_path: str) -> List[Dict]:
        """v4 Enterprise-Grade Extraction with structural analysis."""
        from thefuzz import fuzz, process
        try:
            df = pd.read_excel(file_path, header=None)
            # 1. Structural Analysis: Find the main table body
            # We look for the row with the most contentful cells
            max_cols = 0
            header_row_idx = 0
            for i in range(min(20, len(df))):
                non_empty = df.iloc[i].count()
                if non_empty > max_cols:
                    max_cols = non_empty
                    header_row_idx = i

            df.columns = df.iloc[header_row_idx]
            df = df.iloc[header_row_idx+1:]
            df = df.dropna(how='all', axis=0)

            # 2. Hyper-Fuzzy Header Detection (40+ variants)
            target_fields = {
                'name': ['اسم الصنف', 'Item Name', 'Description', 'Details', 'الصنف', 'البيان', 'Product', 'Model', 'النوع', 'اسم المنتج', 'اسم المادة', 'Nomenclature', 'Service', 'Task'],
                'quantity': ['الكمية', 'Quantity', 'Qty', 'Amount', 'العدد', 'الوحدات', 'Vol', 'Stock', 'Count', 'كست', 'عدد الوحدات', 'QNT', 'Weight', 'Size'],
                'price': ['السعر', 'Unit Price', 'Price', 'Rate', 'سعر الوحدة', 'القيمة', 'Cost', 'Unit Cost', 'المبلغ', 'سعر المفرد', 'Price Each', 'Total Price', 'Net Price'],
                'code': ['الكود', 'Item Code', 'Part No', 'SKU', 'رقم الصنف', 'الباركود', 'Barcode', 'Ref', 'Reference', 'Serial', 'رقم المادة', 'ID', 'Part #', 'Index']
            }

            col_map = {}
            for field, choices in target_fields.items():
                best_match = None
                highest_score = 0
                for col in df.columns:
                    col_str = str(col).strip()
                    if not col_str or col_str.lower() == 'nan': continue
                    match, score = process.extractOne(col_str, choices, scorer=fuzz.token_set_ratio)
                    if score > 70 and score > highest_score:
                        highest_score = score
                        best_match = col
                if best_match:
                    col_map[field] = best_match

            # 3. Intelligent Data Cleaning & Mapping
            results = []
            for _, row in df.iterrows():
                name_val = row.get(col_map.get('name'))
                if pd.isna(name_val) or str(name_val).strip() == "": continue
                if any(x in str(name_val).lower() for x in ['total', 'sum', 'إجمالي', 'مجموع']): continue

                def clean_num(val):
                    if pd.isna(val) or val == "": return 0.0
                    try:
                        # Handle values like "1,200.50 SAR"
                        s = re.sub(r'[^\d.]', '', str(val))
                        return float(s) if s else 0.0
                    except: return 0.0

                results.append({
                    'code': str(row.get(col_map.get('code'), '')).split('.')[0] if not pd.isna(row.get(col_map.get('code'))) else '',
                    'name': str(name_val).strip(),
                    'quantity': clean_num(row.get(col_map.get('quantity'))),
                    'price': clean_num(row.get(col_map.get('price')))
                })
            return results
        except Exception as e:
            print(f"v4 Hyper-Smart Excel Extraction Error: {e}")
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
