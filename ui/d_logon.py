# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'd_logon.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_d_logon(object):
    def setupUi(self, d_logon):
        d_logon.setObjectName("d_logon")
        d_logon.resize(550, 300)
        d_logon.setMinimumSize(QtCore.QSize(550, 300))
        d_logon.setMaximumSize(QtCore.QSize(550, 300))
        d_logon.setModal(True)
        self.horizontalLayout = QtWidgets.QHBoxLayout(d_logon)
        self.horizontalLayout.setContentsMargins(9, 9, 9, 9)
        self.horizontalLayout.setSpacing(9)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.frame = QtWidgets.QFrame(d_logon)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.edt_username = QtWidgets.QLineEdit(self.frame)
        self.edt_username.setGeometry(QtCore.QRect(280, 30, 231, 32))
        self.edt_username.setObjectName("edt_username")
        self.label_3 = QtWidgets.QLabel(self.frame)
        self.label_3.setGeometry(QtCore.QRect(270, 70, 58, 18))
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(self.frame)
        self.label_4.setGeometry(QtCore.QRect(270, 130, 58, 18))
        self.label_4.setObjectName("label_4")
        self.bt_conectar = QtWidgets.QPushButton(self.frame)
        self.bt_conectar.setGeometry(QtCore.QRect(270, 210, 101, 34))
        self.bt_conectar.setObjectName("bt_conectar")
        self.edt_password = QtWidgets.QLineEdit(self.frame)
        self.edt_password.setGeometry(QtCore.QRect(280, 90, 231, 32))
        self.edt_password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.edt_password.setObjectName("edt_password")
        self.cbo_database = QtWidgets.QComboBox(self.frame)
        self.cbo_database.setGeometry(QtCore.QRect(280, 150, 231, 32))
        self.cbo_database.setObjectName("cbo_database")
        self.label_2 = QtWidgets.QLabel(self.frame)
        self.label_2.setGeometry(QtCore.QRect(270, 10, 71, 18))
        self.label_2.setObjectName("label_2")
        self.chk_direct_access = QtWidgets.QCheckBox(self.frame)
        self.chk_direct_access.setGeometry(QtCore.QRect(400, 220, 101, 21))
        self.chk_direct_access.setObjectName("chk_direct_access")
        self.tree_tns = QtWidgets.QTreeWidget(self.frame)
        self.tree_tns.setGeometry(QtCore.QRect(10, 10, 251, 261))
        self.tree_tns.setAlternatingRowColors(False)
        self.tree_tns.setUniformRowHeights(True)
        self.tree_tns.setObjectName("tree_tns")
        self.tree_tns.headerItem().setText(0, "1")
        self.tree_tns.header().setVisible(False)
        self.line_2 = QtWidgets.QFrame(self.frame)
        self.line_2.setGeometry(QtCore.QRect(270, 190, 251, 16))
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.horizontalLayout.addWidget(self.frame)

        self.retranslateUi(d_logon)
        QtCore.QMetaObject.connectSlotsByName(d_logon)

    def retranslateUi(self, d_logon):
        _translate = QtCore.QCoreApplication.translate
        d_logon.setWindowTitle(_translate("d_logon", "Dialog"))
        self.label_3.setText(_translate("d_logon", "Pasword"))
        self.label_4.setText(_translate("d_logon", "Database"))
        self.bt_conectar.setText(_translate("d_logon", "OK"))
        self.label_2.setText(_translate("d_logon", "Username"))
        self.chk_direct_access.setText(_translate("d_logon", "Direct Acess"))
