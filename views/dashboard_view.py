from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                             QPushButton, QLabel, QGridLayout, QMessageBox)
from PySide6.QtCore import Qt
import qtawesome as qta

class DashboardView(QWidget):
    def __init__(self, service):
        super().__init__()
        self.service = service
        self.setup_ui()

    def setup_ui(self):
        from PySide6.QtCharts import QChart, QChartView, QBarSet, QBarSeries, QBarCategoryAxis, QValueAxis, QPieSeries
        from PySide6.QtGui import QPainter

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(30)

        # Header
        header = QLabel("لوحة التحكم الذكية - Smart Dashboard")
        header.setStyleSheet("font-size: 28px; font-weight: bold; color: #d4af37;")
        layout.addWidget(header)

        # Top Stats Cards
        stats_h_layout = QHBoxLayout()
        stats_h_layout.setSpacing(20)

        self.total_items_card = self.create_stat_card("إجمالي الأصناف", "0", "fa5s.boxes", "#1a2a6c")
        self.low_stock_card = self.create_stat_card("النواقص", "0", "fa5s.exclamation-triangle", "#e74c3c")
        self.expiring_card = self.create_stat_card("أصناف قاربت الانتهاء", "0", "fa5s.calendar-times", "#f39c12")
        self.total_value_card = self.create_stat_card("قيمة المخزون", "0.00", "fa5s.money-bill-wave", "#27ae60")
        self.weekly_activity_card = self.create_stat_card("حركات الأسبوع (IN/OUT)", "0/0", "fa5s.exchange-alt", "#2980b9")

        stats_h_layout.addWidget(self.total_items_card)
        stats_h_layout.addWidget(self.low_stock_card)
        stats_h_layout.addWidget(self.expiring_card)
        stats_h_layout.addWidget(self.total_value_card)
        stats_h_layout.addWidget(self.weekly_activity_card)
        layout.addLayout(stats_h_layout)

        # Middle Section (Charts)
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(30)

        # Bar Chart for 7-day trend
        self.activity_chart = QChart()
        self.activity_chart.setTitle("نشاط المخزن (آخر 7 أيام)")
        self.activity_chart.setAnimationOptions(QChart.SeriesAnimations)

        self.chart_view = QChartView(self.activity_chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.chart_view.setMinimumHeight(350)
        charts_layout.addWidget(self.chart_view, 2)

        # Pie Chart for Categories
        self.pie_chart = QChart()
        self.pie_chart.setTitle("توزيع الأصناف حسب الفئات")
        self.pie_chart_view = QChartView(self.pie_chart)
        self.pie_chart_view.setRenderHint(QPainter.Antialiasing)
        self.pie_chart_view.setMinimumHeight(350)
        charts_layout.addWidget(self.pie_chart_view, 1)

        layout.addLayout(charts_layout)

        # Bottom Section: Alerts & Quick Actions
        bottom_layout = QHBoxLayout()

        alerts_group = QGroupBox("تنبيهات النظام الذكية")
        alerts_vbox = QVBoxLayout(alerts_group)
        self.alerts_label = QLabel("لا توجد تنبيهات عاجلة حالياً.")
        self.alerts_label.setStyleSheet("color: #7f8c8d; font-size: 14px;")
        alerts_vbox.addWidget(self.alerts_label)
        bottom_layout.addWidget(alerts_group)

        layout.addLayout(bottom_layout)

        layout.addStretch()
        self.refresh()

    def create_stat_card(self, title, value, icon, color):
        card = QGroupBox()
        card.setObjectName("StatCard")
        card.setStyleSheet(f"QGroupBox#StatCard {{ border: 2px solid {color}; border-radius: 15px; background: white; padding: 20px; }}")

        card_layout = QHBoxLayout(card)

        icon_label = QLabel()
        icon_label.setPixmap(qta.icon(icon, color=color).pixmap(50, 50))

        text_layout = QVBoxLayout()
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 16px; color: #7f8c8d;")

        val_label = QLabel(value)
        val_label.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {color};")
        val_label.setObjectName("ValueLabel")

        text_layout.addWidget(title_label)
        text_layout.addWidget(val_label)

        card_layout.addLayout(text_layout)
        card_layout.addStretch()
        card_layout.addWidget(icon_label)

        return card

    def refresh(self):
        from PySide6.QtCharts import QBarSet, QBarSeries, QBarCategoryAxis, QValueAxis, QPieSeries, QPieSlice
        try:
            stats = self.service.get_stats()

            # Update Cards
            self.total_items_card.findChild(QLabel, "ValueLabel").setText(str(stats.get('total_items', 0)))
            self.low_stock_card.findChild(QLabel, "ValueLabel").setText(str(stats.get('low_stock', 0)))
            self.expiring_card.findChild(QLabel, "ValueLabel").setText(str(stats.get('expiring_soon', 0)))
            self.total_value_card.findChild(QLabel, "ValueLabel").setText(f"{stats.get('total_value', 0):,.2f}")
            self.weekly_activity_card.findChild(QLabel, "ValueLabel").setText(
                f"{stats.get('inbound_7d', 0)} / {stats.get('outbound_7d', 0)}"
            )

            # Update Bar Chart (Movement Trend)
            self.activity_chart.removeAllSeries()
            set_in = QBarSet("وارد")
            set_out = QBarSet("صادر")
            set_in.append(stats.get('inbound_7d', 0))
            set_out.append(stats.get('outbound_7d', 0))

            series = QBarSeries()
            series.append(set_in)
            series.append(set_out)
            self.activity_chart.addSeries(series)

            # Update Pie Chart (Categories)
            self.pie_chart.removeAllSeries()
            pie_series = QPieSeries()
            cat_dist = stats.get('category_dist', {})
            for cat, count in cat_dist.items():
                pie_series.append(f"{cat or 'غير مصنف'}", count)

            if pie_series.count() > 0:
                self.pie_chart.addSeries(pie_series)

            # Update Alerts
            alert_text = []
            if stats.get('low_stock', 0) > 0:
                alert_text.append(f"⚠️ يوجد {stats['low_stock']} صنف تحت حد الطلب.")
            if stats.get('expiring_soon', 0) > 0:
                alert_text.append(f"⏰ {stats['expiring_soon']} أصناف ستنتهي صلاحيتها قريباً.")

            if alert_text:
                self.alerts_label.setText("\n".join(alert_text))
                self.alerts_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
            else:
                self.alerts_label.setText("✅ النظام يعمل بكفاءة عالية، لا توجد مشاكل.")
                self.alerts_label.setStyleSheet("color: #27ae60;")

        except Exception as e:
            from app_logging.app_logger import app_logger
            app_logger.error(f"Dashboard refresh error: {e}")
