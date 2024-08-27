import lib.d_logon as d_logon
import dm


from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

class form(QDialog):
    def __init__(self):
        super(form, self).__init__()
        self.ui = d_logon.Ui_d_logon()
        self.ui.setupUi(self)
        self.ui.bt_conectar.clicked.connect(self.bt_conectar_clicked)
        self.ui.tree_tns.clicked.connect(self.tree_tns_itemclicked)
        self.reload_conf = True


    def showLogin(self):
        if self.reload_conf:
            self.ui.tree_tns.clear()
            self.reload_conf = False
            for x in dm.configValue(tag='tnsSaved').split("\n"):
                if len(x) > 3:
                    if x.startswith(">"):
                        item = QTreeWidgetItem( [ x[1:].strip() ] )
                        self.ui.tree_tns.addTopLevelItem(item)    
                    else:
                        rr = x.split("|")
                        x = QTreeWidgetItem( [ f"{rr[0]}@{rr[2]}" , rr[0], rr[1], rr[2] ] )
                        item.addChild(x)

            self.ui.cbo_database.clear() 
            for x in dm.configValue(tag='tns').split("\n"):
                if len( x.strip() ) > 0:
                    a = x.split("|")
                    self.ui.cbo_database.addItem(a[0].strip(), a[1].strip())
        self.show()


    def tree_tns_itemclicked(self, it):
        if self.ui.tree_tns.currentItem().text(1):
            self.ui.edt_username.setText( self.ui.tree_tns.currentItem().text(1) )
            self.ui.edt_password.setText( self.ui.tree_tns.currentItem().text(2) )
            self.ui.cbo_database.setCurrentText( self.ui.tree_tns.currentItem().text(3) )
            


    def bt_conectar_clicked(self):
        dm.db.CONNECT( self.ui.edt_username.text(), self.ui.edt_password.text(), self.ui.cbo_database.currentData(), self.ui.chk_direct_access.isChecked() )
        if dm.db.status_code == 0:
            for i in range( dm.f_principal.ui.pc_editor.tabBar().count() ):
                dm.f_principal.ui.pc_editor.widget(i).db.disconnect()    
                dm.f_principal.ui.pc_editor.widget(i).ui.chk_run_user_local.setVisible(not dm.db.is_direct)
            dm.f_principal.setWindowTitle( f"{self.ui.edt_username.text()}@{self.ui.cbo_database.currentText()} - ({dm.db.login_banner})")
            dm.f_principal.tree_objetos_montar()
            self.close()
        else:
            dm.messageBox(dm.db.status_msg)
