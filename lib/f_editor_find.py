# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'f_editor_find.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_f_editor_find(object):
    def setupUi(self, f_editor_find):
        f_editor_find.setObjectName("f_editor_find")
        f_editor_find.resize(438, 201)
        f_editor_find.setModal(True)
        self.edt_text = QtWidgets.QLineEdit(f_editor_find)
        self.edt_text.setGeometry(QtCore.QRect(100, 20, 171, 26))
        self.edt_text.setObjectName("edt_text")
        self.bt_replace_all = QtWidgets.QPushButton(f_editor_find)
        self.bt_replace_all.setGeometry(QtCore.QRect(310, 110, 101, 26))
        self.bt_replace_all.setObjectName("bt_replace_all")
        self.edt_replace = QtWidgets.QLineEdit(f_editor_find)
        self.edt_replace.setGeometry(QtCore.QRect(100, 60, 171, 26))
        self.edt_replace.setObjectName("edt_replace")
        self.label = QtWidgets.QLabel(f_editor_find)
        self.label.setGeometry(QtCore.QRect(20, 20, 71, 18))
        self.label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(f_editor_find)
        self.label_2.setGeometry(QtCore.QRect(11, 60, 81, 18))
        self.label_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName("label_2")
        self.groupBox = QtWidgets.QGroupBox(f_editor_find)
        self.groupBox.setGeometry(QtCore.QRect(10, 90, 271, 91))
        self.groupBox.setObjectName("groupBox")
        self.chk_match_case = QtWidgets.QCheckBox(self.groupBox)
        self.chk_match_case.setGeometry(QtCore.QRect(30, 30, 111, 24))
        self.chk_match_case.setObjectName("chk_match_case")
        self.chk_match_whole_word = QtWidgets.QCheckBox(self.groupBox)
        self.chk_match_whole_word.setGeometry(QtCore.QRect(30, 60, 151, 24))
        self.chk_match_whole_word.setObjectName("chk_match_whole_word")
        self.bt_find = QtWidgets.QPushButton(f_editor_find)
        self.bt_find.setGeometry(QtCore.QRect(310, 20, 101, 26))
        self.bt_find.setObjectName("bt_find")
        self.bt_replace = QtWidgets.QPushButton(f_editor_find)
        self.bt_replace.setGeometry(QtCore.QRect(310, 80, 101, 26))
        self.bt_replace.setObjectName("bt_replace")
        self.bt_find_next = QtWidgets.QPushButton(f_editor_find)
        self.bt_find_next.setGeometry(QtCore.QRect(310, 50, 101, 26))
        self.bt_find_next.setObjectName("bt_find_next")

        self.retranslateUi(f_editor_find)
        QtCore.QMetaObject.connectSlotsByName(f_editor_find)

    def retranslateUi(self, f_editor_find):
        _translate = QtCore.QCoreApplication.translate
        f_editor_find.setWindowTitle(_translate("f_editor_find", "Find / Replace"))
        self.bt_replace_all.setText(_translate("f_editor_find", "Replace All"))
        self.label.setText(_translate("f_editor_find", "Find Text:"))
        self.label_2.setText(_translate("f_editor_find", "Replace By:"))
        self.groupBox.setTitle(_translate("f_editor_find", "Options"))
        self.chk_match_case.setText(_translate("f_editor_find", "Match Case"))
        self.chk_match_whole_word.setText(_translate("f_editor_find", "Match Whole Word"))
        self.bt_find.setText(_translate("f_editor_find", "Find"))
        self.bt_replace.setText(_translate("f_editor_find", "Replace"))
        self.bt_find_next.setText(_translate("f_editor_find", "Find Next"))
