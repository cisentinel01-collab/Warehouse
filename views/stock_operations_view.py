from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QPushButton, QLineEdit, QLabel,
                             QHeaderView, QComboBox, QSpinBox, QFormLayout,
                             QGroupBox, QMessageBox, QTabWidget, QDoubleSpinBox,
                             QInputDialog, QDateEdit, QGridLayout, QScrollArea, QFrame)
from PySide6.QtCore import Qt, Signal, QTimer
import qtawesome as qta
from utils.auth import AuthManager
from database.session import Session

class StockOperationsView(QWidget):
    data_changed = Signal()

    def __init__(self, controller, op_type="IN"):
        super().__init__()
        self.controller = controller
        self.op_type = op_type # "IN" or "OUT"
        self.items_to_move = []

        # Debounce timer for item combo search
        self.item_search_timer = QTimer()
        self.item_search_timer.setSingleShot(True)
        self.item_search_timer.timeout.connect(self.perform_item_search)

        self.setup_ui()

    def setup_ui(self):
        from utils.translation_manager import tr
        self.main_layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)

        # Operation Tab
        self.op_tab = QWidget()
        self.setup_operation_tab()
        self.tabs.addTab(self.op_tab, tr("execute_operation"))

        # History Tab
        self.history_tab = QWidget()
        self.setup_history_tab()
        self.tabs.addTab(self.history_tab, tr("history"))

    def setup_operation_tab(self):
        main_layout = QVBoxLayout(self.op_tab)

        # Scroll Area for spacious layout
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(30) # High spacing for "comfort"

        # Header Info
        info_group = QGroupBox("بيانات العملية")
        info_layout = QFormLayout(info_group)
        info_layout.setSpacing(20)
        info_layout.setLabelAlignment(Qt.AlignRight)

        self.ref_input = QLineEdit()
        self.ref_input.setReadOnly(True)
        self.ref_input.setMinimumHeight(45)
        self.ref_input.setPlaceholderText("سيتم التوليد تلقائياً")
        self.ref_input.setText(self.controller.generate_invoice_no(self.op_type))
        info_layout.addRow("رقم الفاتورة/العملية:", self.ref_input)

        from utils.translation_manager import tr
        if self.op_type == "IN":
            self.supplier_combo = QComboBox()
            self.supplier_combo.setMinimumHeight(45)
            self.supplier_combo.setToolTip(tr("select_supplier_tooltip"))
            self.load_suppliers()
            info_layout.addRow(tr("supplier") + ":", self.supplier_combo)

            self.receiver_input = QLineEdit()
            self.receiver_input.setMinimumHeight(45)
            self.receiver_input.setPlaceholderText(tr("receiver_placeholder"))
            from utils.validator import Validator
            Validator.setup_strict_validation(self.receiver_input, "name")
            info_layout.addRow(tr("receiver_name") + ":", self.receiver_input)
        else:
            self.issuing_entity = QLineEdit()
            self.issuing_entity.setMinimumHeight(45)
            self.issuing_entity.setPlaceholderText(tr("issuing_entity_placeholder"))
            from utils.validator import Validator
            Validator.setup_strict_validation(self.issuing_entity, "name")
            info_layout.addRow(tr("issuing_entity") + ":", self.issuing_entity)

            self.receiver_name = QLineEdit()
            self.receiver_name.setMinimumHeight(45)
            self.receiver_name.setPlaceholderText(tr("receiver_person_placeholder"))
            Validator.setup_strict_validation(self.receiver_name, "name")
            info_layout.addRow(tr("receiver_person") + ":", self.receiver_name)

            self.reason_input = QLineEdit()
            self.reason_input.setMinimumHeight(45)
            self.reason_input.setPlaceholderText(tr("issue_reason_placeholder"))
            info_layout.addRow(tr("issue_reason") + ":", self.reason_input)

        layout.addWidget(info_group)

        # Item Selector (Enhanced Smart Grid)
        selector_group = QGroupBox("إضافة أصناف ذكية")
        selector_grid = QGridLayout(selector_group)
        selector_grid.setSpacing(25)

        self.item_combo = QComboBox()
        self.item_combo.setEditable(True)
        self.item_combo.setMinimumHeight(50)
        self.item_combo.setPlaceholderText("اختر صنف أو ابحث بالكود...")

        # Connect signals once here
        self.item_combo.lineEdit().textChanged.connect(self.on_item_combo_text_changed)
        self.item_combo.currentIndexChanged.connect(self.handle_item_selection_change)

        self.load_items()

        item_h_layout = QHBoxLayout()
        item_h_layout.addWidget(self.item_combo)

        selector_grid.addWidget(QLabel("الصنف:"), 0, 0)
        selector_grid.addLayout(item_h_layout, 0, 1, 1, 3)

        self.qty_input = QSpinBox()
        self.qty_input.setMinimum(1)
        self.qty_input.setMaximum(1000000)
        self.qty_input.setMinimumHeight(45)
        selector_grid.addWidget(QLabel("الكمية المطلوب تحريكها:"), 1, 0)
        selector_grid.addWidget(self.qty_input, 1, 1)

        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("0.00")
        self.price_input.setMinimumHeight(45)
        selector_grid.addWidget(QLabel("سعر الوحدة:"), 1, 2)
        selector_grid.addWidget(self.price_input, 1, 3)

        if self.op_type == "IN":
            self.batch_input = QLineEdit()
            self.batch_input.setPlaceholderText("رقم التشغيلة / Batch Number")
            self.batch_input.setMinimumHeight(45)
            selector_grid.addWidget(QLabel("رقم التشغيلة:"), 2, 0)
            selector_grid.addWidget(self.batch_input, 2, 1)

            self.prod_date = QDateEdit()
            self.prod_date.setCalendarPopup(True)
            from PySide6.QtCore import QDate
            self.prod_date.setDate(QDate.currentDate())
            self.prod_date.setMinimumHeight(45)
            selector_grid.addWidget(QLabel("تاريخ الإنتاج:"), 2, 2)
            selector_grid.addWidget(self.prod_date, 2, 3)

            self.exp_date = QDateEdit()
            self.exp_date.setCalendarPopup(True)
            self.exp_date.setDate(QDate.currentDate().addYears(1))
            self.exp_date.setMinimumHeight(45)
            selector_grid.addWidget(QLabel("تاريخ الانتهاء:"), 3, 0)
            selector_grid.addWidget(self.exp_date, 3, 1)

        add_item_btn = QPushButton("إضافة الصنف للقائمة (ذكية)")
        add_item_btn.setObjectName("GoldButton")
        add_item_btn.setMinimumHeight(55)
        add_item_btn.setIcon(qta.icon("fa5s.plus-circle", color="black"))
        add_item_btn.setEnabled(AuthManager.has_permission(self.op_type.lower(), 'submit'))
        add_item_btn.clicked.connect(self.add_item_to_list)
        selector_grid.addWidget(add_item_btn, 3, 2, 1, 2)

        import_btn = QPushButton("استيراد ذكي من (Excel/PDF)")
        import_btn.setIcon(qta.icon("fa5s.file-upload", color="white"))
        import_btn.setStyleSheet("background-color: #2980b9; color: white; padding: 10px;")
        import_btn.clicked.connect(self.handle_smart_import)
        selector_grid.addWidget(import_btn, 4, 0, 1, 4)

        layout.addWidget(selector_group)

        # Selected Items Table
        table_group = QGroupBox("الأصناف المضافة للعملية")
        table_layout = QVBoxLayout(table_group)
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        headers = ["الكود", "الاسم", "الكمية", "السعر"]
        self.table.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setMinimumHeight(300)
        table_layout.addWidget(self.table)

        clear_btn = QPushButton("مسح القائمة بالكامل")
        clear_btn.setStyleSheet("color: #e74c3c; border: 1px solid #e74c3c; padding: 5px;")
        clear_btn.clicked.connect(self.clear_list)
        table_layout.addWidget(clear_btn, 0, Qt.AlignLeft)

        layout.addWidget(table_group)

        # Financials
        fin_group = QGroupBox("الإجماليات والخصومات")
        fin_layout = QFormLayout(fin_group)
        fin_layout.setSpacing(20)

        disc_box = QHBoxLayout()
        self.discount_input = QSpinBox()
        self.discount_input.setSuffix("%")
        self.discount_input.setMinimumHeight(45)
        self.discount_input.setMinimumWidth(150)
        self.discount_input.valueChanged.connect(self.update_summary)
        disc_box.addWidget(self.discount_input)
        disc_box.addStretch()

        fin_layout.addRow("نسبة الخصم التجاري:", disc_box)

        self.summary_label = QLabel("المجموع: 0.00 | الخصم: 0.00 | الإجمالي: 0.00")
        self.summary_label.setObjectName("GoldSummaryLabel")
        self.summary_label.setMinimumHeight(60)
        fin_layout.addRow(self.summary_label)

        # Submit Button
        self.submit_btn = QPushButton("إتمام العملية وتوليد المستندات (PDF)")
        self.submit_btn.setObjectName("PrimaryButton")
        self.submit_btn.setFixedHeight(65)
        if not AuthManager.has_permission(self.op_type.lower(), 'submit'):
            self.submit_btn.setEnabled(False)
            self.submit_btn.setToolTip("لا تملك صلاحية تنفيذ هذه العملية")

        self.submit_btn.clicked.connect(self.handle_submit)
        fin_layout.addRow(self.submit_btn)

        layout.addWidget(fin_group)

        scroll.setWidget(container)
        main_layout.addWidget(scroll)

    def handle_smart_import(self):
        from PySide6.QtWidgets import QFileDialog
        from services.import_service import ImportService
        from views.import_verification_dialog import ImportVerificationDialog

        file_path, _ = QFileDialog.getOpenFileName(self, "اختر ملف الفاتورة", "", "All Files (*.xlsx *.pdf *.xls)")
        if not file_path: return

        service = ImportService()
        if file_path.endswith('.pdf'):
            data = service.extract_from_pdf(file_path)
        else:
            data = service.extract_from_excel(file_path)

        if not data:
            QMessageBox.warning(self, "تنبيه", "لم يتم العثور على بيانات في الملف أو تنسيق الملف غير مدعوم")
            return

        dialog = ImportVerificationDialog(data, self)
        if dialog.exec():
            # Add confirmed items to list
            for item in dialog.confirmed_data:
                # Find item in system
                sys_item = self.controller.get_item_by_code(item['code'])
                if not sys_item:
                    search_res = self.controller.search_items(item['name'])
                    if search_res: sys_item = search_res[0]

                if sys_item:
                    # Model to dict if SQLAlchemy object
                    if not isinstance(sys_item, dict):
                        sys_item = {
                            'id': sys_item.id,
                            'code': sys_item.code,
                            'name': sys_item.name,
                            'unit': sys_item.uom.name if sys_item.uom else ''
                        }

                    item_id = sys_item['id']
                    item_code = sys_item['code']
                    item_name = sys_item['name']
                else:
                    QMessageBox.information(self, "تنبيه", f"الصنف {item['name']} غير موجود في النظام. يرجى إضافته يدوياً.")
                    continue

                self.items_to_move.append({
                    "item_id": item_id,
                    "item_name": item_name,
                    "item_code": item_code,
                    "quantity": item['quantity'],
                    "price": item['price'],
                    "unit": sys_item.get('unit', '')
                })

                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(str(item_code)))
                self.table.setItem(row, 1, QTableWidgetItem(str(item_name)))
                self.table.setItem(row, 2, QTableWidgetItem(str(item['quantity'])))
                self.table.setItem(row, 3, QTableWidgetItem(str(item['price'])))

            self.update_summary()

    def setup_history_tab(self):
        from PySide6.QtWidgets import QTableView
        from views_components.enterprise_table_model import EnterpriseTableModel
        from PySide6.QtCore import QThreadPool
        from utils.translation_manager import tr

        self.threadpool = QThreadPool.globalInstance()
        layout = QVBoxLayout(self.history_tab)
        layout.setContentsMargins(20, 20, 20, 20)

        self.history_view = QTableView()
        self.history_view.setEditTriggers(QTableView.NoEditTriggers)
        self.history_view.setSelectionBehavior(QTableView.SelectRows)
        self.history_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.history_view.doubleClicked.connect(self.handle_history_double_click)
        layout.addWidget(self.history_view)

        self.history_headers = ["date", "reference_no", "party", "final_total"]
        self.history_model = EnterpriseTableModel([], self.history_headers)
        self.history_view.setModel(self.history_model)

        refresh_btn = QPushButton(tr("refresh_history"))
        refresh_btn.clicked.connect(self.load_history)
        layout.addWidget(refresh_btn)

        self.load_history()

    def load_history(self):
        from workers.worker import Worker
        worker = Worker(self.controller.get_movement_history, type=self.op_type, limit=100)
        worker.signals.result.connect(self.on_history_loaded)
        self.threadpool.start(worker)

    def on_history_loaded(self, history):
        data = []
        for h in history:
            # Handle model object or dict
            if self.op_type == 'IN':
                party_obj = getattr(h, 'supplier', None)
                party_name = party_obj.name if party_obj else getattr(h, 'supplier_name', 'N/A')
            else:
                party_name = getattr(h, 'issuing_entity', 'N/A')

            data.append({
                "id": getattr(h, 'id', None),
                "date": str(getattr(h, 'date', '')).split('.')[0],
                "reference_no": getattr(h, 'reference_no', ''),
                "party": party_name,
                "final_total": f"{float(getattr(h, 'final_total', 0)):,.2f}"
            })
        self.history_model.update_data(data)

    def handle_history_double_click(self, index):
        if not index.isValid(): return
        row_data = self.history_model._data[index.row()]
        m_id = row_data.get("id")
        if m_id:
            self.view_movement_pdf(m_id)

    def view_movement_pdf(self, movement_id):
        path = self.controller.generate_movement_pdf(movement_id)
        from views.print_preview import PrintPreviewDialog
        dialog = PrintPreviewDialog(path, self)
        dialog.exec()

    def load_suppliers(self):
        self.supplier_combo.clear()
        suppliers = self.controller.get_suppliers()
        for s in suppliers:
            # Model to dict if needed
            s_id = s.id if hasattr(s, 'id') else s['id']
            s_name = s.name if hasattr(s, 'name') else s['name']
            self.supplier_combo.addItem(s_name, s_id)

    def update_summary(self):
        subtotal = sum(item['quantity'] * item.get('price', 0) for item in self.items_to_move)
        total_qty = sum(item['quantity'] for item in self.items_to_move)
        discount_pct = self.discount_input.value()
        discount_amt = (subtotal * discount_pct) / 100
        final = subtotal - discount_amt
        self.summary_label.setText(
            f"إجمالي عدد الأصناف: {len(self.items_to_move)} | إجمالي الكميات: {total_qty}\n"
            f"المجموع: {subtotal:,.2f} | الخصم: {discount_amt:,.2f} | الإجمالي النهائي: {final:,.2f}"
        )

    def handle_item_selection_change(self):
        item_data = self.item_combo.currentData()
        if item_data:
            try:
                # item_data could be a dict or a model object
                item_id = getattr(item_data, 'id', None)
                if item_id is None and isinstance(item_data, dict):
                    item_id = item_data.get('id')

                if not item_id: return

                # Fetch last purchase price via raw query for speed
                from database.db_manager import DBManager
                db = DBManager()
                query = """
                    SELECT mi.price FROM movement_items mi
                    JOIN movements m ON mi.movement_id = m.id
                    WHERE mi.item_id = :p1 AND m.type = 'IN'
                    ORDER BY m.date DESC LIMIT 1
                """
                res = db.execute_query(query, (item_id,))
                if res:
                    self.price_input.setText(f"{float(res[0]['price']):.2f}")
                else:
                    self.price_input.setText("0.00")
            except Exception as e:
                # Fallback to zero if query fails
                self.price_input.setText("0.00")

    def load_items(self):
        self.item_combo.blockSignals(True)
        self.item_combo.clear()
        items = self.controller.get_items(limit=100)
        for i in items:
            code = i.code if hasattr(i, 'code') else i['code']
            name = i.name if hasattr(i, 'name') else i['name']
            stock = i.current_stock if hasattr(i, 'current_stock') else i['current_stock']
            self.item_combo.addItem(f"{code} - {name} (المخزون: {stock})", i)
        self.item_combo.blockSignals(False)

    def on_item_combo_text_changed(self, text):
        if len(text) >= 2:
            self.item_search_timer.start(300)

    def perform_item_search(self):
        text = self.item_combo.currentText()
        if not text:
            return

        items = self.controller.search_items(text)

        self.item_combo.blockSignals(True)
        self.item_combo.clear()
        for i in items[:50]:
            code = i.code if hasattr(i, 'code') else i['code']
            name = i.name if hasattr(i, 'name') else i['name']
            stock = i.current_stock if hasattr(i, 'current_stock') else i['current_stock']
            self.item_combo.addItem(f"{code} - {name} (المخزون: {stock})", i)
        self.item_combo.setEditText(text)
        self.item_combo.blockSignals(False)

    def clear_list(self):
        if self.items_to_move:
            self.table.setRowCount(0)
            self.items_to_move = []
            self.update_summary()

    def refresh(self):
        self.load_items()
        self.load_history()

    def add_item_to_list(self):
        item_data = self.item_combo.currentData()

        if not item_data:
            typed_text = self.item_combo.currentText().split(" - ")[0].strip()
            item_data = self.controller.get_item_by_code(typed_text)

        if not item_data:
            QMessageBox.warning(self, "تنبيه", "يرجى اختيار صنف صحيح أولاً")
            return

        qty = self.qty_input.value()
        if qty <= 0: return

        try:
            price_text = self.price_input.text()
            if not price_text:
                QMessageBox.warning(self, "تنبيه", "يرجى إدخال السعر")
                return
            price = float(price_text)
        except ValueError:
            QMessageBox.warning(self, "خطأ", "السعر يجب أن يكون رقماً")
            return

        item_id = item_data.id if hasattr(item_data, 'id') else item_data['id']
        item_code = item_data.code if hasattr(item_data, 'code') else item_data['code']
        item_name = item_data.name if hasattr(item_data, 'name') else item_data['name']
        item_stock = item_data.current_stock if hasattr(item_data, 'current_stock') else item_data['current_stock']

        existing_idx = -1
        for idx, item in enumerate(self.items_to_move):
            if item['item_id'] == item_id:
                if self.op_type == "IN":
                    new_batch = self.batch_input.text() or "DEFAULT"
                    if item.get('batch_info', {}).get('batch_number') == new_batch:
                        existing_idx = idx
                        break
                else:
                    existing_idx = idx
                    break

        if existing_idx != -1:
            new_qty = self.items_to_move[existing_idx]['quantity'] + qty
        else:
            new_qty = qty

        if self.op_type == "OUT":
            if new_qty > item_stock:
                QMessageBox.warning(self, "تنبيه المخزون",
                                  f"الكمية الكلية المطلوبة ({new_qty}) أكبر من المخزون المتاح ({item_stock})")
                return

        if existing_idx != -1:
            self.items_to_move[existing_idx]['quantity'] = new_qty
            self.items_to_move[existing_idx]['price'] = price
            self.table.setItem(existing_idx, 2, QTableWidgetItem(str(new_qty)))
            self.table.setItem(existing_idx, 3, QTableWidgetItem(str(price)))
        else:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(item_code)))
            self.table.setItem(row, 1, QTableWidgetItem(str(item_name)))
            self.table.setItem(row, 2, QTableWidgetItem(str(qty)))
            self.table.setItem(row, 3, QTableWidgetItem(str(price)))

            item_entry = {
                "item_id": item_id,
                "item_name": item_name,
                "item_code": item_code,
                "quantity": qty,
                "price": price,
                "unit": item_data.uom.name if hasattr(item_data, 'uom') and item_data.uom else ''
            }

            if self.op_type == "IN":
                item_entry["batch_info"] = {
                    "batch_number": self.batch_input.text() or "DEFAULT",
                    "production_date": self.prod_date.date().toString("yyyy-MM-dd"),
                    "expiry_date": self.exp_date.date().toString("yyyy-MM-dd")
                }

            self.items_to_move.append(item_entry)

        self.update_summary()

    def handle_submit(self):
        if not AuthManager.has_permission(self.op_type.lower(), 'submit'):
            QMessageBox.warning(self, "تنبيه", "لا تملك صلاحية تنفيذ هذه العملية")
            return

        if not self.items_to_move:
            QMessageBox.warning(self, "تنبيه", "يرجى إضافة أصناف أولاً")
            return

        try:
            ref_no = self.controller.generate_invoice_no(self.op_type)
            self.ref_input.setText(ref_no)

            movement_data = {
                "reference_no": ref_no,
                "notes": "",
                "discount_percent": self.discount_input.value()
            }

            from utils.validator import Validator
            from utils.notifications import NotificationManager
            if self.op_type == "IN":
                if not Validator.is_not_empty(self.receiver_input.text()):
                    QMessageBox.warning(self, "تنبيه", "يرجى إدخال اسم المستلم")
                    return
                if not self.supplier_combo.currentData():
                    QMessageBox.warning(self, "تنبيه", "يرجى اختيار المورد")
                    return
                movement_data["supplier_id"] = self.supplier_combo.currentData()
                movement_data["received_by"] = self.receiver_input.text()
                success, low_items = self.controller.receive_stock(movement_data, self.items_to_move)
            else:
                if not Validator.is_not_empty(self.issuing_entity.text()) or \
                   not Validator.is_not_empty(self.receiver_name.text()):
                    QMessageBox.warning(self, "تنبيه", "يرجى إدخال الجهة المستلمة واسم الشخص")
                    return
                movement_data["issuing_entity"] = self.issuing_entity.text()
                movement_data["receiver_name"] = self.receiver_name.text()
                movement_data["reason"] = self.reason_input.text()
                success, low_items = self.controller.issue_stock(movement_data, self.items_to_move)

            if success:
                msg = f"تمت العملية بنجاح. رقم الفاتورة: {ref_no}"
                QMessageBox.information(self, "نجاح", msg)

                for item in low_items:
                    NotificationManager.error(self.window(), f"تنبيه: الصنف '{item}' وصل للحد الحرج!")
                self.reset_form()
                self.data_changed.emit()
                self.load_history()
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل إتمام العملية: {str(e)}")

    def reset_form(self):
        self.ref_input.setText(self.controller.generate_invoice_no(self.op_type))
        self.table.setRowCount(0)
        self.items_to_move = []
        self.summary_label.setText("المجموع: 0.00 | الخصم: 0.00 | الإجمالي: 0.00")
        self.discount_input.setValue(0)
        if self.op_type == "IN":
            self.receiver_input.clear()
        else:
            self.issuing_entity.clear()
            self.receiver_name.clear()
            self.reason_input.clear()
        self.load_items()

    def closeEvent(self, event):
        Session.remove()
        event.accept()
