from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                             QPushButton, QLabel, QGridLayout, QMessageBox,
                             QFrame, QScrollArea)
from PySide6.QtCore import Qt
from PySide6.QtCharts import QChart, QChartView, QBarSet, QBarSeries, QBarCategoryAxis, QValueAxis, QPieSeries, QPieSlice
from PySide6.QtGui import QPainter, QLinearGradient, QGradient, QColor
import qtawesome as qta
from utils.translation_manager import tr, tr_manager

class DashboardView(QWidget):
    def __init__(self, service):
        super().__init__()
        self.service = service
        self.setup_ui()

    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Scroll Area for high-density data
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        self.scroll_content = QWidget()
        layout = QVBoxLayout(self.scroll_content)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(35)
        scroll.setWidget(self.scroll_content)
        self.main_layout.addWidget(scroll)

        # Header with Logo/Title
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: #111; border-bottom: 2px solid #d4af37; padding: 10px;")
        header_h = QHBoxLayout(header_frame)

        logo_icon = QLabel()
        logo_icon.setPixmap(qta.icon("fa5s.shield-alt", color="#d4af37").pixmap(45, 45))
        header_h.addWidget(logo_icon)

        header_title = QLabel("AMERICAN MARINE SERVICES FREEZONE")
        header_title.setStyleSheet("font-size: 28px; font-weight: 900; color: #d4af37; letter-spacing: 2px;")
        header_h.addWidget(header_title)

        header_h.addStretch()

        control_label = QLabel(tr("system_subtitle").upper())
        control_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #7f8c8d; border: 1px solid #333; padding: 5px 15px; border-radius: 15px;")
        header_h.addWidget(control_label)

        layout.addWidget(header_frame)

        # Top Stats Cards
        stats_h_layout = QHBoxLayout()
        stats_h_layout.setSpacing(20)

        self.total_items_card = self.create_stat_card(tr("total_items"), "0", "fa5s.boxes", "#1a2a6c")
        self.low_stock_card = self.create_stat_card(tr("low_stock"), "0", "fa5s.exclamation-triangle", "#e74c3c")
        self.expiring_card = self.create_stat_card(tr("expiring_soon"), "0", "fa5s.calendar-times", "#f39c12")
        self.total_value_card = self.create_stat_card(tr("total_value"), "0.00", "fa5s.money-bill-wave", "#27ae60")
        self.weekly_activity_card = self.create_stat_card(tr("weekly_activity"), "0/0", "fa5s.exchange-alt", "#2980b9")
        self.aging_items_card = self.create_stat_card(tr("aging_items"), "0", "fa5s.history", "#9b59b6")

        stats_h_layout.addWidget(self.total_items_card)
        stats_h_layout.addWidget(self.low_stock_card)
        stats_h_layout.addWidget(self.expiring_card)
        stats_h_layout.addWidget(self.total_value_card)
        stats_h_layout.addWidget(self.weekly_activity_card)
        stats_h_layout.addWidget(self.aging_items_card)
        layout.addLayout(stats_h_layout)

        # Middle Section (Charts)
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(30)

        # Bar Chart for 7-day trend
        self.activity_chart = QChart()
        self.activity_chart.setTitle(tr("activity_7d"))
        self.activity_chart.setAnimationOptions(QChart.SeriesAnimations)

        self.chart_view = QChartView(self.activity_chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.chart_view.setMinimumHeight(350)
        charts_layout.addWidget(self.chart_view, 2)

        # Pie Chart for Categories
        self.pie_chart = QChart()
        self.pie_chart.setTitle(tr("category_distribution"))
        self.pie_chart_view = QChartView(self.pie_chart)
        self.pie_chart_view.setRenderHint(QPainter.Antialiasing)
        self.pie_chart_view.setMinimumHeight(350)
        charts_layout.addWidget(self.pie_chart_view, 1)

        layout.addLayout(charts_layout)

        # Bottom Section: Alerts & Top Items
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(30)

        # Alerts
        alerts_frame = QFrame()
        alerts_frame.setStyleSheet("background-color: #1c1e26; border-radius: 15px; padding: 20px;")
        alerts_vbox = QVBoxLayout(alerts_frame)
        alerts_header = QLabel(tr("smart_alerts"))
        alerts_header.setStyleSheet("color: #d4af37; font-weight: bold; font-size: 14px;")
        alerts_vbox.addWidget(alerts_header)

        self.alerts_label = QLabel(tr("system_status_ok"))
        self.alerts_label.setStyleSheet("color: #27ae60; font-size: 16px; font-weight: bold;")
        self.alerts_label.setWordWrap(True)
        alerts_vbox.addWidget(self.alerts_label)
        alerts_vbox.addStretch()
        bottom_layout.addWidget(alerts_frame, 1)

        # Top Moving Items
        top_items_frame = QFrame()
        top_items_frame.setStyleSheet("background-color: #1c1e26; border-radius: 15px; padding: 20px;")
        top_vbox = QVBoxLayout(top_items_frame)
        top_header = QLabel(tr("top_moving_items"))
        top_header.setStyleSheet("color: #d4af37; font-weight: bold; font-size: 14px;")
        top_vbox.addWidget(top_header)

        self.top_items_list = QVBoxLayout()
        top_vbox.addLayout(self.top_items_list)
        top_vbox.addStretch()
        bottom_layout.addWidget(top_items_frame, 1)

        layout.addLayout(bottom_layout)

        layout.addStretch()
        self.refresh()

    def create_stat_card(self, title, value, icon, color):
        card = QFrame()
        card.setObjectName("ProStatCard")
        card.setMinimumHeight(130)
        card.setStyleSheet(f"""
            QFrame#ProStatCard {{
                background-color: #1c1e26;
                border-left: 5px solid {color};
                border-radius: 12px;
                padding: 15px;
            }}
        """)

        card_layout = QHBoxLayout(card)

        text_layout = QVBoxLayout()
        title_label = QLabel(title.upper())
        title_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #95a5a6;")

        val_label = QLabel(value)
        val_label.setStyleSheet(f"font-size: 32px; font-weight: 900; color: #ecf0f1;")
        val_label.setObjectName("ValueLabel")

        text_layout.addWidget(title_label)
        text_layout.addStretch()
        text_layout.addWidget(val_label)

        card_layout.addLayout(text_layout)
        card_layout.addStretch()

        icon_label = QLabel()
        icon_label.setPixmap(qta.icon(icon, color=color).pixmap(55, 55))
        card_layout.addWidget(icon_label)

        return card

    def refresh(self):
        try:
            stats = self.service.get_stats()

            # Update Cards
            self.total_items_card.findChild(QLabel, "ValueLabel").setText(str(stats.get('total_items', 0)))
            self.low_stock_card.findChild(QLabel, "ValueLabel").setText(str(stats.get('low_stock', 0)))
            self.expiring_card.findChild(QLabel, "ValueLabel").setText(str(stats.get('expiring_soon', 0)))
            self.total_value_card.findChild(QLabel, "ValueLabel").setText(f"{stats.get('total_value', 0):,.2f}")
            self.aging_items_card.findChild(QLabel, "ValueLabel").setText(str(stats.get('aging_items', 0)))

            # Calculate weekly summary
            trends = stats.get('trends', [])
            total_in = sum(t['in'] for t in trends)
            total_out = sum(t['out'] for t in trends)
            self.weekly_activity_card.findChild(QLabel, "ValueLabel").setText(f"{int(total_in)} / {int(total_out)}")

            # Update Bar Chart (Detailed Daily Trend)
            self.activity_chart.removeAllSeries()
            set_in = QBarSet(tr("inbound"))
            set_out = QBarSet(tr("outbound"))

            categories = []
            for t in trends:
                set_in.append(t['in'])
                set_out.append(t['out'])
                categories.append(t['date'])

            series = QBarSeries()
            series.append(set_in)
            series.append(set_out)
            self.activity_chart.addSeries(series)

            # Re-create axes for the chart
            self.activity_chart.createDefaultAxes()
            axis_x = QBarCategoryAxis()
            axis_x.append(categories)
            self.activity_chart.setAxisX(axis_x, series)

            # Update Pie Chart (Categories)
            self.pie_chart.removeAllSeries()
            pie_series = QPieSeries()
            cat_dist = stats.get('category_dist', {})
            for cat, count in cat_dist.items():
                slice = pie_series.append(f"{cat}", count)
                slice.setLabelVisible(True)

            if pie_series.count() > 0:
                self.pie_chart.addSeries(pie_series)

            # Update Alerts
            alert_text = []
            if stats.get('low_stock', 0) > 0:
                alert_text.append(f"⚠️ {tr('low_stock_alert')}: {stats['low_stock']}")
            if stats.get('expiring_soon', 0) > 0:
                alert_text.append(f"⏰ {tr('expiring_soon_alert')}: {stats['expiring_soon']}")

            if alert_text:
                self.alerts_label.setText("\n".join(alert_text))
                self.alerts_label.setStyleSheet("color: #e74c3c; font-weight: bold; font-size: 16px;")
            else:
                self.alerts_label.setText(tr("system_status_ok"))
                self.alerts_label.setStyleSheet("color: #27ae60; font-weight: bold; font-size: 16px;")

            # Update Top Items
            while self.top_items_list.count():
                child = self.top_items_list.takeAt(0)
                if child.widget(): child.widget().deleteLater()

            for item in stats.get('top_moving', []):
                item_row = QLabel(f"• {item['name']} ({int(item['value'])} units)")
                item_row.setStyleSheet("color: #ecf0f1; font-size: 13px; padding: 2px;")
                self.top_items_list.addWidget(item_row)

        except Exception as e:
            from app_logging.app_logger import app_logger
            app_logger.error(f"Dashboard refresh error: {e}")
