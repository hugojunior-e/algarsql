# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'f_logon.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_f_logon(object):
    def setupUi(self, f_logon):
        f_logon.setObjectName("f_logon")
        f_logon.resize(550, 280)
        f_logon.setMinimumSize(QtCore.QSize(550, 280))
        f_logon.setMaximumSize(QtCore.QSize(550, 280))
        f_logon.setModal(True)
        self.horizontalLayout = QtWidgets.QHBoxLayout(f_logon)
        self.horizontalLayout.setContentsMargins(9, 9, 9, 9)
        self.horizontalLayout.setSpacing(9)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.frame = QtWidgets.QFrame(f_logon)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.edt_username = QtWidgets.QLineEdit(self.frame)
        self.edt_username.setGeometry(QtCore.QRect(280, 30, 201, 32))
        self.edt_username.setObjectName("edt_username")
        self.label_3 = QtWidgets.QLabel(self.frame)
        self.label_3.setGeometry(QtCore.QRect(270, 70, 58, 18))
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(self.frame)
        self.label_4.setGeometry(QtCore.QRect(270, 130, 58, 18))
        self.label_4.setObjectName("label_4")
        self.line = QtWidgets.QFrame(self.frame)
        self.line.setGeometry(QtCore.QRect(270, 190, 251, 16))
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.bt_conectar = QtWidgets.QPushButton(self.frame)
        self.bt_conectar.setGeometry(QtCore.QRect(280, 210, 71, 34))
        self.bt_conectar.setObjectName("bt_conectar")
        self.edt_password = QtWidgets.QLineEdit(self.frame)
        self.edt_password.setGeometry(QtCore.QRect(280, 90, 201, 32))
        self.edt_password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.edt_password.setObjectName("edt_password")
        self.cbo_database = QtWidgets.QComboBox(self.frame)
        self.cbo_database.setGeometry(QtCore.QRect(280, 150, 201, 32))
        self.cbo_database.setObjectName("cbo_database")
        self.label_2 = QtWidgets.QLabel(self.frame)
        self.label_2.setGeometry(QtCore.QRect(270, 10, 71, 18))
        self.label_2.setObjectName("label_2")
        self.chk_direct_access = QtWidgets.QCheckBox(self.frame)
        self.chk_direct_access.setGeometry(QtCore.QRect(360, 216, 131, 21))
        self.chk_direct_access.setObjectName("chk_direct_access")
        self.tree_tns = QtWidgets.QTreeWidget(self.frame)
        self.tree_tns.setGeometry(QtCore.QRect(10, 10, 251, 241))
        self.tree_tns.setAlternatingRowColors(False)
        self.tree_tns.setUniformRowHeights(True)
        self.tree_tns.setObjectName("tree_tns")
        self.tree_tns.headerItem().setText(0, "1")
        self.tree_tns.header().setVisible(False)
        self.horizontalLayout.addWidget(self.frame)

        self.retranslateUi(f_logon)
        QtCore.QMetaObject.connectSlotsByName(f_logon)

    def retranslateUi(self, f_logon):
        _translate = QtCore.QCoreApplication.translate
        f_logon.setWindowTitle(_translate("f_logon", "Dialog"))
        self.label_3.setText(_translate("f_logon", "Pasword"))
        self.label_4.setText(_translate("f_logon", "Database"))
        self.bt_conectar.setText(_translate("f_logon", "OK"))
        self.label_2.setText(_translate("f_logon", "Username"))
        self.chk_direct_access.setText(_translate("f_logon", "Direct Acess"))
