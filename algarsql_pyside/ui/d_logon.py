# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'd_logon.ui'
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
    QFrame, QHBoxLayout, QHeaderView, QLabel,
    QLineEdit, QPushButton, QSizePolicy, QTreeWidget,
    QTreeWidgetItem, QWidget)

class Ui_d_logon(object):
    def setupUi(self, d_logon):
        if not d_logon.objectName():
            d_logon.setObjectName(u"d_logon")
        d_logon.resize(550, 300)
        d_logon.setMinimumSize(QSize(550, 300))
        d_logon.setMaximumSize(QSize(550, 300))
        d_logon.setModal(True)
        self.horizontalLayout = QHBoxLayout(d_logon)
        self.horizontalLayout.setSpacing(9)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(9, 9, 9, 9)
        self.frame = QFrame(d_logon)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.edt_username = QLineEdit(self.frame)
        self.edt_username.setObjectName(u"edt_username")
        self.edt_username.setGeometry(QRect(280, 30, 231, 32))
        self.label_3 = QLabel(self.frame)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(270, 70, 58, 18))
        self.label_4 = QLabel(self.frame)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(270, 130, 58, 18))
        self.bt_conectar = QPushButton(self.frame)
        self.bt_conectar.setObjectName(u"bt_conectar")
        self.bt_conectar.setGeometry(QRect(270, 210, 101, 34))
        self.edt_password = QLineEdit(self.frame)
        self.edt_password.setObjectName(u"edt_password")
        self.edt_password.setGeometry(QRect(280, 90, 231, 32))
        self.edt_password.setEchoMode(QLineEdit.Password)
        self.cbo_database = QComboBox(self.frame)
        self.cbo_database.setObjectName(u"cbo_database")
        self.cbo_database.setGeometry(QRect(280, 150, 231, 32))
        self.label_2 = QLabel(self.frame)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(270, 10, 71, 18))
        self.chk_direct_access = QCheckBox(self.frame)
        self.chk_direct_access.setObjectName(u"chk_direct_access")
        self.chk_direct_access.setGeometry(QRect(400, 220, 101, 21))
        self.tree_tns = QTreeWidget(self.frame)
        __qtreewidgetitem = QTreeWidgetItem()
        __qtreewidgetitem.setText(0, u"1");
        self.tree_tns.setHeaderItem(__qtreewidgetitem)
        self.tree_tns.setObjectName(u"tree_tns")
        self.tree_tns.setGeometry(QRect(10, 10, 251, 261))
        self.tree_tns.setAlternatingRowColors(False)
        self.tree_tns.setUniformRowHeights(True)
        self.tree_tns.header().setVisible(False)
        self.line_2 = QFrame(self.frame)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setGeometry(QRect(270, 190, 251, 16))
        self.line_2.setFrameShape(QFrame.Shape.HLine)
        self.line_2.setFrameShadow(QFrame.Shadow.Sunken)

        self.horizontalLayout.addWidget(self.frame)


        self.retranslateUi(d_logon)

        QMetaObject.connectSlotsByName(d_logon)
    # setupUi

    def retranslateUi(self, d_logon):
        d_logon.setWindowTitle(QCoreApplication.translate("d_logon", u"Dialog", None))
        self.label_3.setText(QCoreApplication.translate("d_logon", u"Pasword", None))
        self.label_4.setText(QCoreApplication.translate("d_logon", u"Database", None))
        self.bt_conectar.setText(QCoreApplication.translate("d_logon", u"OK", None))
        self.label_2.setText(QCoreApplication.translate("d_logon", u"Username", None))
        self.chk_direct_access.setText(QCoreApplication.translate("d_logon", u"Direct Acess", None))
    # retranslateUi

