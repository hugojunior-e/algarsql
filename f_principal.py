import d_principal
import dm
import os
import dm_const
import f_editor_tti
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class form(QMainWindow):
    def __init__(self):
        super(form, self).__init__()
        self.ui = d_principal.Ui_d_principal()
        self.ui.setupUi(self)
        self.popup_config = dm.createMenu(self, ["Recall SQL|Ctrl+E", "View Sessions", "Find Objects", "Explain Query|F5", "CSV Updater", "-", "Recompile Invalid Objects", "-", "Reload Templates","-", "Config Tools","-","Export data Table"],self.popup_config_click)        
        self.popup_tree   = dm.createMenu(self, ["View Code", "Query Data"],self.popup_tree_click)
        self.ui.actionLogon.triggered.connect( lambda: dm.f_logon.showLogin() )
        self.ui.actionLogoff.triggered.connect(self.actionLogoff_click)
        self.ui.actionNewEditor.triggered.connect(self.actionNewEditor_click)
        self.ui.actionRunSQL.triggered.connect( lambda: self.ui.pc_editor.currentWidget().executeSQL() )
        self.ui.actionStopSQL.triggered.connect( lambda: self.ui.pc_editor.currentWidget().db.stopSQL() )
        self.ui.actionCommit.triggered.connect(self.actionCommit_click)
        self.ui.actionRollback.triggered.connect(self.actionRollback_click)
        self.ui.actionConfigs.triggered.connect( lambda: self.popup_config.exec_(QCursor.pos()) )
        self.ui.actionOpenEditor.triggered.connect(self.actionOpenEditor_click)
        self.ui.actionSaveEditor.triggered.connect(self.actionSaveEditor_click)
        self.ui.pc_editor.currentChanged.connect(self.pc_editor_tabchange)
        self.ui.pc_editor.removeTab(0)
        self.ui.pc_editor.removeTab(0)
        self.ui.pc_editor.tabCloseRequested.connect( lambda index: (self.ui.pc_editor.widget(index).db.disconnect(), self.ui.pc_editor.removeTab(index)) )
        self.ui.tree_objetos.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.tree_objetos.customContextMenuRequested.connect(self.tree_objetos_popup)   
        self.ui.tree_templates.doubleClicked.connect( self.tree_templates_doubleclicked )
        self.ui.splitter.setSizes([300, 1000])
        self.montaTreeTemplate()
        self.setWindowTitle(dm_const.C_APP_VERSION)
        
    
    ## ==============================================================================================
    ## tree de objetos + popup
    ## ==============================================================================================

    def extrai_ddl(self, info):
            if dm.db.prepare() == False:
                QMessageBox.about(None, "Message", self.db.status_msg) 
                return
            self.bt      = dm.createButtonWork(Run=lambda:(self.th.thread.terminate(),self.bt.close()), Text=f"Extracting DML {info}")
            self.bt.info = info
            self.th      = dm.Worker(proc_run=lambda:(dm.db.executeSQL(p_sql=info, p_tipo='DML')), proc_fim=self.popup_tree_view_code_finish)

    def popup_tree_view_code_finish(self):
        for txt in dm.db.status_msg.split("<end_package_spec>"):
            nomes              = self.bt.info.split("/")
            tab                = self.actionNewEditor_click()
            tab.ui.mem_editor.setPlainText(txt)
            tab.db_hide_grid_opts( False )
            tab.objectname = nomes[0] + "." + nomes[2]
            tab.tabTextIcon()
            self.bt.close()

    def popup_tree_click(self):
        x = self.ui.tree_objetos.currentItem().text(1)

        if self.sender().text() == "View Code":
            self.extrai_ddl(x)

        if self.sender().text() == "Query Data":
            xx  = self.ui.tree_objetos.currentItem().text(1).split("/")
            tab = self.actionNewEditor_click()
            tab.ui.mem_editor.setPlainText("SELECT * FROM " + xx[0] + "." + xx[2])
            tab.executeSQL()

    def tree_objetos_popup(self, position):
        x = self.ui.tree_objetos.currentItem().text(1)
        if x:
            self.popup_tree.actions()[1].setVisible( "/TABLE/" in x or "/VIEW/" in x )
            self.popup_tree.exec_(self.ui.tree_objetos.viewport().mapToGlobal(position))

    def tree_objetos_montar(self):
        self.ui.tree_objetos.clear()
        dm.db.executeSQL( p_sql=dm_const.C_SQL_TREE )
        dm.all_tables = []
        dm.all_users  = []
        if dm.db.status_code == 0:
            v_OWNER       = '-'
            v_OBJECT_TYPE = '-'            
            for x in dm.db.cur.fetchall():
                if x[0] != v_OWNER:
                    dm.all_users   = dm.all_users + [x[0]]
                    pai = QTreeWidgetItem([ x[0] ])
                    pai.setIcon(0,dm.iconUser)
                    self.ui.tree_objetos.addTopLevelItem(pai)

                if x[0] + x[1] != v_OWNER + v_OBJECT_TYPE:
                    meio            = QTreeWidgetItem([ x[1] ])
                    meio.setIcon(0,dm.iconObject)
                    pai.addChild(meio)

                no_final            = QTreeWidgetItem([ x[2] , x[0] + "/" + x[1] + "/" + x[2] ])
                no_final.setIcon(0,dm.iconBlue if x[3] == "VALID" else dm.iconRed)
                meio.addChild(no_final)

                if x[1] in ['TABLE','VIEW']:
                    dm.all_tables = dm.all_tables + [ x[2] ]
                v_OWNER       = x[0]
                v_OBJECT_TYPE = x[1]

    ## ==============================================================================================
    ## botoes do toolbar
    ## ==============================================================================================

    def actionLogoff_click(self):
        dm.db.disconnect()
        for i in range( self.ui.pc_editor.tabBar().count() ):
            self.ui.pc_editor.widget(i).db.disconnect()    
        self.setWindowTitle(dm_const.C_APP_VERSION)   
        self.ui.tree_objetos.clear()

    def actionCommit_click(self):
        self.ui.pc_editor.currentWidget().db.commit()
        self.pc_editor_tabchange()

    def actionRollback_click(self):
        self.ui.pc_editor.currentWidget().db.rollback()
        self.pc_editor_tabchange()

    def actionNewEditor_click(self,):
        tab     = f_editor_tti.form()
        tab.ui.chk_run_user_local.setVisible(not dm.db.is_direct)
        self.ui.pc_editor.addTab(tab,dm.iconBlue, "*")
        self.ui.pc_editor.setCurrentWidget(tab)
        return tab

    def actionOpenEditor_loadfromfile(self, fileName):
        dados        = "".join( dm.loadFromFile(fileName) )
        tab          = self.actionNewEditor_click()
        tab.filename = fileName
        A,B          = dm.tipoSQL(dados,checkCreateObj=True)
        if  A == 3:
            tab.objectname = B
            tab.db_hide_grid_opts( False )

        tab.ui.mem_editor.setPlainText(dados)
        tab.tabTextIcon()

    def actionOpenEditor_click(self):
        fileName, _ = QFileDialog.getOpenFileName(None,"Open File", "","SQL Files(*.sql);;All Files (*)", options=QFileDialog.DontUseNativeDialog)        
        if fileName:
            self.actionOpenEditor_loadfromfile(fileName=fileName)

    def actionSaveEditor_click(self):
        tab  = self.ui.pc_editor.currentWidget()
        nome = ""
        novo = False
        if tab:
            if tab.filename == None:
                nome, _ = QFileDialog.getSaveFileName(self, "Save file", "", "SQL Files (*.sql)",  options=QFileDialog.DontUseNativeDialog)
                novo  = True
            else:
                nome  = tab.filename
            
            if nome:
                tab.filename = nome
                xx = open(nome, "w")
                xx.write(tab.ui.mem_editor.toPlainText())
                xx.close()
                tab.tabTextIcon()
                if novo:
                    self.montaTreeTemplate()
            

    ## ==============================================================================================
    ## popup botao de configuracoes
    ## ==============================================================================================

    def popup_config_recompile(self):
        dm.db.executeSQL(p_sql=dm_const.C_SQL_RECOMPILE, p_tipo="SELECT_DIRECT")
        if dm.db.status_code == 0:
            listagem = dm.db.cur.fetchall()
            self.bt.H_msg_ret = []
            for x in listagem:
                self.bt.setText( x[0] )
                dm.db.executeSQL(p_sql=x[1], p_tipo="EXEC_DIRECT")

                self.bt.H_msg_ret.append( x[0] )
                self.bt.H_msg_ret.append( dm.db.status_msg )
                self.bt.H_msg_ret.append( "----------------------------------------" )
        self._bt_.close()
        
        
    def popup_config_export_data(self):
        db = self.ui.pc_editor.currentWidget().db
        ff = dm.do_filename('export_data.db')
        while True:
           data =  db.cur.fetchmany(5000)
           if len(data) == 0:
               break
               


    def popup_config_click(self):
        if self.sender().text() == "Reload Templates":
            self.montaTreeTemplate()

        elif self.sender().text() == "Export data Table":
            self.bt = dm.createButtonWork(Run=lambda:(self.th.thread.terminate(),self.bt.close()))
            self.th = dm.Worker(proc_run=self.popup_config_export_data)


        elif self.sender().text() == "Recompile Invalid Objects":
            x       = lambda: dm.f_editor.showForm("Editor", "\n".join( self.bt.H_msg_ret ) )
            self.bt = dm.createButtonWork(Run=lambda:(self.th.thread.terminate(),self.bt.close(), x))
            self.th = dm.Worker(proc_run=self.popup_config_recompile, proc_fim=x)
        else:
            ff = self.ui.pc_editor.currentWidget()
            dm.f_editor.showForm( self.sender().text() , "" if ff == None else ff.ui.mem_editor.toPlainText() )


    ## ==============================================================================================
    ## tree de templates
    ## ==============================================================================================

    def tree_templates_doubleclicked(self,index):
        fileName = self.ui.tree_templates.model().fileName(index)
        filePath = self.ui.tree_templates.model().filePath(index)
        fullName = (filePath + os.path.pathsep + fileName).split(":")[0]
        if os.path.isfile(fullName):
            self.actionOpenEditor_loadfromfile(fileName=fullName)

    def montaTreeTemplate(self):
        dir_path = dm.configValue(tag="template_dir")
        model    = QFileSystemModel()
        model.setRootPath(dir_path)        
        self.ui.tree_templates.setModel(model)
        self.ui.tree_templates.setRootIndex(model.index(dir_path))
        self.ui.tree_templates.hideColumn(1)
        self.ui.tree_templates.hideColumn(3)
        self.ui.tree_templates.setColumnWidth(0, 250)



    ## ==============================================================================================
    ##
    ## ==============================================================================================

    def pc_editor_tabchange(self):
        try:
            in_execution   = self.ui.pc_editor.currentWidget().db.in_execution
            is_transaction = self.ui.pc_editor.currentWidget().db.in_transaction
            self.ui.actionRunSQL.setEnabled(not in_execution)
            self.ui.actionStopSQL.setEnabled(in_execution)
            self.ui.actionCommit.setEnabled(is_transaction)
            self.ui.actionRollback.setEnabled(is_transaction)
        except:
            self.ui.actionRunSQL.setEnabled(False)
            self.ui.actionStopSQL.setEnabled(False)
            self.ui.actionCommit.setEnabled(False)
            self.ui.actionRollback.setEnabled(False)