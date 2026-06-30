from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableView,
                             QPushButton, QLabel, QHeaderView, QTabWidget, QGroupBox)
from PySide6.QtCore import Qt, QThreadPool
from views_components.enterprise_table_model import EnterpriseTableModel
from workers.worker import Worker
from utils.translation_manager import tr, tr_manager

class AccountingView(QWidget):
    def __init__(self, service):
        super().__init__()
        self.service = service
        self.threadpool = QThreadPool.globalInstance()
        self.setup_ui()

    def setup_ui(self):
        self.setLayoutDirection(Qt.RightToLeft if tr_manager.is_rtl else Qt.LeftToRight)
        layout = QVBoxLayout(self)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # 0. Dashboard
        self.dash_tab = QWidget()
        self.setup_dash_tab()
        self.tabs.addTab(self.dash_tab, tr("dashboard"))

        # 1. Chart of Accounts
        self.coa_tab = QWidget()
        self.setup_coa_tab()
        self.tabs.addTab(self.coa_tab, tr("coa"))

        # 2. Journal Entries
        self.entries_tab = QWidget()
        self.setup_entries_tab()
        self.tabs.addTab(self.entries_tab, tr("journal_entries"))

        # 3. Trial Balance
        self.trial_tab = QWidget()
        self.setup_trial_tab()
        self.tabs.addTab(self.trial_tab, tr("trial_balance"))

    def setup_coa_tab(self):
        layout = QVBoxLayout(self.coa_tab)

        # Action Bar
        actions = QHBoxLayout()
        add_acc = QPushButton(tr("add_item")) # Re-using key for "Add Account"
        add_acc.setObjectName("PrimaryButton")
        actions.addWidget(add_acc)
        actions.addStretch()
        layout.addLayout(actions)

        self.coa_view = QTableView()
        self.coa_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.coa_view.setAlternatingRowColors(True)
        self.coa_view.setStyleSheet("QTableView { background-color: #1a1c23; color: white; }")
        layout.addWidget(self.coa_view)

        headers = ["code", "name", "type", "active"]
        translated = [tr("code"), tr("item_name"), tr("type"), tr("status")]
        self.coa_model = EnterpriseTableModel([], headers, translated)
        self.coa_view.setModel(self.coa_model)

    def setup_entries_tab(self):
        layout = QVBoxLayout(self.entries_tab)
        self.entries_view = QTableView()
        self.entries_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.entries_view)

        headers = ["date", "name", "ref", "state"]
        translated = [tr("date"), tr("id"), tr("invoice_no"), tr("status")]
        self.entries_model = EnterpriseTableModel([], headers, translated)
        self.entries_view.setModel(self.entries_model)

    def setup_trial_tab(self):
        layout = QVBoxLayout(self.trial_tab)
        self.trial_view = QTableView()
        self.trial_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.trial_view)

        headers = ["account", "debit", "credit", "balance"]
        self.trial_model = EnterpriseTableModel([], headers, headers)
        self.trial_view.setModel(self.trial_model)

    def refresh(self):
        # Refresh COA
        worker = Worker(self.service.get_accounts)
        worker.signals.result.connect(self.on_coa_loaded)
        self.threadpool.start(worker)

    def setup_dash_tab(self):
        layout = QVBoxLayout(self.dash_tab)
        layout.setContentsMargins(30, 30, 30, 30)

        from PySide6.QtCharts import QChart, QChartView, QPieSeries
        from PySide6.QtGui import QPainter

        self.chart = QChart()
        self.chart.setTitle(tr("financial_summary"))
        self.chart.setAnimationOptions(QChart.SeriesAnimations)
        self.chart.setBackgroundBrush(Qt.NoBrush)

        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.chart_view.setMinimumHeight(400)

        self.dash_group = QGroupBox(tr("financial_summary"))
        self.dash_group.setStyleSheet("QGroupBox { font-size: 18px; color: #d4af37; border: 1px solid #333; padding-top: 25px; }")
        gl = QVBoxLayout(self.dash_group)

        stat_h = QHBoxLayout()
        self.income_lbl = QLabel("Income: $0.00")
        self.income_lbl.setStyleSheet("color: #27ae60; font-size: 22px; font-weight: bold;")
        self.expense_lbl = QLabel("Expense: $0.00")
        self.expense_lbl.setStyleSheet("color: #e74c3c; font-size: 22px; font-weight: bold;")
        self.profit_lbl = QLabel("Net Profit: $0.00")
        self.profit_lbl.setStyleSheet("color: #d4af37; font-size: 28px; font-weight: 1000;")

        stat_h.addWidget(self.income_lbl)
        stat_h.addStretch()
        stat_h.addWidget(self.expense_lbl)
        stat_h.addStretch()
        stat_h.addWidget(self.profit_lbl)

        gl.addLayout(stat_h)
        gl.addWidget(self.chart_view)

        layout.addWidget(self.dash_group)

    def refresh(self):
        # Refresh COA
        worker = Worker(self.service.get_accounts)
        worker.signals.result.connect(self.on_coa_loaded)
        self.threadpool.start(worker)

        # Refresh P&L
        worker_pl = Worker(self.service.get_profit_loss)
        worker_pl.signals.result.connect(self.on_pl_loaded)
        self.threadpool.start(worker_pl)

    def on_pl_loaded(self, pl_data):
        self.income_lbl.setText(f"{tr('inbound')}: ${pl_data['income']:,.2f}")
        self.expense_lbl.setText(f"{tr('outbound')}: ${pl_data['expense']:,.2f}")
        self.profit_lbl.setText(f"{tr('net_profit')}: ${pl_data['net_profit']:,.2f}")

        # Update Chart
        from PySide6.QtCharts import QPieSeries
        self.chart.removeAllSeries()
        series = QPieSeries()
        series.append(tr("inbound"), pl_data['income'])
        series.append(tr("outbound"), pl_data['expense'])
        if series.count() > 0:
            series.slices()[0].setBrush(Qt.green)
            series.slices()[1].setBrush(Qt.red)
        self.chart.addSeries(series)

    def on_coa_loaded(self, accounts):
        data = [{"code": a.code, "name": a.name, "type": a.type, "active": str(a.active)} for a in accounts]
        self.coa_model.update_data(data)
