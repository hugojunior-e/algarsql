import ui.d_principal as d_principal
import dm
import os
import dm_const
import sqlite3
import f_editor_tti
from PyQt5.QtWidgets import QMainWindow, QTreeWidgetItem, QFileDialog, QFileSystemModel
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt

class form(QMainWindow):
    def __init__(self):
        super(form, self).__init__()
        self.ui = d_principal.Ui_d_principal()
        self.ui.setupUi(self)
        self.actionConfigs_popup = dm.MENU(["Recall SQL|Ctrl+E", "View Sessions|-", "Find Objects|-", "Explain Query|F5", "CSV Updater|-", "-", "Recompile Invalid Objects|-", "-", "Reload Templates|-","-", "Config Tools|-","-","Export data Table|-"],self.actionConfigs_popup_click, self)        
        self.tree_objetos_popup  = dm.MENU(["View Code|-", "Query Data|-"],self.tree_objetos_popup_click, self)

        self.ui.actionLogon.triggered.connect( lambda: dm.f_logon.showLogin() )
        self.ui.actionLogoff.triggered.connect(self.actionLogoff_click)
        self.ui.actionNewEditor.triggered.connect(self.actionNewEditor_click)
        self.ui.actionRunSQL.triggered.connect(self.actionRunSQL_click)
        self.ui.actionStopSQL.triggered.connect( lambda: self.ui.pc_editor.currentWidget().db.stopSQL() )
        self.ui.actionCommit.triggered.connect(self.actionCommit_click)
        self.ui.actionRollback.triggered.connect(self.actionRollback_click)
        self.ui.actionConfigs.triggered.connect( lambda: self.actionConfigs_popup.exec_(QCursor.pos()) )
        self.ui.actionOpenEditor.triggered.connect(self.actionOpenEditor_click)
        self.ui.actionSaveEditor.triggered.connect(self.actionSaveEditor_click)
        self.ui.pc_editor.currentChanged.connect(self.pc_editor_tabchange)
        self.ui.pc_editor.removeTab(0)
        self.ui.pc_editor.removeTab(0)
        self.ui.pc_editor.tabCloseRequested.connect( lambda index: (self.ui.pc_editor.widget(index).db.disconnect(), self.ui.pc_editor.removeTab(index)) )
        self.ui.tree_objetos.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.tree_objetos.customContextMenuRequested.connect(self.tree_objetos_popup_show)   
        self.ui.tree_templates.doubleClicked.connect( self.tree_templates_doubleclicked )
        self.ui.splitter.setSizes([310, 1000])
        self.tree_templates_montar()
        self.setWindowTitle(dm_const.C_APP_VERSION)
        self.ui.bt_find.clicked.connect( lambda: self.findReplaceActions(1) )
        self.ui.bt_find_next.clicked.connect( lambda: self.findReplaceActions(2))
        self.ui.bt_find_replace.clicked.connect( lambda: self.findReplaceActions(3) )
        self.ui.bt_find_replace_all.clicked.connect( lambda: self.findReplaceActions(4) )
        
    
    ## ==============================================================================================
    ## tree de objetos + popup
    ## ==============================================================================================


    def tree_objetos_popup_view_code_finish(self):
        for txt in dm.db.status_msg.split("<end_package_spec>"):
            tab                = self.actionNewEditor_click()
            tab.editorSQL.setText(txt)
            tab.visibility_controls( False )
            tab.objectname = self.bt.info
            tab.tabTextIcon()
            self.bt.close()

    def extrai_ddl(self, owner, type, name):
        if dm.db.prepare() == False: return
        
        self.bt      = dm.createButtonWork(Run=lambda:(self.th.thread.terminate(),self.bt.close()), Text=f"Extracting DML {owner + '.' + name}")
        self.bt.info = owner + '.' + name
        self.th      = dm.WORKER(proc_run=lambda:(dm.db.DDL(owner, type, name)), proc_fim=self.tree_objetos_popup_view_code_finish)


    def tree_objetos_popup_show(self, position):
        x = self.ui.tree_objetos.currentItem().text(1)
        if x:
            self.tree_objetos_popup.showAction('query_data', "/TABLE/" in x or "/VIEW/" in x )
            self.tree_objetos_popup.exec_(self.ui.tree_objetos.viewport().mapToGlobal(position))


    def tree_objetos_popup_click(self):
        x = self.ui.tree_objetos.currentItem().text(1)

        if self.sender().text() == "View Code":
            a,b,c = x.split("/")
            self.extrai_ddl( a,b,c )

        if self.sender().text() == "Query Data":
            xx  = self.ui.tree_objetos.currentItem().text(1).split("/")
            tab = self.actionNewEditor_click()
            tab.editorSQL.setText("SELECT * FROM " + xx[0] + "." + xx[2])
            tab.executeSQL()


    def tree_objetos_montar_start(self):
        dm.db.SELECT( p_sql=dm_const.C_SQL_TREE, fetchSize=0 )
        dm.all_tables = []
        dm.all_users  = []
        topLevelItems = []
        if dm.db.status_code == 0:
            v_OWNER       = '-'
            v_OBJECT_TYPE = '-'            
            for x in dm.db.col_data:
                if x[0] != v_OWNER:
                    dm.all_users   = dm.all_users + [x[0]]
                    pai = QTreeWidgetItem([ x[0] ])
                    pai.setIcon(0,dm.iconUser)
                    topLevelItems.append(pai)

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
        self.ui.tree_objetos.__topLevelItems = topLevelItems

    def tree_objetos_montar(self):
        self.ui.tree_objetos.clear()
        self.th1 = dm.WORKER(proc_run=self.tree_objetos_montar_start, proc_fim=lambda: self.ui.tree_objetos.addTopLevelItems(self.ui.tree_objetos.__topLevelItems) )

    ## ==============================================================================================
    ## botoes do toolbar 
    ## ==============================================================================================

    def actionRunSQL_click(self):
        self.ui.pc_editor.currentWidget().executeSQL()

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
            tab.visibility_controls( False )

        tab.editorSQL.setText(dados)
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
                xx.write(tab.editorSQL.getText())
                xx.close()
                tab.tabTextIcon()
                if novo:
                    self.tree_templates_montar()
            

    ## ==============================================================================================
    ## popup botao de configuracoes
    ## ==============================================================================================

    def popup_config_recompile(self):
        dm.db.SELECT(p_sql=dm_const.C_SQL_RECOMPILE, direct=True, fetchSize=0)
        if dm.db.status_code == 0:
            self.bt.H_msg_ret = []
            for x in dm.db.col_data:
                self.bt.setText( x[0] )
                dm.db.EXECUTE(p_sql=x[1],direct=True)

                self.bt.H_msg_ret.append( x[0] )
                self.bt.H_msg_ret.append( dm.db.status_msg )
                self.bt.H_msg_ret.append( "----------------------------------------" )
        self._bt_.close()
        
        
    def popup_config_export_data(self):
        tab = self.ui.pc_editor.currentWidget()
        ff  = dm.generateFileName('export_data.db',inOutputDir=True)
        if os.path.exists(ff):
            os.remove(ff)
        tab.tabTextIcon(Icon=dm.iconRed)
        tab.db.SELECT( p_sql=tab.pegaSQL() )
        sqlite_conn        = sqlite3.connect(ff)
        sqlite_cursor      = sqlite_conn.cursor()
        columns            = [ f"{column[0]} TEXT" for column in tab.db.cur.description]
        create_table_query = f"CREATE TABLE IF NOT EXISTS tabela ( { ', '.join(columns) } )"
        insert_table_query = f"INSERT INTO tabela VALUES ({', '.join(['?' for _ in columns])})"
        sqlite_cursor.execute(create_table_query)
        qtd = 0
        while self.bt.isVisible():
            row = tab.db.cur.fetchmany(10000)
            qtd = qtd + len(row)
            if len(row) == 0:
                break

            dados = []
            for xx in row:
                dados_item = []
                for item in xx:
                    if "LOB" in str(type(item)).upper():
                        dados_item.append( item.read() )
                    else:
                        dados_item.append( item )
                dados.append(dados_item)

            sqlite_cursor.executemany(insert_table_query, dados)
            sqlite_conn.commit()

            self.bt.setText( f"{qtd} records" )
        sqlite_conn.close()
        tab.tabTextIcon(Icon=dm.iconBlue)


    def actionConfigs_popup_click(self):
        if self.sender().text() == "Reload Templates":
            self.tree_templates_montar()

        elif self.sender().text() == "Export data Table":
            if self.ui.pc_editor.currentWidget():
                self.bt = dm.createButtonWork()
                self.th = dm.WORKER(proc_run=self.popup_config_export_data)


        elif self.sender().text() == "Recompile Invalid Objects":
            x       = lambda: dm.f_editor.showForm("Editor", "\n".join( self.bt.H_msg_ret ) )
            self.bt = dm.createButtonWork(Run=lambda:(self.th.thread.terminate(),self.bt.close(), x))
            self.th = dm.WORKER(proc_run=self.popup_config_recompile, proc_fim=x)
        else:
            ff = self.ui.pc_editor.currentWidget()
            dm.f_editor.showForm( self.sender().text() , "" if ff == None else ff.editorSQL.getText() )


    ## ==============================================================================================
    ## tree de templates
    ## ==============================================================================================

    def tree_templates_doubleclicked(self,index):
        fileName = self.ui.tree_templates.model().fileName(index)
        filePath = self.ui.tree_templates.model().filePath(index)
        fullName = (filePath + os.path.pathsep + fileName).split(":")[0]
        if os.path.isfile(fullName):
            if os.path.splitext(fullName)[1].upper() == '.PY':
                os.system( f"code {fullName}" )
            else:
                self.actionOpenEditor_loadfromfile(fileName=fullName)


    def tree_templates_montar(self):
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

    ## ==============================================================================================
    ##
    ## ==============================================================================================

    def findReplaceActions(self, action):
        frm = self.ui.pc_editor.currentWidget()
        if frm:
            frm.editorSQL.finder_prepare([self.ui.edt_find_text.text(),self.ui.edt_find_replace.text(), self.ui.chk_find_match_case.isChecked(), self.ui.chk_find_match_whole_word.isChecked()])
            if action == 1:
                frm.editorSQL.finder()   
            elif action == 2:
                frm.editorSQL.finder_select()
            elif action == 3:
                frm.editorSQL.finder_replace()
            elif action == 4:
                frm.editorSQL.finder_replace_all()  


