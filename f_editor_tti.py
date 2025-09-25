from f_editor_sql import EDITOR_SQL
import ui.d_editor_tti as d_editor_tti
import dm
import dm_const
import os
import subprocess
import time
import csv
from datetime import datetime

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget, QListWidget, QListWidgetItem, QTableWidget, QMessageBox, QInputDialog, QLineEdit
)
class form(QWidget):
    def __init__(self):
        super(form, self).__init__()

        self.db               = dm.ORACLE()
        self.db_timer         = dm.WORKER(proc_run=self.db_timer_run, proc_fim=self.db_timer_stop, autostart=False)
        self.mem_editor_popup = dm.MENU(["Find|Ctrl+F", "-", "Format SQL|Ctrl+Alt+F", "UPPERCASE|Ctrl+U", "lowercase|Ctrl+L", "-", "Paste with UNION|-", "Paste with ITENS|-", "-", "Comment|-", "Uncomment|-", "-", "Describe|-", "Properties|-",'Drop Table|-',"-"],self.mem_editor_popup_click, self)
        
        self.ui = d_editor_tti.Ui_d_editor_tti()
        self.ui.setupUi(self)

        self.ui.bt_tool_clip.clicked.connect(self.bt_tool_clip_clicked)
        self.ui.bt_tool_csv.clicked.connect(self.bt_tool_csv_clicked)
        self.ui.bt_tool_insert.clicked.connect(self.bt_tool_insert_clicked)
        self.ui.bt_tool_column.clicked.connect(lambda: dm.f_editor_form.showForm(self.ui.grid_select, self.db) )
        self.ui.bt_tool_delete.clicked.connect( self.bt_tool_delete_clicked )
        self.ui.bt_fetch.clicked.connect(self.bt_fetch_clicked)

        self.ui.grid_select.doubleClicked.connect( lambda: dm.f_editor_form.showForm(self.ui.grid_select, self.db) )
        self.ui.grid_select.verticalHeader().setDefaultSectionSize(20)
        self.ui.code_completation = QListWidget()
        self.ui.code_completation.setWindowFlag(Qt.FramelessWindowHint)
        self.ui.code_completation.setWindowModality(Qt.ApplicationModal)
        self.ui.code_completation.keyPressEvent = self.code_completation_KEY_PRESS
        self.ui.chk_run_user_local.setChecked( dm.configValue(tag="cfg_run_user_pref") == "1" )
        self.ui.bt_fetch.setVisible(False)
        self.filename    = None
        self.objectname  = None

        self.editorSQL = EDITOR_SQL(text="SELECT * FROM DUAL", customContextMenu=self.mem_editor_popup_show)# dm.EDITOR_SQL(text="SELECT * FROM DUAL", customContextMenu=self.mem_editor_popup_show)
        self.editorSQL.textChanged.connect(self.mem_editor_textchanged)
        self.editorSQL.keyCompleterEvent = self.mem_editor_keyPressEvent
        self.ui.editorLayout.addWidget(self.editorSQL)

    ## ==============================================================================================
    ## TabSheets Titles and Icons
    ## ==============================================================================================
        
    def tabTextIcon(self,Text=None, Icon=None, changed=""):
        tab_pai       = self.parentWidget().parentWidget()
        tab_idx       = tab_pai.indexOf(self)
        if Text != None:
            tab_pai.setTabText(tab_idx,Text)   
        else:
            nome1 = "" if self.filename   == None else os.path.basename(self.filename) + changed
            nome2 = "" if self.objectname == None else "@" + self.objectname
            nome3 = "" if  nome1 == "" or nome2 == "" else " | " 
            if len(nome1 + nome2) == 0:
                nome1 = f"SID={self.db.login_sid}"
            tab_pai.setTabText(tab_idx, (nome2 + nome3 + nome1).strip() )           
        if Icon != None:
            tab_pai.setTabIcon(tab_idx,Icon)   


    ## ==============================================================================================
    ## configura a visibilidade de alguns controles
    ## ==============================================================================================


    def visibility_controls(self, b=False):
        self.ui.chk_all_text.setChecked(True)
        self.ui.chk_run_user_local.setChecked(True)        
        self.ui.bt_fetch.setVisible(b)
        self.ui.bt_tool_clip.setVisible(b)
        self.ui.bt_tool_column.setVisible(b)
        self.ui.bt_tool_csv.setVisible(b)
        self.ui.bt_tool_insert.setVisible(b)
        self.ui.bt_tool_delete.setVisible(b)
        self.ui.chk_all_text.setVisible(b)
        self.ui.chk_parameters.setVisible(b)
        self.ui.chk_run_user_local.setVisible(b)
        self.ui.pc_baixo_grid.setTabVisible(1,False)


    ## ==============================================================================================
    ## menu popup do editor
    ## ==============================================================================================
    def mem_editor_popup_show(self, position):
        txt = self.editorSQL.getSelectedText()
        txt = "" if txt == None else txt
        self.mem_editor_popup.showAction("describe",    txt.upper() in dm.all_tables)
        self.mem_editor_popup.showAction("properties",  txt.upper() in dm.all_tables)
        self.mem_editor_popup.showAction("drop_table",  txt.upper() in dm.all_tables)
        self.mem_editor_popup.showAction("format_sql",  len(txt) > 0)
        self.mem_editor_popup.exec_(self.editorSQL.viewport().mapToGlobal(position))


    def mem_editor_popup_click(self):
        txt = self.editorSQL.getSelectedText()
        
        if self.sender().text() == "Find":
            self.editorSQL.finder_prepare()

        elif self.sender().text() == "UPPERCASE":
            self.editorSQL.replaceSelectedText(txt.upper())

        elif self.sender().text() == "lowercase":
            self.editorSQL.replaceSelectedText(txt.lower())

        elif self.sender().text() == "Format SQL":
            txt = self.editorSQL.getSelectedText()
            if len(txt) > 1:
                arq = dm.generateFileName("fmt.sql")
                jar = dm.generateFileName("dm_format_sql.jar")
                if os.path.exists(jar):
                    o = open( arq , 'w')
                    o.write(txt)
                    o.close()
                    x = subprocess.run(['java', '-jar', jar, arq ], capture_output=True, text=True).stdout
                    self.editorSQL.replaceSelectedText(x)
                    os.remove(arq)
                else:
                    dm.messageBox("dm_format_sql.jar not found")
            else:
                dm.messageBox("No SQL Selected")            

        elif self.sender().text() == "Drop Table":
            if txt in dm.all_tables:
                dm.db.EXECUTE(p_sql='DROP TABLE ' + txt, direct=True)
                dm.messageBox( mensagem=dm.db.status_msg )

        elif self.sender().text() == "Paste with ITENS":
            x = ",\n".join( dm.clipboard.text().strip().split("\n") )
            self.editorSQL.replaceSelectedText( x.strip() )

        elif self.sender().text() == "Paste with UNION":
            x = "\nUNION ALL\n".join(["SELECT '" + d.strip() + "' o from dual" for d in dm.clipboard.text().strip().split("\n")])
            self.editorSQL.replaceSelectedText(x)

        elif self.sender().text() == "Comment":
            x = "/*" + txt.replace(r"\*", "|*").replace("*/", "*|") + "*/"
            self.editorSQL.replaceSelectedText(x)

        elif self.sender().text() == "Uncomment":
            x = txt.replace("/*", "").replace("*/", "").replace("|*", "/*").replace("*|", "*/")
            self.editorSQL.replaceSelectedText(x)

        elif self.sender().text() == "Describe":
            x = dm.db.SELECT(p_sql=dm_const.C_SQL_DESCRIBE % (txt.upper()), fetchSize=0)
            if dm.db.status_code == 0:
                self.grid_describe = QTableWidget()
                self.grid_describe.setWindowFlag(Qt.WindowStaysOnTopHint)
                dm.populateGrid(self.grid_describe, dm.db.col_data, dm.db.col_names)
                self.grid_describe.show()

        elif self.sender().text() == "Properties":
            x = dm.db.SELECT(p_sql=dm_const.C_SQL_PROPERTIES % (txt.upper()), fetchSize=0)
            if dm.db.status_code == 0:
                col_data = []
                for r in dm.db.col_data:
                    for i, info in enumerate(r):
                        col_data = col_data + [(dm.db.col_names[i], info)]
                self.grid_props = QTableWidget()
                self.grid_props.setWindowFlag(Qt.WindowStaysOnTopHint)
                dm.populateGrid(self.grid_props,col_data, ["Property", "Value"] )
                self.grid_props.show()
            else:
                dm.messageBox(dm.db.status_msg)


    ## ==============================================================================================
    ## code completation
    ## ==============================================================================================

    def codeCompletation(self,lista, x, y):
        self.ui.code_completation.move(x,y)
        self.ui.code_completation.clear()
        for x in lista:
            QListWidgetItem(x, self.ui.code_completation)
        self.ui.code_completation.show()

    def mem_editor_textchanged(self):
        self.tabTextIcon(changed="*")

    
    def code_completation_KEY_PRESS(self, event):
        if event.key() in (Qt.Key_Enter, Qt.Key_Return, Qt.Key_Escape):
            event.ignore()
            self.ui.code_completation.close()
            if event.key() != Qt.Key_Escape:
                self.editorSQL.replaceSelectedText( self.ui.code_completation.currentItem().text() )
            return
        QListWidget.keyPressEvent(self.ui.code_completation, event)

    def mem_editor_keyPressEvent(self):
        word  = self.editorSQL.wordOnCursor()
        lista = []

        if word.upper() in dm.all_users:
            dm.db.SELECT(p_sql=dm_const.C_SQL_ALL_TABLES % (word), fetchSize=0)
            lista = [x[0] for x in dm.db.col_data]

        elif word.upper() in dm.all_tables:
            dm.db.SELECT(p_sql=dm_const.C_SQL_ALL_TAB_COLUMNS % (word), fetchSize=0)
            lista = [x[0] for x in dm.db.col_data]

        else:
            x = self.editorSQL.getText().upper().replace(';', ' ').replace(',', ' ').replace("\n", ' ').replace('\t', ' ').replace('.', ' ').replace('*', ' ').replace(' SELECT ', ' ')
            while x.find('  ') > 0:
                x = x.replace('  ', ' ')
            info_a = x.split(' ')
            for i, info in enumerate(info_a):
                if word.upper() == info.upper() and info_a[i-1] in dm.all_tables:
                    dm.db.SELECT(p_sql=dm_const.C_SQL_ALL_TAB_COLUMNS % (info_a[i-1]), fetchSize=0)
                    lista = [x[0] for x in dm.db.col_data]
                    break

        if len(lista) > 0:
            cr = self.editorSQL.cursorRect()
            tt = self.editorSQL.viewport().mapToGlobal(cr.topLeft())
            self.codeCompletation(lista, tt.x(), tt.y())

    ## ==============================================================================================
    ## toolbar - botoes grid
    ## ==============================================================================================

    def bt_tool_delete_clicked(self):
        v_rowid = None
        for x in range( self.ui.grid_select.columnCount() ):
            if self.ui.grid_select.horizontalHeaderItem(x).text() == 'ROWID':
                v_rowid = self.ui.grid_select.item(self.ui.grid_select.currentIndex().row(),x).text()
        if v_rowid == None:
            dm.messageBox("No rowid found!") 
        else:
            self.db.EXECUTE(p_sql=f" delete (\n{self.db._sql}\n) where rowid = '{v_rowid}' ")
            if self.db.status_code != 0:
                dm.messageBox(self.db.status_msg ) 
            else:    
                self.ui.grid_select.removeRow( self.ui.grid_select.currentIndex().row() )
                dm.f_principal.pc_editor_tabchange()

    ##-------------
                
    def bt_fetch_clicked_start(self):
        try:
            while self.bt.isVisible():
                data = self.db.cur.fetchmany(500)
                if len(data) == 0:
                    self.ui.bt_fetch.close()
                    break
                dm.populateGrid(grid=self.ui.grid_select,data=data,appending=True,columnTypes=self.db.col_types)
                self.bt.setText( str(self.ui.grid_select.rowCount()) )
            self.bt.close()
        except Exception as e:
            self.bt.setText( str(e) )
        

    def bt_fetch_clicked(self):
        self.bt        = dm.createButtonWork()
        self.th        = dm.WORKER(proc_run=self.bt_fetch_clicked_start)

    ##-------------

    def bt_tool_insert_clicked_start(self):
        try:
            self.db.SELECT(p_sql=self.pegaSQL(),direct=self.ui.chk_run_user_local.isChecked() )
            if self.db.status_code == 0:
                qtd            = 0 
                ins_file       = open( file=dm.generateFileName("generated_inserts.sql",inOutputDir=True), mode="w", encoding="utf-8")
                s_insert_title = f"""insert into {self.bt.H_table_name}({",".join(self.db.col_names)}) """
                while self.bt.isVisible():
                    data = self.db.cur.fetchmany(5000)
                    qtd  = qtd + len(data)
                    if len(data) == 0:
                        break
                    for r in data:
                        ins_file.write( f"""{s_insert_title} values ({ ",".join(  [ self.db.value(xx) for xx in r]   ) });\n""" )
                    self.bt.setText( f"Exporting ... {qtd}" )
                                    
                ins_file.close()
                self.bt.setText(f"Saved File generated_inserts.sql: {qtd} rows")
            else:
                self.bt.setText(self.db.status_msg)

        except Exception as e:
            self.bt.setText(f"Error: { str(e) }")

    def bt_tool_insert_clicked(self):
        if self.db.prepare() == False: return
                
        table_name, ok = QInputDialog().getText(self, "Export Data" , "Type TableName",  QLineEdit.Normal, "__tablename__")                        
        if ok:    
            self.bt              = dm.createButtonWork()
            self.bt.H_table_name = table_name           
            self.th              = dm.WORKER(proc_run=self.bt_tool_insert_clicked_start)

    ##-------------

    def bt_tool_csv_clicked_start(self):
        try:
            self.db.SELECT(p_sql=self.pegaSQL(), direct=self.ui.chk_run_user_local.isChecked() )
            if self.db.status_code == 0:
                qtd      = 0 
                csv_file = open( file=dm.generateFileName("exported.csv",inOutputDir=True), mode="w", encoding="utf-8")
                arq      = csv.writer(csv_file,delimiter=";",quotechar='"', escapechar="\\",quoting=csv.QUOTE_ALL)
                arq.writerow( self.db.col_names )
                while self.bt.isVisible():
                    data = self.db.cur.fetchmany(5000)
                    qtd  = qtd + len(data)
                    if len(data) == 0:
                        break
                    arq.writerows(data)
                    self.bt.setText( f"Exporting ... {qtd}" )
                csv_file.close()
                self.bt.setText(f"Saved File exported.csv: {qtd} rows")
            else:
                self.bt.setText(self.db.status_msg)
        except Exception as e:
            self.bt.setText(f"Error: { str(e) }")


    def bt_tool_csv_clicked(self):
        if self.db.prepare() == False: return
                
        if QMessageBox.question(self,"Confirm","Confirm export to csv?",QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.bt = dm.createButtonWork()
            self.th = dm.WORKER(proc_run=self.bt_tool_csv_clicked_start)
            """
            workbook = xlsxwriter.Workbook('/algar/relatorio.xlsx')
            sheet = workbook.add_worksheet()

            self.db.SELECT(p_sql=self.pegaSQL(), direct=self.ui.chk_run_user_local.isChecked(), fetchSize=0 )
            for r, row in enumerate(self.db.col_data):
                    for c, col in enumerate(row):
                            if "LOB" in str(type(col)).upper():
                                info = col.read()
                            else:
                                info = col
                            sheet.write(r, c, info)

            workbook.close()
            """

    ##-------------

    def bt_tool_clip_clicked(self):
        selection = self.ui.grid_select.selectedIndexes()
        if selection:
            rows     = sorted(index.row() for index in selection)
            columns  = sorted(index.column() for index in selection)
            rowcount = rows[-1] - rows[0] + 1
            colcount = columns[-1] - columns[0] + 1
            table = [[''] * colcount for _ in range(rowcount)]
            for index in selection:
                row = index.row() - rows[0]
                column = index.column() - columns[0]
                table[row][column] = (str(index.data()) + " ").strip()
            stream = ""
            for r in table:
                stream = stream + "\t".join(r) + "\n"
            dm.clipboard.setText(stream)
            dm.messageBox("Copied to Clipboard")

    ## ==============================================================================================
    ## executar SQL
    ## ==============================================================================================

    def db_timer_stop(self):
        self.ui.lb_timer.setText(  str(self.db_timer.dt_fim - self.db_timer.dt_ini)[0:-3]  )
        self.tabTextIcon(Icon=dm.iconBlue)
        dm.f_principal.pc_editor_tabchange()

    def db_timer_start(self):
        self.db_timer.stop   = False
        self.db_timer.dt_ini = datetime.now()
        self.db.in_execution = True
        self.tabTextIcon(Icon=dm.iconRed)
        dm.f_principal.pc_editor_tabchange()
        self.db_timer.start()

    def db_timer_run(self):
        while self.db_timer.stop == False:
            self.db_timer.dt_fim = datetime.now()
            self.ui.lb_timer.setText(  str(self.db_timer.dt_fim-self.db_timer.dt_ini)[0:-7]  )
            time.sleep(0.5)




    def pegaSQL(self):
        sql = self.editorSQL.getText()

        if not self.ui.chk_all_text.isChecked():
            sql_selected = self.editorSQL.getSelectedText()
            if len(sql_selected.strip()) > 0:
                sql = sql_selected

        if self.ui.chk_parameters.isChecked() == False and self.objectname == None and "&" in sql:
            while "&" in sql:
                idx = sql.find("&")
                x   = sql[idx:]
                for i in range( len(x) ):
                    if x[i:i+1] in ['"',"'",";"," ","\n","",","]:
                        text, ok = QInputDialog().getText(self, "value" , f"Type Value Of: {x[0:i]}",  QLineEdit.Normal, "")                        
                        if ok:
                            print(x[0:i] + "-" + text)
                            sql = sql.replace( x[0:i] , text )
                        else:
                            return None
                        break
        return sql.strip()



    def executeSQL_finish(self):
        self.db_timer.stop = True
        if self.objectname != None:
            if self.db.status_code != 0:
                dm.messageBox(self.db.status_msg)               
            else:
                ii = self.objectname.split(".")
                self.db.SELECT(p_sql=dm_const.C_SQL_ALL_ERRORS % (ii[0], ii[1]), direct=True, fetchSize=0 )
                dm.populateGrid(self.ui.grid_select, data=self.db.col_data,columnNames=self.db.col_names, columnTypes=self.db.col_types)
                for ii in range(len(self.db.col_data)):
                    self.ui.grid_select.setColumnWidth(2, 650)
                    self.ui.grid_select.setRowHeight(ii, 100)

        else:
            if self.db.status_code != 0 or self.db._sql_type != 1:
                dm.messageBox(self.db.status_msg)               
            elif self.db._sql_type == 1:
                dm.populateGrid(grid=self.ui.grid_select, data=self.db.col_data, columnNames=self.db.col_names, columnTypes=self.db.col_types)
        
        self.ui.mem_dbms.setPlainText(self.db.dbms_output)

    def executeSQL_start(self):
        try:
            if self.db._sql_type == 1:
                self.db.SELECT(p_sql=self.db._sql, logger=True, direct=self.ui.chk_run_user_local.isChecked(), fetchSize=20 )
            else:
                self.db.EXECUTE(p_sql=self.db._sql, logger=True, direct=self.ui.chk_run_user_local.isChecked())
        except Exception as e:
            self.db.status_code = -1
            self.db.status_msg = str(e)

    def executeSQL(self):
        if self.db.prepare() == False: return
        
        self.ui.grid_select.setRowCount(0)
        self.ui.grid_select.setColumnCount(0)
        self.db._sql        = self.pegaSQL()
        self.db._sql_type   = dm.tipoSQL(self.db._sql)    
                     

        self.ui.bt_fetch.setVisible(self.db._sql_type == 1)

        if self.db._sql != None:
            self.db_timer_start()
            self.th = dm.WORKER(proc_run=self.executeSQL_start, proc_fim=self.executeSQL_finish)
