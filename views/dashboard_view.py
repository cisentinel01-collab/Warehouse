from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QLabel, QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QProgressBar, QScrollArea)
from PySide6.QtCore import Qt, QThreadPool
import qtawesome as qta
from workers.worker import Worker

class DashboardView(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.threadpool = QThreadPool()
        self.setup_ui()

    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.refresh()

    def refresh(self):
        worker = Worker(self.controller.get_stats)
        worker.signals.result.connect(self.on_stats_loaded)
        self.threadpool.start(worker)

    def on_stats_loaded(self, stats):
        # Clear existing layout
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(40)

        # 1. Main KPI Row
        cards_layout = QGridLayout()
        cards_layout.setSpacing(30)

        self.add_card(cards_layout, "إجمالي الأصناف", str(stats['total_items']), "fa5s.boxes", "#1a2a6c", 0, 0)
        self.add_card(cards_layout, "قيمة المخزن", f"{stats['total_value']:,.2f}", "fa5s.money-bill-wave", "#27ae60", 0, 1)
        self.add_card(cards_layout, "نواقص (إعادة طلب)", str(stats['reorder_count']), "fa5s.shopping-cart", "#e74c3c", 0, 2)
        self.add_card(cards_layout, "أصناف منتهية", str(stats['expired_count']), "fa5s.calendar-times", "#c0392b", 0, 3)
        self.add_card(cards_layout, "تنتهي قريباً", str(stats['expiring_count']), "fa5s.calendar-day", "#f39c12", 0, 4)

        layout.addLayout(cards_layout)

        # 2. Financial Summary Row
        fin_layout = QHBoxLayout()
        fin_layout.setSpacing(20)
        self.add_stat_box(fin_layout, "إجمالي الوارد (قيمة المشتريات)", f"{stats['total_in']:,.2f}", "#2ecc71", "fa5s.arrow-down")
        self.add_stat_box(fin_layout, "إجمالي الصادر (قيمة المنصرف)", f"{stats['total_out']:,.2f}", "#3498db", "fa5s.arrow-up")
        layout.addLayout(fin_layout)

        # 3. Performance Row
        perf_layout = QHBoxLayout()
        perf_layout.setSpacing(20)
        self.add_info_card(perf_layout, "المنتج الأكثر سحباً", stats['top_item'], "fa5s.fire", "#e67e22")
        self.add_info_card(perf_layout, "المورد الأكثر تعاملاً", stats['top_supplier'], "fa5s.handshake", "#9b59b6")
        layout.addLayout(perf_layout)

        # 4. Detailed Sections
        details_layout = QHBoxLayout()
        details_layout.setSpacing(20)

        # Stock Alerts
        stock_status_frame = QFrame()
        stock_status_frame.setObjectName("Card")
        ss_layout = QVBoxLayout(stock_status_frame)
        ss_title = QLabel("تنبيهات المخزون الحرجة")
        ss_title.setObjectName("CardTitle")
        ss_layout.addWidget(ss_title)

        low_items = stats['stock_status'][:8]
        if not low_items:
            ss_layout.addWidget(QLabel("لا توجد نواقص حالياً"))
        else:
            for item in low_items:
                i_layout = QHBoxLayout()
                i_layout.addWidget(QLabel(item['name']))
                progress = QProgressBar()
                progress.setMaximum(item['min_stock'] * 2 if item['min_stock'] > 0 else 100)
                progress.setValue(item['current_stock'])
                progress.setFormat(f"{item['current_stock']} / {item['min_stock']}")
                progress.setStyleSheet("QProgressBar::chunk { background-color: #e74c3c; }")
                i_layout.addWidget(progress)
                ss_layout.addLayout(i_layout)
        ss_layout.addStretch()
        details_layout.addWidget(stock_status_frame, 1)

        # Expiry Alerts
        expiry_frame = QFrame()
        expiry_frame.setObjectName("Card")
        ex_layout = QVBoxLayout(expiry_frame)
        ex_title = QLabel("أصناف تنتهي صلاحيتها قريباً")
        ex_title.setObjectName("CardTitle")
        ex_layout.addWidget(ex_title)

        ex_table = QTableWidget()
        ex_table.setColumnCount(4)
        ex_table.setHorizontalHeaderLabels(["الصنف", "الكود", "تاريخ الانتهاء", "متبقي (شهر)"])
        ex_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        ex_table.verticalHeader().setVisible(False)
        ex_table.setRowCount(len(stats['expiring_items']))
        for r, item in enumerate(stats['expiring_items']):
            ex_table.setItem(r, 0, QTableWidgetItem(str(item['name'])))
            ex_table.setItem(r, 1, QTableWidgetItem(str(item['code'])))
            ex_table.setItem(r, 2, QTableWidgetItem(str(item['expiry_date'])))
            months = int(item['months_left'])
            ex_table.setItem(r, 3, QTableWidgetItem(str(months)))
        ex_layout.addWidget(ex_table)
        details_layout.addWidget(expiry_frame, 2)

        # Reorder Suggestions
        reorder_frame = QFrame()
        reorder_frame.setObjectName("Card")
        re_layout = QVBoxLayout(reorder_frame)
        re_title = QLabel("مقترحات إعادة الطلب")
        re_title.setObjectName("CardTitle")
        re_layout.addWidget(re_title)

        re_table = QTableWidget()
        re_table.setColumnCount(4)
        re_table.setHorizontalHeaderLabels(["الصنف", "المخزون", "الحد الأدنى", "المورد"])
        re_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        re_table.verticalHeader().setVisible(False)
        re_table.setRowCount(len(stats['reorder_items']))
        for r, item in enumerate(stats['reorder_items']):
            re_table.setItem(r, 0, QTableWidgetItem(item['name']))
            re_table.setItem(r, 1, QTableWidgetItem(str(item['current_stock'])))
            re_table.setItem(r, 2, QTableWidgetItem(str(item['min_stock'])))
            re_table.setItem(r, 3, QTableWidgetItem(item['supplier_name'] or "N/A"))
        re_layout.addWidget(re_table)
        details_layout.addWidget(reorder_frame, 2)

        # Recent Activity
        activity_frame = QFrame()
        activity_frame.setObjectName("Card")
        act_layout = QVBoxLayout(activity_frame)
        act_title = QLabel("سجل النشاط الأخير")
        act_title.setObjectName("CardTitle")
        act_layout.addWidget(act_title)

        self.activity_table = QTableWidget()
        self.activity_table.setColumnCount(3)
        self.activity_table.setHorizontalHeaderLabels(["الوقت", "المستخدم", "العملية"])
        self.activity_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.activity_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.activity_table.setSelectionMode(QTableWidget.NoSelection)
        self.activity_table.verticalHeader().setVisible(False)
        self.activity_table.setStyleSheet("border: none; background: transparent;")

        logs = self.controller.get_recent_activities()
        self.activity_table.setRowCount(len(logs))
        for row, log in enumerate(logs):
            ts = log['timestamp']
            if hasattr(ts, 'strftime'):
                time_str = ts.strftime("%H:%M:%S")
            else:
                ts_str = str(ts)
                time_str = ts_str.split()[1] if ' ' in ts_str else ts_str

            self.activity_table.setItem(row, 0, QTableWidgetItem(time_str))
            self.activity_table.setItem(row, 1, QTableWidgetItem(log['user_name'] or "النظام"))
            self.activity_table.setItem(row, 2, QTableWidgetItem(log['action']))

        act_layout.addWidget(self.activity_table)
        details_layout.addWidget(activity_frame, 2)

        layout.addLayout(details_layout)

        scroll.setWidget(content_widget)
        self.main_layout.addWidget(scroll)

    def add_card(self, layout, title, value, icon, color, r, c):
        card = QFrame()
        card.setObjectName("Card")
        card.setMinimumHeight(150) # Taller cards
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(25, 25, 25, 25)

        icon_label = QLabel()
        icon_label.setPixmap(qta.icon(icon, color=color).pixmap(65, 65)) # Larger icons
        card_layout.addWidget(icon_label)

        text_layout = QVBoxLayout()
        t_label = QLabel(title)
        t_label.setObjectName("CardTitle")
        t_label.setStyleSheet("font-size: 18px;")
        v_label = QLabel(value)
        v_label.setObjectName("CardValue")
        v_label.setStyleSheet(f"color: {color}; font-size: 32px;") # Larger value font

        text_layout.addWidget(t_label)
        text_layout.addWidget(v_label)
        card_layout.addLayout(text_layout)
        layout.addWidget(card, r, c)

    def add_stat_box(self, layout, title, value, color, icon):
        box = QFrame()
        box.setObjectName("Card")
        box.setStyleSheet(f"border-right: 5px solid {color};")
        l = QVBoxLayout(box)
        t = QLabel(title)
        t.setObjectName("CardTitle")
        v = QHBoxLayout()
        v_val = QLabel(value)
        v_val.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {color};")
        v_icon = QLabel()
        v_icon.setPixmap(qta.icon(icon, color=color).pixmap(24, 24))
        v.addWidget(v_val)
        v.addStretch()
        v.addWidget(v_icon)
        l.addWidget(t)
        l.addLayout(v)
        layout.addWidget(box)

    def add_info_card(self, layout, title, value, icon, color):
        card = QFrame()
        card.setObjectName("Card")
        l = QVBoxLayout(card)

        header = QHBoxLayout()
        h_icon = QLabel()
        h_icon.setPixmap(qta.icon(icon, color=color).pixmap(20, 20))
        h_title = QLabel(title)
        h_title.setStyleSheet("font-size: 13px; color: #7f8c8d; font-weight: bold;")
        header.addWidget(h_icon)
        header.addWidget(h_title)
        header.addStretch()

        v_label = QLabel(value)
        v_label.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {color}; margin-top: 5px;")
        v_label.setWordWrap(True)

        l.addLayout(header)
        l.addWidget(v_label)
        layout.addWidget(card)
