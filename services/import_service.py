import pandas as pd
import pdfplumber
import re
import os
from typing import List, Dict

class ImportService:
    def __init__(self):
        pass

    def extract_from_excel(self, file_path: str) -> List[Dict]:
        """v5 Beast-Mode Extraction with structural intelligence and header discovery."""
        from thefuzz import fuzz, process
        try:
            df = pd.read_excel(file_path, header=None)
            # Strategy 1: Data Cleaning (Drop empty perimeter)
            df = df.dropna(how='all', axis=0).dropna(how='all', axis=1)

            # 1. Beast Structural Analysis: Discover main table body
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

            # 2. Hyper-Fuzzy Header Detection (50+ variants)
            target_fields = {
                'name': ['اسم الصنف', 'Item Name', 'Description', 'Details', 'الصنف', 'البيان', 'Product', 'Model', 'النوع', 'اسم المنتج', 'اسم المادة', 'Nomenclature', 'Service', 'Task', 'Subject', 'Article', 'Items'],
                'quantity': ['الكمية', 'Quantity', 'Qty', 'Amount', 'العدد', 'الوحدات', 'Vol', 'Stock', 'Count', 'عدد الوحدات', 'QNT', 'Weight', 'Size', 'UOM', 'Units'],
                'price': ['السعر', 'Unit Price', 'Price', 'Rate', 'سعر الوحدة', 'القيمة', 'Cost', 'Unit Cost', 'المبلغ', 'سعر المفرد', 'Price Each', 'Total Price', 'Net Price', 'Total Amt', 'Value'],
                'code': ['الكود', 'Item Code', 'Part No', 'SKU', 'رقم الصنف', 'الباركود', 'Barcode', 'Ref', 'Reference', 'Serial', 'رقم المادة', 'ID', 'Part #', 'Index', 'Code', 'No.']
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

            # 3. Beast Pattern Fallback: If col_map is missing fields, scan row-by-row
            results = []
            for idx, row in df.iterrows():
                name_val = row.get(col_map.get('name')) if col_map.get('name') is not None else None

                # If fuzzy matching failed, try brute force pattern matching on the row
                if name_val is None or pd.isna(name_val):
                    # Look for first string that looks like a name and adjacent numbers
                    candidates = [x for x in row.values if not pd.isna(x)]
                    if len(candidates) >= 2:
                        # Simple heuristic: Item name usually long string, Qty/Price are floats
                        str_candidates = [str(x) for x in candidates if isinstance(x, str) and len(str(x)) > 3]
                        num_candidates = [float(re.sub(r'[^\d.]', '', str(x))) for x in candidates if str(x).replace('.','').isdigit()]
                        if str_candidates and num_candidates:
                            name_val = str_candidates[0]
                            # Assume first num is qty, second is price
                            qty_val = num_candidates[0]
                            price_val = num_candidates[1] if len(num_candidates) > 1 else 0.0
                            code_val = ""
                        else: continue
                    else: continue
                else:
                    def clean_num(val):
                        if pd.isna(val) or val == "": return 0.0
                        try:
                            s = re.sub(r'[^\d.]', '', str(val))
                            return float(s) if s else 0.0
                        except: return 0.0
                    qty_val = clean_num(row.get(col_map.get('quantity')))
                    price_val = clean_num(row.get(col_map.get('price')))
                    code_val = str(row.get(col_map.get('code'), '')).split('.')[0] if not pd.isna(row.get(col_map.get('code'))) else ''

                if not name_val or any(x in str(name_val).lower() for x in ['total', 'sum', 'إجمالي', 'مجموع']): continue

                results.append({
                    'code': code_val,
                    'name': str(name_val).strip(),
                    'quantity': qty_val,
                    'price': price_val
                })
            return results
        except Exception as e:
            print(f"v6 Hyper-Smart Excel Extraction Error: {e}")
            return []

    def extract_from_pdf(self, file_path: str) -> List[Dict]:
        """Extracts table data from PDF invoices with OCR fallback."""
        results = []
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    # Try digital extraction first
                    tables = page.extract_tables()
                    if tables:
                        for table in tables:
                            if not table or len(table) < 2: continue
                            results.extend(self._process_table_rows(table))
                    else:
                        # Fallback to OCR for scanned PDFs
                        results.extend(self.extract_from_image(file_path))
            return results
        except Exception as e:
            print(f"PDF Extraction Error: {e}")
            return []

    def extract_from_image(self, file_path: str) -> List[Dict]:
        """OCR-based extraction for scans and images using PaddleOCR."""
        try:
            from paddleocr import PaddleOCR
            # Initialize with Arabic/English support
            ocr = PaddleOCR(use_angle_cls=True, lang='ar')
            result = ocr.ocr(file_path, cls=True)

            # Simplified heuristic for OCR results
            extracted_text = []
            for idx in range(len(result)):
                res = result[idx]
                for line in res:
                    extracted_text.append(line[1][0])

            # In a real "Beast-Mode" scenario, we'd use a LLM or structural analyzer here.
            # For now, we return a list of discovered strings for the user to map.
            return [{"name": txt, "quantity": 1, "price": 0.0, "code": ""} for txt in extracted_text if len(txt) > 5]
        except Exception as e:
            print(f"OCR Extraction Error: {e}")
            return []

    def _process_table_rows(self, table):
        rows_data = []
        for row in table[1:]:
            extracted = {'name': '', 'quantity': 0, 'price': 0, 'code': ''}
            for cell in row:
                if not cell: continue
                cell_str = str(cell).strip()
                if re.match(r'^\d+(\.\d+)?$', cell_str):
                    num = float(cell_str)
                    if extracted['quantity'] == 0: extracted['quantity'] = num
                    elif extracted['price'] == 0: extracted['price'] = num
                elif len(cell_str) > 3:
                    if not extracted['name']: extracted['name'] = cell_str
                    elif not extracted['code']: extracted['code'] = cell_str
            if extracted['name'] and extracted['quantity'] > 0:
                rows_data.append(extracted)
        return rows_data
