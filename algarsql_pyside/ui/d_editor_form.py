# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'd_editor_form.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QFrame, QHBoxLayout,
    QHeaderView, QPlainTextEdit, QPushButton, QSizePolicy,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)

class Ui_d_editor_form(object):
    def setupUi(self, d_editor_form):
        if not d_editor_form.objectName():
            d_editor_form.setObjectName(u"d_editor_form")
        d_editor_form.resize(336, 490)
        d_editor_form.setModal(True)
        self.verticalLayout = QVBoxLayout(d_editor_form)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.frame = QFrame(d_editor_form)
        self.frame.setObjectName(u"frame")
        self.frame.setMinimumSize(QSize(0, 40))
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame)
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(-1, -1, -1, 9)
        self.bt_salvar = QPushButton(self.frame)
        self.bt_salvar.setObjectName(u"bt_salvar")

        self.horizontalLayout.addWidget(self.bt_salvar)


        self.verticalLayout.addWidget(self.frame)

        self.grid = QTableWidget(d_editor_form)
        if (self.grid.columnCount() < 2):
            self.grid.setColumnCount(2)
        __qtablewidgetitem = QTableWidgetItem()
        self.grid.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.grid.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        self.grid.setObjectName(u"grid")

        self.verticalLayout.addWidget(self.grid)

        self.mem_grid = QPlainTextEdit(d_editor_form)
        self.mem_grid.setObjectName(u"mem_grid")
        font = QFont()
        font.setFamilies([u"Monospace"])
        self.mem_grid.setFont(font)
        self.mem_grid.setLineWrapMode(QPlainTextEdit.NoWrap)

        self.verticalLayout.addWidget(self.mem_grid)


        self.retranslateUi(d_editor_form)

        QMetaObject.connectSlotsByName(d_editor_form)
    # setupUi

    def retranslateUi(self, d_editor_form):
        d_editor_form.setWindowTitle(QCoreApplication.translate("d_editor_form", u"Dialog", None))
        self.bt_salvar.setText(QCoreApplication.translate("d_editor_form", u"salvar", None))
        ___qtablewidgetitem = self.grid.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("d_editor_form", u"FieldName", None));
        ___qtablewidgetitem1 = self.grid.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("d_editor_form", u"FieldValue", None));
    # retranslateUi

