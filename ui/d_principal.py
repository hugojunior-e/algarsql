# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'd_principal.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_d_principal(object):
    def setupUi(self, d_principal):
        d_principal.setObjectName("d_principal")
        d_principal.resize(928, 653)
        self.centralwidget = QtWidgets.QWidget(d_principal)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.splitter = QtWidgets.QSplitter(self.centralwidget)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.toolBox = QtWidgets.QToolBox(self.splitter)
        self.toolBox.setMinimumSize(QtCore.QSize(200, 0))
        self.toolBox.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.toolBox.setObjectName("toolBox")
        self.page = QtWidgets.QWidget()
        self.page.setGeometry(QtCore.QRect(0, 0, 561, 549))
        self.page.setObjectName("page")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.page)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tree_objetos = QtWidgets.QTreeWidget(self.page)
        self.tree_objetos.setObjectName("tree_objetos")
        self.tree_objetos.headerItem().setText(0, "1")
        self.tree_objetos.header().setVisible(False)
        self.verticalLayout.addWidget(self.tree_objetos)
        self.toolBox.addItem(self.page, "")
        self.page_2 = QtWidgets.QWidget()
        self.page_2.setGeometry(QtCore.QRect(0, 0, 561, 549))
        self.page_2.setObjectName("page_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.page_2)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.tree_templates = QtWidgets.QTreeView(self.page_2)
        self.tree_templates.setAlternatingRowColors(True)
        self.tree_templates.setObjectName("tree_templates")
        self.verticalLayout_2.addWidget(self.tree_templates)
        self.toolBox.addItem(self.page_2, "")
        self.pc_editor = QtWidgets.QTabWidget(self.splitter)
        self.pc_editor.setTabsClosable(True)
        self.pc_editor.setObjectName("pc_editor")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.pc_editor.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.pc_editor.addTab(self.tab_2, "")
        self.verticalLayout_3.addWidget(self.splitter)
        d_principal.setCentralWidget(self.centralwidget)
        self.toolBar = QtWidgets.QToolBar(d_principal)
        self.toolBar.setIconSize(QtCore.QSize(25, 25))
        self.toolBar.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        self.toolBar.setFloatable(True)
        self.toolBar.setObjectName("toolBar")
        d_principal.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.actionLogon = QtWidgets.QAction(d_principal)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/png/ico/db_logon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionLogon.setIcon(icon)
        self.actionLogon.setObjectName("actionLogon")
        self.actionLogoff = QtWidgets.QAction(d_principal)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/png/ico/db_logoff.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionLogoff.setIcon(icon1)
        self.actionLogoff.setObjectName("actionLogoff")
        self.actionNewEditor = QtWidgets.QAction(d_principal)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/png/ico/file_new.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionNewEditor.setIcon(icon2)
        self.actionNewEditor.setObjectName("actionNewEditor")
        self.actionSaveEditor = QtWidgets.QAction(d_principal)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/png/ico/file_saveall.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSaveEditor.setIcon(icon3)
        self.actionSaveEditor.setObjectName("actionSaveEditor")
        self.actionOpenEditor = QtWidgets.QAction(d_principal)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/png/ico/file_open.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionOpenEditor.setIcon(icon4)
        self.actionOpenEditor.setObjectName("actionOpenEditor")
        self.actionRunSQL = QtWidgets.QAction(d_principal)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/png/ico/sql_run.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionRunSQL.setIcon(icon5)
        self.actionRunSQL.setObjectName("actionRunSQL")
        self.actionStopSQL = QtWidgets.QAction(d_principal)
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(":/png/ico/sql_stop.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionStopSQL.setIcon(icon6)
        self.actionStopSQL.setObjectName("actionStopSQL")
        self.actionCommit = QtWidgets.QAction(d_principal)
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(":/png/ico/sql_commit.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionCommit.setIcon(icon7)
        self.actionCommit.setObjectName("actionCommit")
        self.actionRollback = QtWidgets.QAction(d_principal)
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap(":/png/ico/sql_rollback.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionRollback.setIcon(icon8)
        self.actionRollback.setObjectName("actionRollback")
        self.actionConfigs = QtWidgets.QAction(d_principal)
        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap(":/png/ico/preferences.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionConfigs.setIcon(icon9)
        self.actionConfigs.setObjectName("actionConfigs")
        self.toolBar.addAction(self.actionLogon)
        self.toolBar.addAction(self.actionLogoff)
        self.toolBar.addAction(self.actionNewEditor)
        self.toolBar.addAction(self.actionSaveEditor)
        self.toolBar.addAction(self.actionOpenEditor)
        self.toolBar.addAction(self.actionRunSQL)
        self.toolBar.addAction(self.actionStopSQL)
        self.toolBar.addAction(self.actionCommit)
        self.toolBar.addAction(self.actionRollback)
        self.toolBar.addAction(self.actionConfigs)

        self.retranslateUi(d_principal)
        self.toolBox.setCurrentIndex(0)
        self.pc_editor.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(d_principal)

    def retranslateUi(self, d_principal):
        _translate = QtCore.QCoreApplication.translate
        d_principal.setWindowTitle(_translate("d_principal", "AlgarSQL"))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page), _translate("d_principal", "Objects Tree"))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_2), _translate("d_principal", "Templates"))
        self.pc_editor.setTabText(self.pc_editor.indexOf(self.tab), _translate("d_principal", "Tab 1"))
        self.pc_editor.setTabText(self.pc_editor.indexOf(self.tab_2), _translate("d_principal", "Tab 2"))
        self.toolBar.setWindowTitle(_translate("d_principal", "toolBar"))
        self.actionLogon.setText(_translate("d_principal", "Logon"))
        self.actionLogoff.setText(_translate("d_principal", "Logoff"))
        self.actionNewEditor.setText(_translate("d_principal", "NewEditor"))
        self.actionNewEditor.setShortcut(_translate("d_principal", "Ctrl+N"))
        self.actionSaveEditor.setText(_translate("d_principal", "SaveEditor"))
        self.actionSaveEditor.setShortcut(_translate("d_principal", "Ctrl+S"))
        self.actionOpenEditor.setText(_translate("d_principal", "OpenEditor"))
        self.actionOpenEditor.setShortcut(_translate("d_principal", "Ctrl+O"))
        self.actionRunSQL.setText(_translate("d_principal", "RunSQL"))
        self.actionRunSQL.setShortcut(_translate("d_principal", "F8"))
        self.actionStopSQL.setText(_translate("d_principal", "StopSQL"))
        self.actionCommit.setText(_translate("d_principal", "Commit"))
        self.actionRollback.setText(_translate("d_principal", "Rollback"))
        self.actionConfigs.setText(_translate("d_principal", "Configs"))
from ui import menus_rc
