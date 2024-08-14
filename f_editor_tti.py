import d_editor_tti
import dm
import dm_const
import os
import subprocess
import time
import csv
from datetime import datetime

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *



class form(QWidget):
    def __init__(self):
        self.db       = dm.HOracle()
        self.db_timer = dm.Worker(self.db_timer_thread, autostart=False)
        
        super(form, self).__init__()
        self.ui = d_editor_tti.Ui_d_editor_tti()
        self.ui.setupUi(self)
        self.msgSc = QShortcut(QKeySequence('Ctrl+F'), self)
        self.msgSc.activated.connect( lambda : dm.f_editor_find.showFindReplace(self.ui.mem_editor) )
        self.ui.bt_tool_clip.clicked.connect(self.bt_tool_clip_clicked)
        self.ui.bt_tool_csv.clicked.connect(self.bt_tool_csv_clicked)
        self.ui.bt_tool_insert.clicked.connect(self.bt_tool_insert_clicked)
        self.ui.bt_tool_column.clicked.connect(lambda: dm.f_editor_form.showForm(self.ui.grid_select, self.db) )
        self.ui.bt_tool_delete.clicked.connect( self.bt_tool_delete_clicked )
        self.ui.bt_fetch.clicked.connect(self.bt_fetch_clicked)
        self.ui.mem_editor.keyPressEvent = self.mem_editor_keyPressEvent
        self.ui.mem_editor.setFont(dm.fontSQL)
        self.ui.mem_editor.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.mem_editor.customContextMenuRequested.connect( lambda position: self.G_popup_editor.exec_(self.ui.mem_editor.viewport().mapToGlobal(position)) )
        self.ui.mem_editor.setPlainText("SELECT * FROM DUAL")
        self.ui.mem_editor.textChanged.connect(self.mem_editor_textchanged)
        self.G_mem_editor_highlight = dm.SyntaxHighlighter(self.ui.mem_editor.document())
        self.ui.mem_dbms.setFont(dm.fontSQL)
        self.G_popup_editor = dm.createMenu(self, ["Format SQL|Ctrl+Alt+F", "UPPERCASE|Ctrl+U", "lowercase|Ctrl+L", "-", "Paste with UNION", "Paste with ITENS", "-", "Comment", "Uncomment", "-", "Describe", "Properties"],self.popup_editor_item_click)
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
    ## menu popup do editor
    ## ==============================================================================================
            
    def popup_editor_item_click(self):
        txt = self.ui.mem_editor.textCursor().selection().toPlainText()
        if self.sender().text() == "UPPERCASE":
            self.ui.mem_editor.textCursor().insertText(txt.upper())

        if self.sender().text() == "lowercase":
            self.ui.mem_editor.textCursor().insertText(txt.lower())

        if self.sender().text() == "Format SQL":
            txt = self.ui.mem_editor.textCursor().selection().toPlainText()
            if len(txt) > 1:
                arq = dm.do_filename("fmt.sql")
                jar = dm.do_filename("FormatSQL.jar")
                if os.path.exists(jar):
                    o = open( arq , 'w')
                    o.write(txt)
                    o.close()
                    x = subprocess.run(['java', '-jar', jar, arq ], capture_output=True, text=True).stdout
                    self.ui.mem_editor.textCursor().insertText(x)
                    os.remove(arq)
                else:
                    QMessageBox.about(None, "Message", "FormatSQL.jar not found")
            else:
                QMessageBox.about(None, "Message", "No SQL Selected")            

        if self.sender().text() == "Paste with ITENS":
            x = ",\n".join( dm.clipboard.text().strip().split("\n") )
            self.ui.mem_editor.textCursor().insertText( x.strip() )

        if self.sender().text() == "Paste with UNION":
            x = "\nUNION ALL\n".join(["SELECT '" + d.strip() + "' o from dual" for d in dm.clipboard.text().strip().split("\n")])
            self.ui.mem_editor.textCursor().insertText(x)

        if self.sender().text() == "Comment":
            x = "/*" + txt.replace("\*", "|*").replace("*/", "*|") + "*/"
            self.ui.mem_editor.textCursor().insertText(x)

        if self.sender().text() == "Uncomment":
            x = txt.replace("/*", "").replace("*/", "").replace("|*", "/*").replace("*|", "*/")
            self.ui.mem_editor.textCursor().insertText(x)

        if self.sender().text() == "Describe":
            x = dm.db.executeSQL(p_sql=dm_const.C_SQL_DESCRIBE % (txt.upper()))
            if dm.db.status_code == 0:
                self.grid_describe = QTableWidget()
                dm.populateGrid(self.grid_describe, dm.db.cur.fetchall(), dm.db.col_names)
                self.grid_describe.show()

        if self.sender().text() == "Properties":
            x = dm.db.executeSQL(p_sql=dm_const.C_SQL_PROPERTIES % (txt.upper()))
            if dm.db.status_code == 0:
                col_data = []
                for r in dm.db.cur.fetchall():
                    for i, info in enumerate(r):
                        col_data = col_data + [(dm.db.col_names[i], info)]
                self.grid_props = QTableWidget()
                dm.populateGrid(self.grid_props,col_data, ["Property", "Value"] )
                self.grid_props.show()
            else:
                QMessageBox.about(None, "Message", dm.db.status_msg)


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
                self.ui.mem_editor.textCursor().insertText( self.ui.code_completation.currentItem().text() )
            return
        QListWidget.keyPressEvent(self.ui.code_completation, event)

    def mem_editor_linenumber(self):
        x     = self.ui.mem_editor.textCursor().position().real
        block = self.ui.mem_editor.toPlainText()[1 : x]
        self.ui.lb_row.setText( str( block.count("\n") + 1) )

    def mem_editor_keyPressEvent(self, event):
        try:
            tc = self.ui.mem_editor.textCursor()

            if event.key() == Qt.Key_Return:
                y = tc.blockNumber()
                i = -1
                for i,tt in enumerate(  self.ui.mem_editor.document().findBlockByLineNumber(y).text() ):
                    if tt != ' ':
                        break
                tc.insertText("\n" + ("" if i == -1 else (" " * i) )  )
                self.mem_editor_linenumber()
                return

            if event.key() in [Qt.Key_Tab, Qt.Key_Backtab]:
                if tc.hasSelection():
                    i_start = tc.selectionStart().real
                    if event.key() == Qt.Key_Tab:
                        new_text = "\n".join(["  " + x for x in tc.selection().toPlainText().split("\n")])
                    else:
                        new_text = "\n".join([x.replace("  ", "", 1) for x in tc.selection().toPlainText().split("\n")])
                    tc.insertText(new_text)
                    tc.setPosition(i_start)
                    tc.setPosition(i_start + len(new_text), QTextCursor.KeepAnchor)
                    self.ui.mem_editor.setTextCursor(tc)
                else:
                    tc.insertText("  ")
                self.mem_editor_linenumber()
                return

            if event.key() == 46:
                tc.select(QTextCursor.WordUnderCursor)
                lista = []

                if tc.selectedText().upper() in dm.all_users:
                    dm.db.executeSQL(p_sql=dm_const.C_SQL_ALL_TABLES % (tc.selectedText()))
                    lista = [x[0] for x in dm.db.cur.fetchall()]

                elif tc.selectedText().upper() in dm.all_tables:
                    dm.db.executeSQL(p_sql=dm_const.C_SQL_ALL_TAB_COLUMNS % (tc.selectedText()))
                    lista = [x[0] for x in dm.db.cur.fetchall()]

                else:
                    x = self.ui.mem_editor.toPlainText().upper().replace(';', ' ').replace(',', ' ').replace("\n", ' ').replace('\t', ' ').replace('.', ' ').replace('*', ' ').replace(' SELECT ', ' ')
                    while x.find('  ') > 0:
                        x = x.replace('  ', ' ')
                    info_a = x.split(' ')
                    for i, info in enumerate(info_a):
                        if tc.selectedText().upper() == info.upper() and info_a[i-1] in dm.all_tables:
                            dm.db.executeSQL(p_sql=dm_const.C_SQL_ALL_TAB_COLUMNS % (info_a[i-1]))
                            lista = [x[0] for x in dm.db.cur.fetchall()]
                            break

                if len(lista) > 0:
                    cr = self.ui.mem_editor.cursorRect()
                    tt = self.ui.mem_editor.viewport().mapToGlobal(cr.topLeft())
                    self.codeCompletation(lista, tt.x(), tt.y())
        except Exception as e:
            print( str(e) )
        QPlainTextEdit.keyPressEvent(self.ui.mem_editor, event)
        self.mem_editor_linenumber()


    ## ==============================================================================================
    ## executar SQL
    ## ==============================================================================================

    def db_hide_grid_opts(self, b):
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
        self.ui.tabWidget.setTabVisible(1,False)


    def db_timer_thread(self):
        dt_ini = datetime.now()
        self.db_timer_stop = False
        while self.db_timer_stop == False:
            self.ui.lb_timer.setText(  str(datetime.now() - dt_ini).split(".")[0]  )
            time.sleep(1)

    def pegaSQL(self):
        sql = self.ui.mem_editor.toPlainText()

        if not self.ui.chk_all_text.isChecked():
            sql = self.ui.mem_editor.textCursor().selection().toPlainText()
            if len(sql.strip()) == 0:
                x = self.ui.mem_editor.textCursor().position().real
                t = ""
                for sql in self.ui.mem_editor.toPlainText().split(";"):
                    if len(t+sql) >= x:
                        break
                    t = t + sql
        
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
        return sql

    def th_process_exec_grid(self):
        if self.objectname != None:
            if self.db.status_code != 0:
                QMessageBox.about(None, "Message", self.db.status_msg)               
            else:
                ii = self.objectname.split(".")
                self.db.executeSQL(p_sql=dm_const.C_SQL_ALL_ERRORS % (ii[0], ii[1]), p_tipo='SELECT_DIRECT' )
                col_data = self.db.cur.fetchall()
                dm.populateGrid(self.ui.grid_select, data=col_data,columnNames=self.db.col_names, columnTypes=self.db.col_types)
                for ii in range(len(col_data)):
                    self.ui.grid_select.setColumnWidth(2, 650)
                    self.ui.grid_select.setRowHeight(ii, 100)
        else:
            if self.db.status_code != 0 or self.db._sql_type != 1:
                QMessageBox.about(None, "Message", self.db.status_msg)               
            elif self.db._sql_type == 1:
                dm.populateGrid(grid=self.ui.grid_select, data=self.db.col_data,columnNames=self.db.col_names, columnTypes=self.db.col_types)
        self.ui.mem_dbms.setPlainText(self.db.dbms_output)
        dm.f_principal.pc_editor_tabchange()
        self.tabTextIcon(Icon=dm.iconBlue)

    def th_process_exec(self):
        try:
            if self.db._sql_type == 1:
                self.db.executeSQL(p_sql=self.db._sql, p_Log=True, p_tipo='SELECT' + self.db._sql_direct)
                if self.db.status_code == 0:
                    self.db.col_data = self.db.cur.fetchmany(20)
            else:
                self.db.executeSQL(p_sql=self.db._sql, p_Log=True, p_tipo='EXEC' + self.db._sql_direct)
        except Exception as e:
            self.db.status_code = -1
            self.db.status_msg = str(e)
        self.db_timer_stop = True


    def executeSQL(self):
        self.ui.grid_select.setRowCount(0)
        self.ui.grid_select.setColumnCount(0)

        if self.db.prepare() == False:
            QMessageBox.about(None, "Message", self.db.status_msg) 
            return

        self.db._sql        = self.pegaSQL()
        self.db._sql_type   = dm.tipoSQL(self.db._sql)                     
        self.db._sql_direct = "_DIRECT" if self.ui.chk_run_user_local.isChecked() else ""        
        self.ui.bt_fetch.setVisible(self.db._sql_type == 1)

        if self.db._sql != None:
            self.db.in_execution = True
            self.tabTextIcon(Icon=dm.iconRed)
            dm.f_principal.pc_editor_tabchange()
            self.db_timer.thread.start()   
            self.th = dm.Worker(proc_run=self.th_process_exec, proc_fim=self.th_process_exec_grid)



    ## ==============================================================================================
    ## toolbar - botoes grid
    ## ==============================================================================================



    def bt_tool_delete_clicked(self):
        v_rowid = None
        for x in range( self.ui.grid_select.columnCount() ):
            if self.ui.grid_select.horizontalHeaderItem(x).text() == 'ROWID':
                v_rowid = self.ui.grid_select.item(self.ui.grid_select.currentIndex().row(),x).text()
        if v_rowid == None:
            QMessageBox.about(None, "Message", "No rowid found!") 
        else:
            self.db.executeSQL(p_sql=f" delete (\n{self.db._sql}\n) where rowid = '{v_rowid}' ",p_tipo="EXEC")
            if self.db.status_code != 0:
                QMessageBox.about(None, "Message", self.db.status_msg ) 
            else:    
                self.ui.grid_select.removeRow( self.ui.grid_select.currentIndex().row() )
                dm.f_principal.pc_editor_tabchange()

    ##-------------
                
    def bt_fetch_clicked_thread_stop(self):
        self.bt.H_stop = True
        self.bt.close()


    def bt_fetch_clicked_thread(self):
        try:
            while self.bt.H_stop == False:
                data = self.db.cur.fetchmany(500)
                if len(data) == 0:
                    self.ui.bt_fetch.setVisible(False)
                    break
                dm.populateGrid(grid=self.ui.grid_select,data=data,appending=True,columnTypes=self.db.col_types)
                self.bt.setText( str(self.ui.grid_select.rowCount()) )
            self.bt.close()
        except Exception as e:
            self.bt.setText( str(e) )
        

    def bt_fetch_clicked(self):
        self.bt        = dm.createButtonWork(Run=lambda:(self.bt_fetch_clicked_thread_stop())  )
        self.bt.H_stop = False
        self.th        = dm.Worker(proc_run=self.bt_fetch_clicked_thread)

    ##-------------

    def bt_tool_insert_clicked_thread(self):
        try:
            self.db.executeSQL(p_sql=self.pegaSQL(), p_tipo='SELECT' + ("_DIRECT" if self.ui.chk_run_user_local.isChecked() else ""))
            if self.db.status_code == 0:
                qtd            = 0 
                ins_file       = open( file=dm.do_filename("generated_inserts.sql",path="output_dir"), mode="w", encoding="utf-8")
                s_insert_title = f"""insert into {self.bt.H_table_name}({",".join(self.db.col_names)}) """
                while True:
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
        if self.db.prepare() == False:
            QMessageBox.about(None, "Message", self.db.status_msg) 
            return
                
        table_name, ok = QInputDialog().getText(self, "Export Data" , "Type TableName",  QLineEdit.Normal, "__tablename__")                        
        if ok:    
            self.bt              = dm.createButtonWork(Run=lambda:(self.th.thread.terminate(),self.bt.close()))
            self.bt.H_table_name = table_name           
            self.th              = dm.Worker(proc_run=self.bt_tool_insert_clicked_thread)

    ##-------------

    def bt_tool_csv_clicked_thread(self):
        try:
            self.db.executeSQL(p_sql=self.pegaSQL(), p_tipo='SELECT' + ("_DIRECT" if self.ui.chk_run_user_local.isChecked() else ""))
            if self.db.status_code == 0:
                qtd      = 0 
                csv_file = open( file=dm.do_filename("exported.csv",path="output_dir"), mode="w", encoding="utf-8")
                arq      = csv.writer(csv_file,delimiter=";",quotechar='"', escapechar="\\",quoting=csv.QUOTE_ALL)
                arq.writerow( self.db.col_names )
                while True:
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
        if self.db.prepare() == False:
            QMessageBox.about(None, "Message", self.db.status_msg) 
            return
                
        if QMessageBox.question(self,"Confirm","Confirm export to csv?",QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.bt = dm.createButtonWork(Run=lambda:(self.th.thread.terminate(),self.bt.close()))
            self.th = dm.Worker(proc_run=self.bt_tool_csv_clicked_thread)

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
        QMessageBox.about(self, "Message", "Copied to Clipboard")
