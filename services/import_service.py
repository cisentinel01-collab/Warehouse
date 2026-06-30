import pandas as pd
import pdfplumber
import re
import os
from typing import List, Dict, Callable, Optional
from thefuzz import fuzz, process

class ImportService:
    def __init__(self):
        pass

    def extract_from_excel(self, file_path: str, progress_callback: Optional[Callable[[int], None]] = None) -> List[Dict]:
        """v5 Beast-Mode Extraction with structural intelligence and header discovery."""
        try:
            if progress_callback: progress_callback(10)
            df = pd.read_excel(file_path, header=None)
            if progress_callback: progress_callback(20)

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
                'code': ['الكود', 'Item Code', 'Part No', 'SKU', 'رقم الصنف', 'الباركود', 'Barcode', 'Ref', 'Reference', 'Serial', 'رقم المادة', 'ID', 'Part #', 'Index', 'Code', 'No.'],
                'production_date': ['تاريخ الانتاج', 'Production Date', 'MFG Date', 'MFG'],
                'expiry_date': ['تاريخ الانتهاء', 'Expiry Date', 'Exp', 'Valid Until']
            }

            col_map = {}
            total_fields = len(target_fields)
            for idx, (field, choices) in enumerate(target_fields.items()):
                if progress_callback: progress_callback(30 + int((idx / total_fields) * 20))
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
            total_rows = len(df)
            for idx, (row_idx, row) in enumerate(df.iterrows()):
                if progress_callback and idx % 10 == 0:
                    progress_callback(50 + int((idx / total_rows) * 45))
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

                def clean_date(val):
                    if pd.isna(val) or val == "" or str(val).lower() == "none": return None
                    try:
                        # Advanced date parsing with format detection
                        return pd.to_datetime(val, errors='coerce').strftime("%Y-%m-%d")
                    except: return None

                results.append({
                    'code': code_val,
                    'name': str(name_val).strip(),
                    'quantity': qty_val,
                    'price': price_val,
                    'production_date': clean_date(row.get(col_map.get('production_date'))),
                    'expiry_date': clean_date(row.get(col_map.get('expiry_date')))
                })
            if progress_callback: progress_callback(100)
            return results
        except Exception as e:
            print(f"v6 Hyper-Smart Excel Extraction Error: {e}")
            return []

    def extract_from_pdf(self, file_path: str) -> List[Dict]:
        """v7 Hybrid Extraction: Structural Digital Tables + Keyword Heuristics + OCR Fallback."""
        results = []
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    # 1. Structural Digital Table Extraction
                    tables = page.extract_tables({
                        "vertical_strategy": "lines",
                        "horizontal_strategy": "lines",
                        "intersection_y_tolerance": 10
                    })

                    if tables:
                        for table in tables:
                            if not table or len(table) < 2: continue
                            results.extend(self._process_table_rows(table))

                    # 2. Heuristic Line-by-Line (if tables failed or incomplete)
                    if len(results) < 2:
                        text = page.extract_text()
                        if text:
                            results.extend(self._extract_via_heuristics(text))

                # 3. Final OCR Fallback (if still no good data)
                if not results:
                    results.extend(self.extract_from_image(file_path))

            return results
        except Exception as e:
            print(f"PDF Extraction Error: {e}")
            return []

    def _extract_via_heuristics(self, text: str) -> List[Dict]:
        """Advanced Regex & Keyword matching for non-tabular digital text."""
        heuristic_results = []
        # Look for patterns: [Name/Desc] ... [Qty] ... [Price]
        lines = text.split('\n')
        for line in lines:
            # Skip totals
            if any(x in line.lower() for x in ['total', 'sum', 'إجمالي', 'مجموع']): continue

            # Pattern: Long string followed by 1 or 2 numbers
            # Matches many standard invoice formats
            parts = re.findall(r'(\w[\w\s\.-]{5,})\s+(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)?', line)
            for p in parts:
                heuristic_results.append({
                    'name': p[0].strip(),
                    'quantity': float(p[1]),
                    'price': float(p[2]) if p[2] else 0.0,
                    'code': ""
                })
        return heuristic_results

    def extract_from_image(self, file_path: str) -> List[Dict]:
        """v8 AI OCR with Grid Grouping logic using PaddleOCR."""
        try:
            from paddleocr import PaddleOCR
            # lang='ar' handles both English and Arabic characters
            ocr = PaddleOCR(use_angle_cls=True, lang='ar', show_log=False)
            result = ocr.ocr(file_path, cls=True)

            if not result or not result[0]: return []

            # 1. Structural Intelligence: Group boxes by Y-coordinate (rows)
            lines = result[0]
            rows = {}
            for box in lines:
                y_center = (box[0][0][1] + box[0][2][1]) / 2
                # Round to nearest 15 pixels to group cells into rows
                row_key = round(y_center / 15) * 15
                if row_key not in rows: rows[row_key] = []
                rows[row_key].append(box)

            structured_rows = []
            for r_key in sorted(rows.keys()):
                # Sort cells in row by X-coordinate
                cells = sorted(rows[r_key], key=lambda x: x[0][0][0])
                texts = [c[1][0] for c in cells]

                # Filter out rows that don't look like data (single cell or too short)
                if len(texts) < 2: continue

                # 2. Heuristic Column Discovery in the row
                row_data = {'name': '', 'quantity': 1, 'price': 0.0, 'code': ''}
                found_num = False
                for t in texts:
                    t_clean = re.sub(r'[^\d.]', '', t)
                    if t_clean and t_clean.replace('.','').isdigit() and len(t_clean) < 10:
                        val = float(t_clean)
                        if not found_num:
                            row_data['quantity'] = val; found_num = True
                        else:
                            row_data['price'] = val
                    elif len(t) > 3 and not row_data['name']:
                        row_data['name'] = t

                if row_data['name']:
                    structured_rows.append(row_data)

            return structured_rows
        except Exception as e:
            print(f"v8 AI OCR Extraction Error: {e}")
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
