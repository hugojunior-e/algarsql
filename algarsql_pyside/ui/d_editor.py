# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'd_editor.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDialog,
    QFrame, QGroupBox, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QPlainTextEdit, QPushButton,
    QSizePolicy, QSpacerItem, QSplitter, QTabWidget,
    QTableWidget, QTableWidgetItem, QTreeWidget, QTreeWidgetItem,
    QVBoxLayout, QWidget)

class Ui_d_editor(object):
    def setupUi(self, d_editor):
        if not d_editor.objectName():
            d_editor.setObjectName(u"d_editor")
        d_editor.resize(929, 594)
        d_editor.setModal(True)
        self.verticalLayout_10 = QVBoxLayout(d_editor)
        self.verticalLayout_10.setSpacing(0)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.verticalLayout_10.setContentsMargins(0, 0, 0, 0)
        self.tabWidget = QTabWidget(d_editor)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tab_editor = QWidget()
        self.tab_editor.setObjectName(u"tab_editor")
        self.verticalLayout = QVBoxLayout(self.tab_editor)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(9, 9, 9, 9)
        self.mem_editor = QPlainTextEdit(self.tab_editor)
        self.mem_editor.setObjectName(u"mem_editor")

        self.verticalLayout.addWidget(self.mem_editor)

        self.tabWidget.addTab(self.tab_editor, "")
        self.tab_session = QWidget()
        self.tab_session.setObjectName(u"tab_session")
        self.vboxLayout = QVBoxLayout(self.tab_session)
        self.vboxLayout.setSpacing(6)
        self.vboxLayout.setObjectName(u"vboxLayout")
        self.vboxLayout.setContentsMargins(9, 9, 9, 9)
        self.frame = QFrame(self.tab_session)
        self.frame.setObjectName(u"frame")
        self.frame.setMinimumSize(QSize(0, 30))
        self.frame.setFrameShape(QFrame.Shape.Box)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.bt_sessions_exec = QPushButton(self.frame)
        self.bt_sessions_exec.setObjectName(u"bt_sessions_exec")

        self.horizontalLayout.addWidget(self.bt_sessions_exec)

        self.cbo_sessions = QComboBox(self.frame)
        self.cbo_sessions.addItem("")
        self.cbo_sessions.addItem("")
        self.cbo_sessions.addItem("")
        self.cbo_sessions.setObjectName(u"cbo_sessions")

        self.horizontalLayout.addWidget(self.cbo_sessions)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.vboxLayout.addWidget(self.frame)

        self.tree_sessions = QTreeWidget(self.tab_session)
        __qtreewidgetitem = QTreeWidgetItem()
        __qtreewidgetitem.setText(0, u"1");
        self.tree_sessions.setHeaderItem(__qtreewidgetitem)
        self.tree_sessions.setObjectName(u"tree_sessions")
        self.tree_sessions.setAlternatingRowColors(True)

        self.vboxLayout.addWidget(self.tree_sessions)

        self.mem_sessions = QPlainTextEdit(self.tab_session)
        self.mem_sessions.setObjectName(u"mem_sessions")

        self.vboxLayout.addWidget(self.mem_sessions)

        self.tabWidget.addTab(self.tab_session, "")
        self.tab_explain = QWidget()
        self.tab_explain.setObjectName(u"tab_explain")
        self.verticalLayout_4 = QVBoxLayout(self.tab_explain)
        self.verticalLayout_4.setSpacing(6)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(9, 9, 9, 9)
        self.frame_3 = QFrame(self.tab_explain)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setMinimumSize(QSize(0, 30))
        self.frame_3.setFrameShape(QFrame.Shape.Box)
        self.frame_3.setFrameShadow(QFrame.Shadow.Raised)
        self.bt_explain = QPushButton(self.frame_3)
        self.bt_explain.setObjectName(u"bt_explain")
        self.bt_explain.setGeometry(QRect(1, 2, 80, 26))

        self.verticalLayout_4.addWidget(self.frame_3)

        self.mem_explain = QPlainTextEdit(self.tab_explain)
        self.mem_explain.setObjectName(u"mem_explain")

        self.verticalLayout_4.addWidget(self.mem_explain)

        self.tree_explain = QTreeWidget(self.tab_explain)
        __qtreewidgetitem1 = QTreeWidgetItem()
        __qtreewidgetitem1.setText(6, u"7");
        __qtreewidgetitem1.setText(5, u"6");
        __qtreewidgetitem1.setText(4, u"5");
        __qtreewidgetitem1.setText(3, u"4");
        __qtreewidgetitem1.setText(2, u"3");
        __qtreewidgetitem1.setText(1, u"2");
        __qtreewidgetitem1.setText(0, u"1");
        self.tree_explain.setHeaderItem(__qtreewidgetitem1)
        self.tree_explain.setObjectName(u"tree_explain")
        self.tree_explain.setColumnCount(7)

        self.verticalLayout_4.addWidget(self.tree_explain)

        self.tabWidget.addTab(self.tab_explain, "")
        self.tab_csv_updater = QWidget()
        self.tab_csv_updater.setObjectName(u"tab_csv_updater")
        self.verticalLayout_5 = QVBoxLayout(self.tab_csv_updater)
        self.verticalLayout_5.setSpacing(6)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.groupBox_5 = QGroupBox(self.tab_csv_updater)
        self.groupBox_5.setObjectName(u"groupBox_5")
        self.groupBox_5.setMinimumSize(QSize(0, 100))
        self.groupBox_5.setMaximumSize(QSize(16777215, 100))
        self.bt_csv_of = QPushButton(self.groupBox_5)
        self.bt_csv_of.setObjectName(u"bt_csv_of")
        self.bt_csv_of.setGeometry(QRect(596, 64, 32, 26))
        self.bt_csv_of.setMaximumSize(QSize(32, 16777215))
        self.bt_csv_populate = QPushButton(self.groupBox_5)
        self.bt_csv_populate.setObjectName(u"bt_csv_populate")
        self.bt_csv_populate.setGeometry(QRect(12, 32, 100, 26))
        self.bt_csv_populate.setMaximumSize(QSize(100, 16777215))
        self.chk_csv = QCheckBox(self.groupBox_5)
        self.chk_csv.setObjectName(u"chk_csv")
        self.chk_csv.setGeometry(QRect(118, 33, 510, 24))
        self.edt_csv_file = QLineEdit(self.groupBox_5)
        self.edt_csv_file.setObjectName(u"edt_csv_file")
        self.edt_csv_file.setGeometry(QRect(12, 64, 578, 26))

        self.verticalLayout_5.addWidget(self.groupBox_5)

        self.frame_5 = QFrame(self.tab_csv_updater)
        self.frame_5.setObjectName(u"frame_5")
        self.frame_5.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_5.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.frame_5)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.splitter = QSplitter(self.frame_5)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Orientation.Horizontal)
        self.grid_csv = QTableWidget(self.splitter)
        if (self.grid_csv.columnCount() < 1):
            self.grid_csv.setColumnCount(1)
        self.grid_csv.setObjectName(u"grid_csv")
        self.grid_csv.setMinimumSize(QSize(300, 0))
        self.grid_csv.setMaximumSize(QSize(300, 16777215))
        self.grid_csv.setAlternatingRowColors(True)
        self.grid_csv.setColumnCount(1)
        self.splitter.addWidget(self.grid_csv)
        self.mem_csv = QPlainTextEdit(self.splitter)
        self.mem_csv.setObjectName(u"mem_csv")
        font = QFont()
        font.setFamilies([u"Monospace"])
        self.mem_csv.setFont(font)
        self.mem_csv.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.mem_csv.setBackgroundVisible(False)
        self.splitter.addWidget(self.mem_csv)

        self.horizontalLayout_3.addWidget(self.splitter)


        self.verticalLayout_5.addWidget(self.frame_5)

        self.tabWidget.addTab(self.tab_csv_updater, "")
        self.tab_find_objects = QWidget()
        self.tab_find_objects.setObjectName(u"tab_find_objects")
        self.verticalLayout_3 = QVBoxLayout(self.tab_find_objects)
        self.verticalLayout_3.setSpacing(6)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(9, 9, 9, 9)
        self.groupBox_4 = QGroupBox(self.tab_find_objects)
        self.groupBox_4.setObjectName(u"groupBox_4")
        self.groupBox_4.setMinimumSize(QSize(0, 100))
        self.groupBox_4.setMaximumSize(QSize(16777215, 100))
        self.chk_obj_table = QCheckBox(self.groupBox_4)
        self.chk_obj_table.setObjectName(u"chk_obj_table")
        self.chk_obj_table.setGeometry(QRect(290, 30, 85, 24))
        self.chk_obj_table.setChecked(True)
        self.chk_obj_view = QCheckBox(self.groupBox_4)
        self.chk_obj_view.setObjectName(u"chk_obj_view")
        self.chk_obj_view.setGeometry(QRect(290, 50, 85, 24))
        self.chk_obj_view.setChecked(True)
        self.chk_obj_package = QCheckBox(self.groupBox_4)
        self.chk_obj_package.setObjectName(u"chk_obj_package")
        self.chk_obj_package.setGeometry(QRect(390, 30, 85, 24))
        self.chk_obj_package.setChecked(True)
        self.chk_obj_trigger = QCheckBox(self.groupBox_4)
        self.chk_obj_trigger.setObjectName(u"chk_obj_trigger")
        self.chk_obj_trigger.setGeometry(QRect(290, 70, 85, 24))
        self.chk_obj_trigger.setChecked(True)
        self.chk_obj_procedure = QCheckBox(self.groupBox_4)
        self.chk_obj_procedure.setObjectName(u"chk_obj_procedure")
        self.chk_obj_procedure.setGeometry(QRect(390, 70, 131, 24))
        self.chk_obj_procedure.setChecked(True)
        self.chk_obj_funcion = QCheckBox(self.groupBox_4)
        self.chk_obj_funcion.setObjectName(u"chk_obj_funcion")
        self.chk_obj_funcion.setGeometry(QRect(390, 50, 85, 24))
        self.chk_obj_funcion.setChecked(True)
        self.edt_objetos = QLineEdit(self.groupBox_4)
        self.edt_objetos.setObjectName(u"edt_objetos")
        self.edt_objetos.setGeometry(QRect(13, 53, 241, 26))
        self.label_3 = QLabel(self.groupBox_4)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(13, 33, 91, 18))
        self.bt_obj_viewcode = QPushButton(self.groupBox_4)
        self.bt_obj_viewcode.setObjectName(u"bt_obj_viewcode")
        self.bt_obj_viewcode.setGeometry(QRect(620, 40, 161, 41))
        self.chk_obj_sequence = QCheckBox(self.groupBox_4)
        self.chk_obj_sequence.setObjectName(u"chk_obj_sequence")
        self.chk_obj_sequence.setGeometry(QRect(510, 50, 85, 24))
        self.chk_obj_sequence.setChecked(True)

        self.verticalLayout_3.addWidget(self.groupBox_4)

        self.grid_objetos = QTableWidget(self.tab_find_objects)
        self.grid_objetos.setObjectName(u"grid_objetos")
        self.grid_objetos.setAlternatingRowColors(True)

        self.verticalLayout_3.addWidget(self.grid_objetos)

        self.tabWidget.addTab(self.tab_find_objects, "")
        self.tab_config = QWidget()
        self.tab_config.setObjectName(u"tab_config")
        self.verticalLayout_2 = QVBoxLayout(self.tab_config)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.groupBox_3 = QGroupBox(self.tab_config)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.groupBox_3.setMinimumSize(QSize(0, 200))
        self.groupBox_3.setMaximumSize(QSize(16777215, 200))
        self.label = QLabel(self.groupBox_3)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(20, 30, 121, 18))
        self.edt_cfg_oracle_dir = QLineEdit(self.groupBox_3)
        self.edt_cfg_oracle_dir.setObjectName(u"edt_cfg_oracle_dir")
        self.edt_cfg_oracle_dir.setGeometry(QRect(20, 50, 231, 26))
        self.label_2 = QLabel(self.groupBox_3)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(20, 80, 161, 18))
        self.edt_cfg_template_dir = QLineEdit(self.groupBox_3)
        self.edt_cfg_template_dir.setObjectName(u"edt_cfg_template_dir")
        self.edt_cfg_template_dir.setGeometry(QRect(20, 100, 231, 26))
        self.chk_cfg_run_user = QCheckBox(self.groupBox_3)
        self.chk_cfg_run_user.setObjectName(u"chk_cfg_run_user")
        self.chk_cfg_run_user.setGeometry(QRect(270, 103, 191, 24))
        self.bt_cfg_salvar = QPushButton(self.groupBox_3)
        self.bt_cfg_salvar.setObjectName(u"bt_cfg_salvar")
        self.bt_cfg_salvar.setGeometry(QRect(20, 130, 151, 41))
        self.label_5 = QLabel(self.groupBox_3)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setGeometry(QRect(270, 30, 161, 18))
        self.edt_cfg_output_dir = QLineEdit(self.groupBox_3)
        self.edt_cfg_output_dir.setObjectName(u"edt_cfg_output_dir")
        self.edt_cfg_output_dir.setGeometry(QRect(270, 50, 231, 26))

        self.verticalLayout_2.addWidget(self.groupBox_3)

        self.groupBox = QGroupBox(self.tab_config)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setMinimumSize(QSize(0, 0))
        self.groupBox.setMaximumSize(QSize(16777215, 16777215))
        self.groupBox.setFlat(False)
        self.verticalLayout_7 = QVBoxLayout(self.groupBox)
        self.verticalLayout_7.setSpacing(0)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.tabWidget_2 = QTabWidget(self.groupBox)
        self.tabWidget_2.setObjectName(u"tabWidget_2")
        self.tab_cfg_services_names = QWidget()
        self.tab_cfg_services_names.setObjectName(u"tab_cfg_services_names")
        self.verticalLayout_8 = QVBoxLayout(self.tab_cfg_services_names)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.mem_cfg_tns = QPlainTextEdit(self.tab_cfg_services_names)
        self.mem_cfg_tns.setObjectName(u"mem_cfg_tns")
        font1 = QFont()
        font1.setFamilies([u"Monospace"])
        font1.setPointSize(10)
        self.mem_cfg_tns.setFont(font1)
        self.mem_cfg_tns.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)

        self.verticalLayout_8.addWidget(self.mem_cfg_tns)

        self.tabWidget_2.addTab(self.tab_cfg_services_names, "")
        self.tab_cfg_users_saved = QWidget()
        self.tab_cfg_users_saved.setObjectName(u"tab_cfg_users_saved")
        self.verticalLayout_9 = QVBoxLayout(self.tab_cfg_users_saved)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.mem_cfg_tns_saved = QPlainTextEdit(self.tab_cfg_users_saved)
        self.mem_cfg_tns_saved.setObjectName(u"mem_cfg_tns_saved")
        self.mem_cfg_tns_saved.setFont(font1)
        self.mem_cfg_tns_saved.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)

        self.verticalLayout_9.addWidget(self.mem_cfg_tns_saved)

        self.tabWidget_2.addTab(self.tab_cfg_users_saved, "")

        self.verticalLayout_7.addWidget(self.tabWidget_2)


        self.verticalLayout_2.addWidget(self.groupBox)

        self.tabWidget.addTab(self.tab_config, "")
        self.tab_recall = QWidget()
        self.tab_recall.setObjectName(u"tab_recall")
        self.verticalLayout_6 = QVBoxLayout(self.tab_recall)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.groupBox_6 = QGroupBox(self.tab_recall)
        self.groupBox_6.setObjectName(u"groupBox_6")
        self.groupBox_6.setMinimumSize(QSize(0, 100))
        self.groupBox_6.setMaximumSize(QSize(16777215, 100))
        self.label_4 = QLabel(self.groupBox_6)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(160, 30, 81, 18))
        self.edt_recall = QLineEdit(self.groupBox_6)
        self.edt_recall.setObjectName(u"edt_recall")
        self.edt_recall.setGeometry(QRect(160, 50, 301, 26))
        self.label_6 = QLabel(self.groupBox_6)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setGeometry(QRect(10, 30, 81, 18))
        self.edt_recall_database = QLineEdit(self.groupBox_6)
        self.edt_recall_database.setObjectName(u"edt_recall_database")
        self.edt_recall_database.setGeometry(QRect(10, 50, 131, 26))

        self.verticalLayout_6.addWidget(self.groupBox_6)

        self.grid_recall = QTableWidget(self.tab_recall)
        if (self.grid_recall.columnCount() < 3):
            self.grid_recall.setColumnCount(3)
        __qtablewidgetitem = QTableWidgetItem()
        self.grid_recall.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.grid_recall.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.grid_recall.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        self.grid_recall.setObjectName(u"grid_recall")
        self.grid_recall.setAlternatingRowColors(True)
        self.grid_recall.setWordWrap(False)

        self.verticalLayout_6.addWidget(self.grid_recall)

        self.mem_recall = QPlainTextEdit(self.tab_recall)
        self.mem_recall.setObjectName(u"mem_recall")

        self.verticalLayout_6.addWidget(self.mem_recall)

        self.tabWidget.addTab(self.tab_recall, "")
        self.tab_importer = QWidget()
        self.tab_importer.setObjectName(u"tab_importer")
        self.verticalLayout_11 = QVBoxLayout(self.tab_importer)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.groupBox_7 = QGroupBox(self.tab_importer)
        self.groupBox_7.setObjectName(u"groupBox_7")
        self.groupBox_7.setMinimumSize(QSize(0, 100))
        self.groupBox_7.setMaximumSize(QSize(16777215, 100))

        self.verticalLayout_11.addWidget(self.groupBox_7)

        self.mem_sessions_2 = QPlainTextEdit(self.tab_importer)
        self.mem_sessions_2.setObjectName(u"mem_sessions_2")

        self.verticalLayout_11.addWidget(self.mem_sessions_2)

        self.grid_objetos_2 = QTableWidget(self.tab_importer)
        self.grid_objetos_2.setObjectName(u"grid_objetos_2")
        self.grid_objetos_2.setAlternatingRowColors(True)

        self.verticalLayout_11.addWidget(self.grid_objetos_2)

        self.tabWidget.addTab(self.tab_importer, "")

        self.verticalLayout_10.addWidget(self.tabWidget)


        self.retranslateUi(d_editor)

        self.tabWidget.setCurrentIndex(5)
        self.tabWidget_2.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(d_editor)
    # setupUi

    def retranslateUi(self, d_editor):
        d_editor.setWindowTitle(QCoreApplication.translate("d_editor", u"Dialog", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_editor), QCoreApplication.translate("d_editor", u"Editor", None))
        self.bt_sessions_exec.setText(QCoreApplication.translate("d_editor", u"view", None))
        self.cbo_sessions.setItemText(0, QCoreApplication.translate("d_editor", u"ACTIVE", None))
        self.cbo_sessions.setItemText(1, QCoreApplication.translate("d_editor", u"INACTIVE", None))
        self.cbo_sessions.setItemText(2, QCoreApplication.translate("d_editor", u"%", None))

        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_session), QCoreApplication.translate("d_editor", u"Sessions", None))
        self.bt_explain.setText(QCoreApplication.translate("d_editor", u"Run", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_explain), QCoreApplication.translate("d_editor", u"Explain", None))
        self.groupBox_5.setTitle(QCoreApplication.translate("d_editor", u"Options", None))
        self.bt_csv_of.setText(QCoreApplication.translate("d_editor", u"...", None))
        self.bt_csv_populate.setText(QCoreApplication.translate("d_editor", u"Populate", None))
        self.chk_csv.setText(QCoreApplication.translate("d_editor", u"First Line = Titles", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_csv_updater), QCoreApplication.translate("d_editor", u"CSV Updater", None))
        self.groupBox_4.setTitle(QCoreApplication.translate("d_editor", u"Filter", None))
        self.chk_obj_table.setText(QCoreApplication.translate("d_editor", u"TABLE", None))
        self.chk_obj_view.setText(QCoreApplication.translate("d_editor", u"VIEW", None))
        self.chk_obj_package.setText(QCoreApplication.translate("d_editor", u"PACKAGE", None))
        self.chk_obj_trigger.setText(QCoreApplication.translate("d_editor", u"TRIGGER", None))
        self.chk_obj_procedure.setText(QCoreApplication.translate("d_editor", u"PROCEDURE", None))
        self.chk_obj_funcion.setText(QCoreApplication.translate("d_editor", u"FUNCTION", None))
        self.label_3.setText(QCoreApplication.translate("d_editor", u"Object Name", None))
        self.bt_obj_viewcode.setText(QCoreApplication.translate("d_editor", u"View Code (DDL)", None))
        self.chk_obj_sequence.setText(QCoreApplication.translate("d_editor", u"SEQUENCE", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_find_objects), QCoreApplication.translate("d_editor", u"Find Objects", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("d_editor", u" Configs", None))
        self.label.setText(QCoreApplication.translate("d_editor", u"Oracle Home", None))
        self.label_2.setText(QCoreApplication.translate("d_editor", u"Templates Directory", None))
        self.chk_cfg_run_user.setText(QCoreApplication.translate("d_editor", u"Default \"Run User\" ", None))
        self.bt_cfg_salvar.setText(QCoreApplication.translate("d_editor", u"Save Configs", None))
        self.label_5.setText(QCoreApplication.translate("d_editor", u"Outputs Directory", None))
        self.groupBox.setTitle(QCoreApplication.translate("d_editor", u"TNS", None))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_cfg_services_names), QCoreApplication.translate("d_editor", u"Services Names/SIDs", None))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_cfg_users_saved), QCoreApplication.translate("d_editor", u"Saved Users", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_config), QCoreApplication.translate("d_editor", u"Configs", None))
        self.groupBox_6.setTitle(QCoreApplication.translate("d_editor", u"Filter Query", None))
        self.label_4.setText(QCoreApplication.translate("d_editor", u"type text:", None))
        self.edt_recall.setText(QCoreApplication.translate("d_editor", u"%", None))
        self.label_6.setText(QCoreApplication.translate("d_editor", u"database:", None))
        self.edt_recall_database.setText(QCoreApplication.translate("d_editor", u"%", None))
        ___qtablewidgetitem = self.grid_recall.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("d_editor", u"Date", None));
        ___qtablewidgetitem1 = self.grid_recall.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("d_editor", u"Database", None));
        ___qtablewidgetitem2 = self.grid_recall.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("d_editor", u"SQL", None));
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_recall), QCoreApplication.translate("d_editor", u"Recall", None))
        self.groupBox_7.setTitle(QCoreApplication.translate("d_editor", u"Filter", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_importer), QCoreApplication.translate("d_editor", u"Importer", None))
    # retranslateUi

