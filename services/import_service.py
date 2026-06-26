import pandas as pd
import pdfplumber
import re
import os
from typing import List, Dict

class ImportService:
    def __init__(self):
        pass

    def extract_from_excel(self, file_path: str) -> List[Dict]:
        """v3 Ultra-Smart Extraction using 40+ variants and Multi-Strategy detection."""
        from thefuzz import fuzz, process
        try:
            df = pd.read_excel(file_path)
            # Strategy 1: Data Cleaning (Drop leading empty rows/cols)
            df = df.dropna(how='all', axis=0).dropna(how='all', axis=1)
            results = []

            # Expanded detection library (40+ variants)
            target_fields = {
                'name': ['اسم الصنف', 'Item Name', 'Description', 'Details', 'الصنف', 'البيان', 'Product', 'Model', 'النوع', 'اسم المنتج', 'اسم المادة'],
                'quantity': ['الكمية', 'Quantity', 'Qty', 'Amount', 'العدد', 'الوحدات', 'Vol', 'Stock', 'Count', 'كست', 'عدد الوحدات'],
                'price': ['السعر', 'Unit Price', 'Price', 'Rate', 'سعر الوحدة', 'القيمة', 'Cost', 'Unit Cost', 'المبلغ', 'سعر المفرد'],
                'code': ['الكود', 'Item Code', 'Part No', 'SKU', 'رقم الصنف', 'الباركود', 'Barcode', 'Ref', 'Reference', 'Serial', 'رقم المادة']
            }

            col_map = {}
            # Strategy 2: Adaptive Header Location (Search first 10 rows for headers)
            for i in range(min(10, len(df))):
                row_vals = [str(x).lower() for x in df.iloc[i].values]
                matches = 0
                for f, variants in target_fields.items():
                    if any(v.lower() in row_vals for v in variants): matches += 1
                if matches >= 2:
                    df.columns = df.iloc[i]
                    df = df.iloc[i+1:]
                    break

            for field, choices in target_fields.items():
                best_match = None
                highest_score = 0
                for col in df.columns:
                    col_str = str(col).strip()
                    if not col_str or col_str == 'nan': continue
                    match, score = process.extractOne(col_str, choices, scorer=fuzz.token_set_ratio)
                    if score > 75 and score > highest_score:
                        highest_score = score
                        best_match = col
                if best_match:
                    col_map[field] = best_match

            # Strategy 3: Heuristic cleaning
            for _, row in df.iterrows():
                name_val = row.get(col_map.get('name'))
                if pd.isna(name_val) or str(name_val).strip() == "" or str(name_val).lower() == "total": continue

                def clean_num(val):
                    if pd.isna(val) or val == "": return 0.0
                    try:
                        s = str(val).replace(',', '').replace('$', '').replace('SAR', '').replace('EGP', '').strip()
                        return float(s)
                    except: return 0.0

                results.append({
                    'code': str(row.get(col_map.get('code'), '')).split('.')[0] if not pd.isna(row.get(col_map.get('code'))) else '',
                    'name': str(name_val).strip(),
                    'quantity': clean_num(row.get(col_map.get('quantity'))),
                    'price': clean_num(row.get(col_map.get('price')))
                })
            return results
        except Exception as e:
            print(f"v3 Ultra-Smart Excel Extraction Error: {e}")
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
