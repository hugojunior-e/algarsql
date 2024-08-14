import lib.f_editor as f_editor
import dm
import lib.constantes

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class form(QDialog):
    def __init__(self):
        super(form, self).__init__()
        self.ui = f_editor.Ui_f_editor()
        self.ui.setupUi(self)
        self.ui.bt_sessions_exec.clicked.connect(self.bt_sessions_exec_click)
        self.ui.edt_objetos.textEdited.connect(self.edt_objetos_edited)
        self.ui.bt_csv_of.clicked.connect(self.bt_csv_of_clicked)
        self.ui.bt_explain.clicked.connect(self.bt_explain_clicked)
        self.ui.bt_csv_populate.clicked.connect(self.bt_csv_populate_edited)
        self.ui.bt_cfg_salvar.clicked.connect(self.bt_cfg_salvar_clicked)
        self.ui.bt_obj_viewcode.clicked.connect(self.bt_obj_viewcode_clicked)
        self.ui.tree_explain.setColumnCount(7)
        self.ui.tree_explain.setHeaderLabels(["#", "Owner", "Name","Type","Cost","Cardinality","Bytes"])        
        self.ui.grid_csv.setColumnCount(1)
        self.ui.grid_csv.setColumnWidth(0,200)
        self.ui.grid_csv.setHorizontalHeaderLabels( ('Field Name/Value','-') )
        self.ui.grid_objetos.verticalHeader().setDefaultSectionSize(20)

        self.mem_csv_highlight     = dm.SyntaxHighlighter(self.ui.mem_csv.document())
        self.mem_explain           = dm.SyntaxHighlighter(self.ui.mem_explain.document())
        self.mem_editor_highlight  = dm.SyntaxHighlighter(self.ui.mem_editor.document())
        self.mem_session_highlight = dm.SyntaxHighlighter(self.ui.mem_sessions.document())
        self.mem_recall_highlight  = dm.SyntaxHighlighter(self.ui.mem_recall.document())

        self.ui.mem_cfg_tns.setFont(dm.fontSQL)
        self.ui.mem_recall.setFont(dm.fontSQL)
        self.ui.mem_cfg_tns_saved.setFont(dm.fontSQL)
        self.ui.mem_csv.setFont(dm.fontSQL)
        self.ui.mem_editor.setFont(dm.fontSQL)
        self.ui.mem_explain.setFont(dm.fontSQL)
        self.ui.mem_sessions.setFont(dm.fontSQL)


        self.ui.edt_recall.textEdited.connect(self.edt_recall_edited)

        self.lista_chk_obj = [self.ui.chk_obj_table,self.ui.chk_obj_view,self.ui.chk_obj_trigger,self.ui.chk_obj_package,self.ui.chk_obj_procedure,self.ui.chk_obj_funcion]
        for x in self.lista_chk_obj:
            x.clicked.connect(self.edt_objetos_edited)

        self.ui.grid_recall.currentItemChanged.connect(lambda a,b: self.ui.mem_recall.setPlainText(a.text()) )
        
        self.ui.tree_sessions.itemSelectionChanged.connect(lambda: self.ui.mem_sessions.setPlainText( self.ui.tree_sessions.currentItem().text(8) ) )
        for i in range(self.ui.tabWidget.count()):
            self.ui.tabWidget.setTabVisible(i,False)


    ## ==============================================================================================
    ## mostra o formulario
    ## ==============================================================================================

    def showForm(self, formName, info):
        if formName == "Editor":
            self.ui.mem_editor.setPlainText(info)
            self.ui.tabWidget.setCurrentWidget(self.ui.tab_editor)
        if formName == "Recall SQL":
            self.ui.tabWidget.setCurrentWidget(self.ui.tab_recall)
            self.edt_recall_edited()
        if formName == "View Sessions":
            self.ui.tree_sessions.clear()
            self.ui.tabWidget.setCurrentWidget(self.ui.tab_session)
        if formName == "Find Objects": 
            self.ui.tabWidget.setCurrentWidget(self.ui.tab_find_objects)
        if formName == "Explain Query":
            self.ui.tree_explain.clear()
            self.ui.tabWidget.setCurrentWidget(self.ui.tab_explain)
            self.ui.mem_explain.setText( info )
        if formName == "CSV Updater":
            self.ui.mem_csv.setPlainText( dm.configValue("csv_sql") )
            self.ui.tabWidget.setCurrentWidget(self.ui.tab_csv_updater)
        if formName == "Config Tools":
            self.ui.tabWidget.setCurrentWidget(self.ui.tab_config)
            self.ui.mem_cfg_tns.setPlainText( dm.configValue(tag="tns") )
            self.ui.mem_cfg_tns_saved.setPlainText( dm.configValue(tag="tnsSaved") )
            self.ui.edt_cfg_oracle_dir.setText(dm.configValue(tag="OracleInstantClientDir"))
            self.ui.edt_cfg_output_dir.setText(dm.configValue(tag="output_dir"))
            self.ui.edt_cfg_template_dir.setText(dm.configValue(tag="template_dir"))
            self.ui.chk_cfg_dark_mode.setChecked( dm.configValue(tag="EditorSqlDarkMode") == "1"  )
            self.ui.chk_cfg_run_user.setChecked( dm.configValue(tag="cfg_run_user_pref") == "1"  )
        self.show()        

    ## ==============================================================================================
    ## tab de configuracoes
    ## ==============================================================================================

    def bt_cfg_salvar_clicked(self):
        dm.configSave("tns", self.ui.mem_cfg_tns.toPlainText(), "CONFIG")
        dm.configSave("tnsSaved", self.ui.mem_cfg_tns_saved.toPlainText(), "CONFIG")
        dm.configSave("OracleInstantClientDir", self.ui.edt_cfg_oracle_dir.text(), "CONFIG")
        dm.configSave("template_dir", self.ui.edt_cfg_template_dir.text(), "CONFIG")
        dm.configSave("output_dir", self.ui.edt_cfg_output_dir.text(), "CONFIG")
        dm.configSave("EditorSqlDarkMode", "1" if self.ui.chk_cfg_dark_mode.isChecked() else "0" , "CONFIG")
        dm.configSave("cfg_run_user_pref" ,"1" if self.ui.chk_cfg_run_user.isChecked() else "0", "CONFIG" )
        dm.f_logon.reload_conf = True
        QMessageBox.about(None, "Message", "Configs Saved Sucess")

    ## ==============================================================================================
    ## tab atualizador csv
    ## ==============================================================================================

    def bt_csv_populate_thread(self):
        new_file   = self.ui.edt_csv_file.text().replace(".csv","_newdata.csv")
        sql        = self.ui.mem_csv.toPlainText()
        i_start    = 1 if self.ui.chk_csv.isChecked() else 0
        linhas     = dm.loadFromFile(self.ui.edt_csv_file.text())[i_start:]

        ##--tratando SELECT
        if dm.tipoSQL(sql) == 1:
            r = open(new_file,'w')
            for i_linha, s_linha in enumerate( linhas ):
                if i_linha % 50 == 0:
                    self.bt.setText( f"processed line {i_linha} " )

                sql_temp = sql
                a_linha  = s_linha.strip().split(";")
                for i,v in enumerate(a_linha):
                    sql_temp = sql_temp.replace( f"<{i+1}>", v )
                
                dm.db.executeSQL(p_sql=sql_temp, p_tipo='SELECT_DIRECT')
                if dm.db.status_code == 0:
                    retorno = dm.db.cur.fetchone()
                    if retorno != None:
                        r.write(s_linha.strip() + ";" + ( ";".join([str(i) for i in retorno]) )   + "\n")
                    else:
                        r.write(s_linha.strip() + ";\n")
                else:
                    self.bt.setText( dm.db.status_msg )
                    return 0
            r.close()
            self.bt.setText( f"Finished. {i_linha} lines\nSaved file: {new_file} " )

        ##--tratando UPDATE, INSERT, DELETE
        else:
            dados_insert = []
            for i_linha, s_linha in enumerate( linhas ):
                dados_insert.append( tuple(s_linha.split(";")) )                    

                if i_linha % 5000 == 0 or i_linha == (len(linhas) - 1):
                    self.bt.setText( f"processed line {i_linha} " )
                    dm.db.executeSQL(p_sql=sql, p_tipo='EXEC_DIRECT', p_bind_values=dados_insert, p_many=True)
                    if dm.db.status_code == 0:
                        dm.db.commit()
                    else:
                        self.bt.setText( dm.db.status_msg  )
                        return 0
                    dados_insert = []
            self.bt.setText( f"Finished {i_linha} records" )


    def bt_csv_populate_edited(self):
        dm.configSave("csv_sql",self.ui.mem_csv.toPlainText(), "CONFIG")
        if len(self.ui.edt_csv_file.text().strip()) == 0:
            QMessageBox.about(None, "Message", "Filename Required")    
            return

        self.bt = dm.createButtonWork(Run=lambda:( self.th.thread.terminate(), self.bt.close() )   ) 
        self.th = dm.Worker(proc_run=self.bt_csv_populate_thread)


    def bt_csv_of_clicked(self):
        fileName, _ = QFileDialog.getOpenFileName(self,"Open File", "","CSV Files(*.csv);;All Files (*)",  options=QFileDialog.DontUseNativeDialog )
        if fileName:
            self.ui.grid_csv.setRowCount(0)
            self.ui.edt_csv_file.setText(fileName)
            x = dm.loadFromFile(fileName)[0]
            for i,reg in enumerate(x.split(";")):
                self.ui.grid_csv.insertRow(i)
                self.ui.grid_csv.setItem(i,0, QTableWidgetItem(reg)   )

    ## ==============================================================================================
    ## tab explain de querys
    ## ==============================================================================================

    def bt_explain_clicked(self):
        nos = [ None for i in range(5000) ]
        dm.db.executeSQL(p_sql='DELETE FROM PLAN_TABLES', p_tipo='EXEC')
        dm.db.executeSQL(p_sql='EXPLAIN PLAN FOR\n' + self.ui.mem_explain.toPlainText(), p_tipo='EXEC')
        dm.db.executeSQL(p_sql=lib.constantes.C_SQL_EXPLAIN)        
        if dm.db.status_code == 0:
            for reg in dm.db.cur.fetchall():
                id = reg[0]
                parent_id= reg[1]
                if parent_id == -1:
                    l1 = QTreeWidgetItem([ reg[2], reg[3], reg[4], reg[5], reg[6], reg[7], reg[8] ])
                    self.ui.tree_explain.addTopLevelItem(l1)
                    nos[id] = l1
                else:
                    ll = QTreeWidgetItem([ reg[2], reg[3], reg[4], reg[5], reg[6], reg[7], reg[8] ])
                    nos[parent_id].addChild(ll)
                    nos[id] = ll
            self.ui.tree_explain.expandAll()     
            for i in range(8):
                self.ui.tree_explain.setColumnWidth(i, 200)
        else:
            QMessageBox.about(None, "Message", dm.db.status_msg)

    ## ==============================================================================================
    ## tab find de objetos
    ## ==============================================================================================

    def bt_obj_viewcode_clicked(self):
        y   = self.ui.grid_objetos.currentRow()
        obj = self.ui.grid_objetos.item(y,0).text() + '/' + self.ui.grid_objetos.item(y,5).text() + '/' + self.ui.grid_objetos.item(y,1).text()
        self.close()
        dm.f_principal.extrai_ddl(obj)

    def edt_objetos_edited(self):
        if dm.db.prepare() == False:
            QMessageBox.about(None, "Message", self.db.status_msg) 
            return
        
        self.ui.grid_objetos.setRowCount(0)
        ot = [  "'" + x.text() + "'" if x.isChecked() else "'-'" for  x in self.lista_chk_obj ]
        dm.db.executeSQL(p_sql=lib.constantes.C_SQL_FIND_OBJECT % ( self.ui.edt_objetos.text() , ",".join(ot) ) )
        if dm.db.status_code == 0:
            dm.populateGrid(grid=self.ui.grid_objetos,data=dm.db.cur.fetchall(),columnNames=dm.db.col_names, columnTypes=dm.db.col_types)
        else:
            QMessageBox.about(None, "Message", dm.db.status_msg)


    ## ==============================================================================================
    ## tab recall
    ## ==============================================================================================

    def edt_recall_edited(self):
        dm.populateGrid(self.ui.grid_recall, dm.configValue(tag="*recall", w=self.ui.edt_recall.text()) )

    ## ==============================================================================================
    ## tab mostra as sessoes do banco
    ## ==============================================================================================
        
    def bt_sessions_exec_click(self):
        dm.db.executeSQL(p_sql=dm.db.sql_session.replace("<WHERE>", self.ui.cbo_sessions.currentText() ))
        if dm.db.status_code == 0:
            parent_id = "-"
            status    = "-"

            self.ui.tree_sessions.setColumnCount(len(dm.db.col_names) - 3)
            for i in range( self.ui.tree_sessions.columnCount()  ):
                self.ui.tree_sessions.headerItem().setText(i, dm.db.col_names[i+2] )
                self.ui.tree_sessions.setColumnWidth(i,150)
           
            for reg in dm.db.cur.fetchall():
                if parent_id != reg[0]:
                    pai = QTreeWidgetItem([ reg[0] ])
                    pai.H_sql = ""
                    self.ui.tree_sessions.addTopLevelItem(pai)                

                if parent_id + status != reg[0] + reg[1]:
                    meio       = QTreeWidgetItem([ reg[1] ])
                    meio.H_sql = ""
                    pai.addChild(meio)
                
                fim  = QTreeWidgetItem([ str(reg[2]), str(reg[3]), str(reg[4]), str(reg[5]), str(reg[6]), str(reg[7]), str(reg[8]), str(reg[9] ) ,  "" if reg[10] == None else str(reg[10])   ])
                meio.addChild( fim )
                parent_id = reg[0]
                status    = reg[1]
        else:
            QMessageBox.about(None, "Message", dm.db.status_msg)
