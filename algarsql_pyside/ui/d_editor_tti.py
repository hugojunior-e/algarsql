# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'd_editor_tti.ui'
##
## Created by: Qt User Interface Compiler version 6.10.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QFrame, QHBoxLayout,
    QHeaderView, QLabel, QPlainTextEdit, QPushButton,
    QSizePolicy, QSpacerItem, QSplitter, QTabWidget,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)

class Ui_d_editor_tti(object):
    def setupUi(self, d_editor_tti):
        if not d_editor_tti.objectName():
            d_editor_tti.setObjectName(u"d_editor_tti")
        d_editor_tti.resize(1247, 512)
        self.verticalLayout_5 = QVBoxLayout(d_editor_tti)
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.splitter = QSplitter(d_editor_tti)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Orientation.Vertical)
        self.verticalLayoutWidget = QWidget(self.splitter)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.editorLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.editorLayout.setObjectName(u"editorLayout")
        self.editorLayout.setContentsMargins(0, 0, 0, 0)
        self.splitter.addWidget(self.verticalLayoutWidget)
        self.pan_baixo = QWidget(self.splitter)
        self.pan_baixo.setObjectName(u"pan_baixo")
        self.verticalLayout_2 = QVBoxLayout(self.pan_baixo)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.pan_baixo_botoes = QFrame(self.pan_baixo)
        self.pan_baixo_botoes.setObjectName(u"pan_baixo_botoes")
        self.pan_baixo_botoes.setMinimumSize(QSize(0, 35))
        self.pan_baixo_botoes.setMaximumSize(QSize(16777215, 35))
        self.pan_baixo_botoes.setFrameShape(QFrame.Shape.NoFrame)
        self.pan_baixo_botoes.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout = QHBoxLayout(self.pan_baixo_botoes)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(2, 0, -1, 0)
        self.bt_tool_column = QPushButton(self.pan_baixo_botoes)
        self.bt_tool_column.setObjectName(u"bt_tool_column")
        self.bt_tool_column.setMinimumSize(QSize(60, 30))
        self.bt_tool_column.setMaximumSize(QSize(30, 16777215))

        self.horizontalLayout.addWidget(self.bt_tool_column)

        self.bt_tool_delete = QPushButton(self.pan_baixo_botoes)
        self.bt_tool_delete.setObjectName(u"bt_tool_delete")
        self.bt_tool_delete.setMinimumSize(QSize(60, 30))
        self.bt_tool_delete.setMaximumSize(QSize(30, 16777215))

        self.horizontalLayout.addWidget(self.bt_tool_delete)

        self.bt_fetch = QPushButton(self.pan_baixo_botoes)
        self.bt_fetch.setObjectName(u"bt_fetch")
        self.bt_fetch.setMinimumSize(QSize(60, 30))
        self.bt_fetch.setMaximumSize(QSize(30, 16777215))

        self.horizontalLayout.addWidget(self.bt_fetch)

        self.bt_tool_clip = QPushButton(self.pan_baixo_botoes)
        self.bt_tool_clip.setObjectName(u"bt_tool_clip")
        self.bt_tool_clip.setMinimumSize(QSize(60, 30))
        self.bt_tool_clip.setMaximumSize(QSize(30, 16777215))

        self.horizontalLayout.addWidget(self.bt_tool_clip)

        self.bt_tool_csv = QPushButton(self.pan_baixo_botoes)
        self.bt_tool_csv.setObjectName(u"bt_tool_csv")
        self.bt_tool_csv.setMinimumSize(QSize(60, 30))
        self.bt_tool_csv.setMaximumSize(QSize(30, 16777215))

        self.horizontalLayout.addWidget(self.bt_tool_csv)

        self.bt_tool_insert = QPushButton(self.pan_baixo_botoes)
        self.bt_tool_insert.setObjectName(u"bt_tool_insert")
        self.bt_tool_insert.setMinimumSize(QSize(60, 30))
        self.bt_tool_insert.setMaximumSize(QSize(30, 16777215))

        self.horizontalLayout.addWidget(self.bt_tool_insert)

        self.bt_tool_descr_sql = QPushButton(self.pan_baixo_botoes)
        self.bt_tool_descr_sql.setObjectName(u"bt_tool_descr_sql")
        self.bt_tool_descr_sql.setMinimumSize(QSize(60, 30))
        self.bt_tool_descr_sql.setMaximumSize(QSize(30, 16777215))

        self.horizontalLayout.addWidget(self.bt_tool_descr_sql)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.chk_all_text = QCheckBox(self.pan_baixo_botoes)
        self.chk_all_text.setObjectName(u"chk_all_text")
        self.chk_all_text.setMinimumSize(QSize(150, 0))
        self.chk_all_text.setMaximumSize(QSize(150, 16777215))

        self.horizontalLayout.addWidget(self.chk_all_text)

        self.chk_run_user_local = QCheckBox(self.pan_baixo_botoes)
        self.chk_run_user_local.setObjectName(u"chk_run_user_local")
        self.chk_run_user_local.setMinimumSize(QSize(150, 0))
        self.chk_run_user_local.setMaximumSize(QSize(150, 16777215))

        self.horizontalLayout.addWidget(self.chk_run_user_local)

        self.chk_parameters = QCheckBox(self.pan_baixo_botoes)
        self.chk_parameters.setObjectName(u"chk_parameters")
        self.chk_parameters.setMinimumSize(QSize(150, 0))
        self.chk_parameters.setMaximumSize(QSize(150, 16777215))

        self.horizontalLayout.addWidget(self.chk_parameters)

        self.lb_timer = QLabel(self.pan_baixo_botoes)
        self.lb_timer.setObjectName(u"lb_timer")
        self.lb_timer.setMinimumSize(QSize(100, 0))
        self.lb_timer.setMaximumSize(QSize(100, 16777215))
        self.lb_timer.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout.addWidget(self.lb_timer)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)


        self.verticalLayout_2.addWidget(self.pan_baixo_botoes)

        self.pc_baixo_grid = QTabWidget(self.pan_baixo)
        self.pc_baixo_grid.setObjectName(u"pc_baixo_grid")
        self.pc_baixo_grid.setTabPosition(QTabWidget.TabPosition.South)
        self.pc_baixo_grid.setTabShape(QTabWidget.TabShape.Rounded)
        self.pc_baixo_grid.setTabBarAutoHide(False)
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.verticalLayout_3 = QVBoxLayout(self.tab)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.grid_select = QTableWidget(self.tab)
        self.grid_select.setObjectName(u"grid_select")
        self.grid_select.setAlternatingRowColors(True)

        self.verticalLayout_3.addWidget(self.grid_select)

        self.pc_baixo_grid.addTab(self.tab, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.verticalLayout_4 = QVBoxLayout(self.tab_2)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.mem_dbms = QPlainTextEdit(self.tab_2)
        self.mem_dbms.setObjectName(u"mem_dbms")
        font = QFont()
        font.setFamilies([u"Monospace"])
        self.mem_dbms.setFont(font)

        self.verticalLayout_4.addWidget(self.mem_dbms)

        self.pc_baixo_grid.addTab(self.tab_2, "")

        self.verticalLayout_2.addWidget(self.pc_baixo_grid)

        self.splitter.addWidget(self.pan_baixo)

        self.verticalLayout_5.addWidget(self.splitter)


        self.retranslateUi(d_editor_tti)

        self.pc_baixo_grid.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(d_editor_tti)
    # setupUi

    def retranslateUi(self, d_editor_tti):
        d_editor_tti.setWindowTitle(QCoreApplication.translate("d_editor_tti", u"Form", None))
        self.bt_tool_column.setText(QCoreApplication.translate("d_editor_tti", u"#", None))
        self.bt_tool_delete.setText(QCoreApplication.translate("d_editor_tti", u"-", None))
        self.bt_fetch.setText(QCoreApplication.translate("d_editor_tti", u"*", None))
        self.bt_tool_clip.setText(QCoreApplication.translate("d_editor_tti", u"copy", None))
        self.bt_tool_csv.setText(QCoreApplication.translate("d_editor_tti", u"csv", None))
        self.bt_tool_insert.setText(QCoreApplication.translate("d_editor_tti", u"sql", None))
        self.bt_tool_descr_sql.setText(QCoreApplication.translate("d_editor_tti", u"descr", None))
        self.chk_all_text.setText(QCoreApplication.translate("d_editor_tti", u"Run all SQL text", None))
        self.chk_run_user_local.setText(QCoreApplication.translate("d_editor_tti", u"Run User Local", None))
        self.chk_parameters.setText(QCoreApplication.translate("d_editor_tti", u"Disable \"&&\"", None))
        self.lb_timer.setText(QCoreApplication.translate("d_editor_tti", u"00:00:00", None))
        self.pc_baixo_grid.setTabText(self.pc_baixo_grid.indexOf(self.tab), QCoreApplication.translate("d_editor_tti", u"data", None))
        self.pc_baixo_grid.setTabText(self.pc_baixo_grid.indexOf(self.tab_2), QCoreApplication.translate("d_editor_tti", u"dbms", None))
    # retranslateUi

