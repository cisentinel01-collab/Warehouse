from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QStackedWidget, QMessageBox, QFrame)
from PySide6.QtCore import Qt, QSize
import qtawesome as qta

from views.dashboard_view import DashboardView
from views.items_view import ItemsView
from views.suppliers_view import SuppliersView
from views.stock_operations_view import StockOperationsView
from views.reports_view import ReportsView
from views.user_management_view import UserManagementView
from views.settings_view import SettingsView
from views.purchase_view import PurchaseView
from views.locations_view import LocationsView
from views.device_management_view import DeviceManagementView

from services.dashboard_service import DashboardService


from controllers.stock_controller import StockController
from controllers.report_controller import ReportController
from controllers.user_controller import UserController
from controllers.purchase_controller import PurchaseController
from controllers.device_controller import DeviceController
from services.report_service import ReportService


from services.item_service import ItemService
from services.supplier_service import SupplierService
from database.session import Session

from utils.auth import AuthManager
from models.inventory import Batch
from views.expiry_alarm_dialog import ExpiryAlarmDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("نظام إدارة المخازن - American Marine Services")
        self.resize(1200, 800)
        self.setLayoutDirection(Qt.RightToLeft)

        self.db = Session()
        self.item_service = ItemService(self.db)
        self.supplier_service = SupplierService(self.db)

        self.setup_ui()
        # Cache Views
        self.dashboard_view = DashboardView(DashboardService(self.db))
        self.items_view = ItemsView(self.item_service)
        self.suppliers_view = SuppliersView(self.supplier_service)
        self.stock_in_view = StockOperationsView(StockController(self.db), "IN")
        self.stock_out_view = StockOperationsView(StockController(self.db), "OUT")
        self.reports_view = ReportsView(ReportController(self.db))
        self.users_view = UserManagementView(UserController(self.db))
        self.devices_view = DeviceManagementView(DeviceController(self.db))
        self.settings_view = SettingsView()
        self.locations_view = LocationsView()
        self.purchase_view = PurchaseView(PurchaseController(self.db))
        self.load_dashboard()
        self.check_expiry_alarm()

    def check_expiry_alarm(self):
        batch_model = Batch()
        expired = batch_model.get_expired()
        soon = batch_model.get_expiring_soon(6)

        if expired or soon:
            # Play alarm (simulated by popup and potential sound integration)
            # In a real desktop app, we'd use QSoundEffect
            dialog = ExpiryAlarmDialog(expired, soon, self)
            dialog.exec()

    def setup_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Sidebar
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 20, 0, 20)
        sidebar_layout.setSpacing(5)

        # Logo/Brand
        brand_label = QLabel("AMS WMS")
        brand_label.setStyleSheet("color: #d4af37; font-size: 24px; font-weight: bold; margin-bottom: 20px; padding: 10px;")
        brand_label.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(brand_label)

        self.nav_buttons = {}
        self.create_nav_button("dashboard", "الرئيسية", "fa5s.chart-line")
        self.create_nav_button("items", "الأصناف", "fa5s.boxes")
        self.create_nav_button("stock_in", "الوارد (المشتريات)", "fa5s.file-import")
        self.create_nav_button("stock_out", "الصادر (صرف)", "fa5s.file-export")
        self.create_nav_button("suppliers", "الموردين", "fa5s.truck")
        self.create_nav_button("locations", "المواقع", "fa5s.map-marker-alt")
        self.create_nav_button("purchase", "المشتريات", "fa5s.shopping-cart")
        self.create_nav_button("reports", "التقارير", "fa5s.file-alt")
        self.create_nav_button("users", "المستخدمين", "fa5s.users")
        self.create_nav_button("devices", "إدارة الأجهزة", "fa5s.desktop")
        self.create_nav_button("settings", "الإعدادات", "fa5s.cog")

        sidebar_layout.addStretch()

        logout_btn = QPushButton("تسجيل الخروج")
        logout_btn.setIcon(qta.icon("fa5s.sign-out-alt", color="white"))
        logout_btn.clicked.connect(self.handle_logout)
        sidebar_layout.addWidget(logout_btn)

        layout.addWidget(self.sidebar)

        # Content Area
        content_container = QWidget()
        self.content_layout = QVBoxLayout(content_container)
        self.content_layout.setContentsMargins(0, 0, 0, 0)

        # Header
        header = QFrame()
        header.setObjectName("Header")
        header_layout = QHBoxLayout(header)
        self.page_title = QLabel("الرئيسية")
        header_layout.addWidget(self.page_title)
        header_layout.addStretch()

        user = AuthManager.get_current_user()
        user_info = QLabel(f"مرحباً، {user['full_name'] if user else ''}")
        header_layout.addWidget(user_info)

        self.content_layout.addWidget(header)

        # Stacked Widget for pages
        self.stack = QStackedWidget()
        self.content_layout.addWidget(self.stack)

        layout.addWidget(content_container)

    def animate_page_switch(self, widget):
        self.stack.addWidget(widget)
        self.stack.setCurrentWidget(widget)

    def create_nav_button(self, id, text, icon_name):
        if not AuthManager.has_permission(id):
            return

        btn = QPushButton(text)
        btn.setIcon(qta.icon(icon_name, color="white"))
        btn.setIconSize(QSize(20, 20))
        btn.setCheckable(True)
        btn.setAutoExclusive(True)
        btn.clicked.connect(lambda: self.switch_page(id))
        self.sidebar.layout().addWidget(btn)
        self.nav_buttons[id] = btn

    def switch_page(self, page_id):
        self.nav_buttons[page_id].setChecked(True)
        self.page_title.setText(self.nav_buttons[page_id].text())

        # Reuse cached views to improve performance
        if page_id == "dashboard":
            view = self.dashboard_view
        elif page_id == "items":
            view = self.items_view
        elif page_id == "suppliers":
            view = self.suppliers_view
        elif page_id == "stock_in":
            view = self.stock_in_view
        elif page_id == "stock_out":
            view = self.stock_out_view
        elif page_id == "reports":
            view = self.reports_view
        elif page_id == "users":
            view = self.users_view
        elif page_id == "devices":
            view = self.devices_view
        elif page_id == "settings":
            view = self.settings_view
        elif page_id == "locations":
            view = self.locations_view
        elif page_id == "purchase":
            view = self.purchase_view
        else:
            return

        # Ensure fresh data if view has a refresh/load method
        if hasattr(view, 'refresh'):
            view.refresh()
        elif hasattr(view, 'load_history'):
            view.load_history()
        elif hasattr(view, 'load_data'):
            view.load_data()

        # Update stacked widget only if view changed
        if self.stack.currentWidget() != view:
            # Check if view is already in stack
            if self.stack.indexOf(view) == -1:
                self.stack.addWidget(view)
            self.stack.setCurrentWidget(view)

    def load_dashboard(self):
        if "dashboard" in self.nav_buttons:
            self.switch_page("dashboard")

    def handle_logout(self):
        AuthManager.logout()
        from views.login_view import LoginView
        self.login_window = LoginView()
        self.login_window.show()
        self.close()
