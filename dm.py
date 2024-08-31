import oracledb
import os
import sys
import sqlite3
import platform

import f_principal
import f_logon
import f_editor_find
import f_editor_form
import f_editor
import dm_const

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from threading import Thread

## ==============================================================================================
## operacoes com arquivos
## ==============================================================================================

def generateFileName(filename, path="root"):
    v_path = os.path.dirname(sys.argv[0]) if path == "root" else configValue(tag="output_dir")
    return os.path.join( v_path, filename )



def loadFromFile(fileName):
    r      = open(fileName,'r', encoding='utf-8', errors='ignore')
    linhas = r.readlines()
    r.close()
    return linhas 


def messageBox(mensagem, printable=True):
    if printable:
        QMessageBox.about(None, "Message", mensagem)     

## ==============================================================================================
##
## ==============================================================================================

def setDarkMode(app):
    if configValue(tag="EditorSqlDarkMode") == "1":
        app.setStyle('Fusion')
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(25, 25, 25)) ##25, 25, 25
        palette.setColor(QPalette.AlternateBase, QColor(35, 35, 35)) ##53, 53, 53
        palette.setColor(QPalette.ToolTipBase, Qt.black)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, Qt.black)
        app.setPalette(palette)    


## ==============================================================================================
## Create Button to Thread Work Message
## ==============================================================================================

def createButtonWork(Run=None, Size=QSize(600, 100), Text="wait a few seconds...", Frameless=True):
    G = QPushButton()
    G.setFixedSize(Size)
    G.setIcon(iconRed)
    G.setWindowModality(Qt.ApplicationModal)
    if Frameless:
        G.setWindowFlag(Qt.FramelessWindowHint)
    G.setText(Text)
    G.clicked.connect( Run if Run != None else lambda:(G.close()) )
    G.show()
    return G



 

## ==============================================================================================
## create menus
## ==============================================================================================

def createMenu(obj, items, procmenuClick):
    menu = QMenu()
    menu.setStyleSheet("QMenu {background-color:white; color:black} QMenu::item:selected {background:blue; color:white}") 
    for x in items:
        if x == "-":
            menu.addSeparator()
        else:
            a = QAction(x.split("|")[0], obj)
            if "|" in x:
                a.setShortcut(QKeySequence(x.split("|")[1]))
                a.setShortcutVisibleInContextMenu(True)
            a.triggered.connect(procmenuClick)
            obj.addAction(a)
            menu.addAction(a)
    return menu

## ==============================================================================================
## funcoes de leitura/escrita de configuracoes/
## ==============================================================================================

def configValue(tag=None, w="%"):
    fileConfig       = generateFileName("AlgarSQL.db")
    if os.path.exists(fileConfig) == False:
        return ""
    conn    = sqlite3.connect(fileConfig)
    cursor  = conn.cursor()
    ret     = None
    if tag == "*recall":
        ret     = cursor.execute( f"select * from sql_history where 1=1 and info like '{w}' order by 1 desc").fetchall()
    else:
        reg     = cursor.execute( f"select info from config where node = '{tag}'" ).fetchall()
        ret     = "" if len(reg) == 0 else reg[0][0]
    conn.close()
    return ret


def configSave(tagName, tagValue, p_tipo):
    conn             = sqlite3.connect(generateFileName("AlgarSQL.db"))
    cursor           = conn.cursor()
    cursor.execute("CREATE TABLE if not exists config      ( node VARCHAR(11), info text ) ")
    cursor.execute("CREATE TABLE if not exists sql_history ( dt datetime default current_timestamp, dbname varchar(50), info text ) ")
    if p_tipo == "CONFIG":
        cursor.execute( f"delete from config where node = '{tagName}'" )
        cursor.execute("insert into config (node,info) values (?,?)", (tagName, tagValue))
    if p_tipo == "SQL_HISTORY":
        cursor.execute("insert into sql_history (dbname,info) values (?,?)", (tagName, tagValue))
    conn.commit()
    conn.close()

## ==============================================================================================
## 
## ==============================================================================================

def populateGrid(grid: QTableWidget, data , columnNames=None, columnTypes=None, editableColumns="", appending=False, columnWidth=200):
    row_idx = 0 if appending == False else grid.rowCount()
    
    grid.setRowCount( len(data) + row_idx )

    if appending == False:
        if columnNames != None:
            grid.col_names = columnNames
            grid.col_types = columnTypes
            
            grid.setColumnCount(len(columnNames))
            for i,x in enumerate(columnNames):
                item  = QTableWidgetItem()
                item.setText(x)
                grid.setHorizontalHeaderItem(i, item) 
                grid.setColumnWidth(i, columnWidth)

    for i,x in enumerate(data):
        for j,a in enumerate(x):
            item = QTableWidgetItem()
            if editableColumns.find( f"-{j}-" ) < 0:
                item.setFlags( item.flags() ^ Qt.ItemIsEditable )
            
            if a == None:
                tt = ""  
            elif columnTypes != None and "DATE" in columnTypes[j]:
                tt = a.strftime("%d/%m/%Y %H:%M:%S")
            elif columnTypes != None and "BLOB" in columnTypes[j]:
                tt = a.read().decode("utf-8", errors='replace')
            else:
                tt = str(a)
            item.setText( tt )
            grid.setItem(i + row_idx,j,item)

## ==============================================================================================
##
## ==============================================================================================
        
def tipoSQL(SQL,checkCreateObj=False):
    x = SQL.upper() + "\n"

    while x.find("--") >= 0:
        a = x.find("--")
        b = x.find("\n",a)
        x = x[0:a] + x[b:]

    while x.find("/*") >= 0:
        a = x.find("/*")
        b = x.find("*/",a)
        if b == -1:
            break
        x = x[0:a] + x[b+2:]    

    if checkCreateObj:
        if x.strip().startswith('CREATE'):
            x = x.replace("\n"," ").replace(" BODY "," ").replace("("," ").replace('"','')
            while x.find("  ") >= 0:
                x = x.replace("  "," ")
            b = ""
            d = x.split(" ")
            for i,dd in enumerate(d):
                if dd in ["PROCEDURE", "TABLE", "TRIGGER", "VIEW", "PACKAGE","FUNCTION"]:
                    b = d[i+1].strip()
                    break
            return 3,b
        else:
            return -3,None
    
    if x.strip().startswith('SELECT') or x.strip().startswith('WITH'):
        return 1
    return 2

## ==============================================================================================
## thread
## ==============================================================================================


class Worker(QObject):
    finished = pyqtSignal()
    def __init__(self, proc_run, proc_fim=None, autostart=True):
        super().__init__()
        self.thread = QThread()
        self.proc_run = proc_run
        self.moveToThread(self.thread)
        self.finished.connect(self.thread.quit)        
        self.thread.started.connect( self.run )
        if proc_fim != None:
            self.thread.finished.connect(proc_fim) 
        if autostart:
            self.start()
    
    def start(self):
        self.thread.start()

    def run(self):
        self.proc_run()
        self.finished.emit()  



## ==============================================================================================
## CLASSE DE CONEXAO COM ORACLE
## ==============================================================================================



class ORACLE:
    def __init__(self):
        self.con            = None
        self.cur            = None
        self.is_connected   = False
        self.in_transaction = False
        self.in_execution   = False
        self.is_direct      = False
        self.login_sid      = 0
        self.last_sql       = "-"
        self.p_usuario      = None
        self.p_senha        = None
        self.p_tns          = None
        self.dbms_output    = ""


    def value(self, v):
        if v == None:
            return "null"
        elif "date" in str(type(v)):
            return f"to_date('{v}','YYYY-MM-DD HH24:MI:SS')"
        else:
            return f"'{str(v)}'"
        


    def prepare(self):
        try:
            self.con.ping()
            self.is_connected = True
        except:
            self.CONNECT(db.p_usuario, db.p_senha, db.p_tns, db.is_direct)
        return self.is_connected
    


    def CONNECT(self, p_usuario, p_senha, p_tns, p_is_direct):
        global C_SQL_SESSIONS
        self.in_transaction = False
        self.in_execution   = False
        self.is_connected   = False
        self.is_direct      = p_is_direct

        if p_usuario == None or p_senha == None or p_tns == None:
            return (-1,"Parameter User/Pass Invalid!")
        try:
            self.p_usuario    = p_usuario
            self.p_senha      = p_senha
            self.p_tns        = p_tns

            print( f"logging into {self.p_usuario}@{self.p_tns}")
            self.con          = oracledb.connect( user=self.p_usuario, password=self.p_senha, dsn=self.p_tns)
            self.cur          = self.con.cursor()
            self.login_sid    = 0
            self.login_serial = 0
            self.cur.execute(dm_const.C_SQL_START)
            self.cur.execute(dm_const.C_SQL_ENABLE_WARN)

            for r in self.cur.execute("select global_name, banner, Sys_Context('USERENV', 'SID') from global_name, v$version").fetchall():
                self.login_global_name = r[0]
                self.login_banner      = r[1]
                self.login_sid         = r[2]

            self.sql_session = dm_const.C_SQL_SESSIONS_ORA
            if p_is_direct == False:
                self.SELECT(p_sql="SELECT OWNER FROM ALL_VIEWS WHERE VIEW_NAME = 'VW_SESSIONS' ORDER BY 1")
                if self.status_code == 0:
                    rr = self.cur.fetchone()
                    self.sql_session = dm_const.C_SQL_SESSIONS_ALGAR.replace("<TABELA>", rr[0] + ".VW_SESSIONS")

            self.con.autocommit = False
            self.is_connected   = True
            self.status_code = 0
            self.status_msg  = 'OK'
        except Exception as e:
            self.status_code = -1
            self.status_msg  = str(e)



    def disconnect(self):
        try:
            if self.con != None:
                t1 = Thread(target=lambda: self.con.close())
                t1.start()
                t1.join(3)
        except:
            print("Not Connected")
        self.p_usuario      = None
        self.is_connected   = False  
        self.in_transaction = False
        self.in_execution   = False  



    def commit(self):
        self.con.commit()
        self.in_transaction = False



    def rollback(self):
        self.con.rollback()
        self.in_transaction = False



    def stopSQL(self):
        self.con.cancel()  


    def create_lob(self, data, is_blob=False):
        x = self.con.createlob(oracledb.DB_TYPE_BLOB if is_blob else oracledb.DB_TYPE_CLOB)
        x.open()
        x.write(data)
        return x
    
    def prepareVars(self, p_sql, logger):
        self.dbms_output  = ""
        self.col_names    = []
        self.col_types    = []
        self.col_data  = []        
        self.in_execution = True
        if logger and self.last_sql != p_sql:
            configSave(self.login_global_name, p_sql,"SQL_HISTORY")
            self.last_sql = p_sql            


    def EXECUTE(self,p_sql, logger=False, p_bind_values=None, p_many=False, direct=False):
        self.prepareVars(p_sql=p_sql, logger=logger)
        try:
            if direct or self.is_direct:
                (self.cur.executemany if p_many else self.cur.execute) ( statement=p_sql , parameters=p_bind_values)
                self.status_code   = 0
                self.status_msg    = "SUCESSO"
            else:
                ret1  = self.cur.var(int)
                ret2  = self.cur.var(str)
                if p_bind_values != None:
                    names = ["","p_str","p_date","p_clob","p_blob",""]
                    self.cur.callproc("user_exec.pc_exec_dml.pr_bind_prepare", (p_sql, ret1, ret2))

                    if ret1.getvalue() != 0:
                        raise Exception(ret2.getvalue())
                    
                    for x in p_bind_values.keys():
                        idx = 1
                        if "datetime" in str(type(p_bind_values[x])):
                            idx = 2
                        if "LOB" in str(type(p_bind_values[x])):
                            idx = 4 if "BLOB" in str(p_bind_values[x].type) else 3
                        self.cur.execute(f"begin user_exec.pc_exec_dml.pr_bind_var(p_var => :p_var, p_tip => :p_tip, {names[idx]} => :p_valor); end;", (x, idx, p_bind_values[x]) )

                    self.cur.callproc("user_exec.pc_exec_dml.pr_bind_execute", (ret1, ret2))
                else:    
                    self.cur.callproc(dm_const.C_SQL_EXEC, (p_sql, ret1, ret2))

                retorno          = f"{ret1.getvalue()}-{ret2.getvalue()}"
                self.status_code = ret1.getvalue()
                self.status_msg  = retorno

            retorno             = self.cur.var(str)
            self.cur.execute(dm_const.C_SQL_DBMS,retorno=retorno)                
            self.dbms_output    = retorno.getvalue()
            self.in_transaction = True
        except Exception as e:
            self.status_code = -1
            self.status_msg  = str(e)
        self.in_execution = False





    def SELECT(self, p_sql, direct=False, logger=False, fetchSize=None):
        self.prepareVars(p_sql, logger)
        try:
            if direct or self.is_direct:
                self.cur.arraysize = 5000
                self.cur.execute(p_sql)
            else:
                myvar = self.cur.var(oracledb.CURSOR)
                self.cur.callproc(dm_const.C_SQL_SELECT, (p_sql, myvar))
                self.cur    = myvar.getvalue()
            self.col_names     = [  self.cur.description[i][0] for i in range(0, len(self.cur.description))  ]
            self.col_types     = [  str(self.cur.description[i][1]) for i in range(0, len(self.cur.description))  ]

            if fetchSize != None:
                self.col_data = self.cur.fetchall() if fetchSize == 0 else self.cur.fetchmany(fetchSize)

            self.status_code   = 0
            self.status_msg    = "SUCESSO"
        except Exception as e:
            self.status_code = -1
            self.status_msg  = str(e)
        self.in_execution = False



    def DDL(self, owner, type, name):
        self.prepareVars("",False)
        try:
            ddl     = self.cur.var(oracledb.CLOB)
            SQL_DML = (dm_const.C_SQL_DML_DIRECT if self.is_direct else dm_const.C_SQL_DML).replace("<1>", type).replace("<2>",owner).replace("<3>", name)
            self.cur.execute(SQL_DML,ddl=ddl)
            self.status_code = 0
            self.status_msg  = ddl.getvalue().read().replace("CCRREEAATTEE",'CREATE')
        except Exception as e:
            self.status_code = -1
            self.status_msg  = str(e)
        self.in_execution = False



    def EXPLAIN(self, p_sql):
        self.EXECUTE(p_sql='DELETE FROM PLAN_TABLES',direct=True)
        self.EXECUTE(p_sql='EXPLAIN PLAN FOR\n' + p_sql,direct=True)
        self.SELECT(p_sql=dm_const.C_SQL_EXPLAIN,direct=True)


    def EVALPY(self, p_code):
        self.in_execution = True
        codevars = {"db": self.con, 'messageBox': messageBox}
        exec(p_code,codevars)
        self.in_execution = False


## ==============================================================================================
## BLOCO PRINCIPAL DO DATA MODULE
## ==============================================================================================

app           = QApplication(sys.argv)
setDarkMode(app)

all_tables    = []
all_users     = []
db            = ORACLE()

fontSQL       = QFont()
fontSQL.setFamily( "Monospace" if platform.system() == "Linux" else "Courier New")
fontSQL.setPointSize(10)


iconBlue      = QIcon()
iconRed       = QIcon()
iconObject    = QIcon()
iconUser      = QIcon()
iconBlue.addPixmap(QPixmap(":/png/ico/blue.png"), QIcon.Normal, QIcon.Off)       
iconRed.addPixmap(QPixmap(":/png/ico/red.png"), QIcon.Normal, QIcon.Off)       
iconObject.addPixmap(QPixmap(":/png/ico/tree_obj.png"), QIcon.Normal, QIcon.Off)       
iconUser.addPixmap(QPixmap(":/png/ico/tree_usr.png"), QIcon.Normal, QIcon.Off)   

clipboard     = app.clipboard()
f_logon       = f_logon.form()
f_principal   = f_principal.form()
f_editor_form = f_editor_form.form()
f_editor      = f_editor.form()
f_editor_find = f_editor_find.form()

def main():
    try:
        od = configValue(tag="OracleInstantClientDir")
        if len(od) > 1 and os.path.exists(od):
            oracledb.init_oracle_client()#lib_dir=od)    
    except Exception as e:
        print(str(e))

    f_principal.showMaximized()
    ret = app.exec_()

    return ret


