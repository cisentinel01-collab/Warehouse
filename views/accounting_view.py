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
        self.coa_view = QTableView()
        self.coa_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
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

    def on_coa_loaded(self, accounts):
        data = [{"code": a.code, "name": a.name, "type": a.type, "active": str(a.active)} for a in accounts]
        self.coa_model.update_data(data)
