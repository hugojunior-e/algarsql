import oracledb
import os
import re
import sys
import sqlite3
import platform

import principal
import logon
import editor_find
import editor_form
import editor

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from threading import Thread

## ==============================================================================================
##
## ==============================================================================================

def do_filename(filename, path="root"):
    v_path = os.path.dirname(sys.argv[0]) if path == "root" else configValue(tag="output_dir")
    return os.path.join( v_path, filename )


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
## loadFromFile
## ==============================================================================================

def loadFromFile(fileName):
    r      = open(fileName,'r', encoding='utf-8', errors='ignore')
    linhas = r.readlines()
    r.close()
    return linhas 

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
    if Run != None:
        G.clicked.connect(Run)
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
    fileConfig       = do_filename("AlgarSQL.db")
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
    conn             = sqlite3.connect(do_filename("AlgarSQL.db"))
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

def populateGrid(grid: QTableWidget, data , columnNames=None, columnTypes=None, editableColumns="", appending=False):
    row_idx = 0 if appending == False else grid.rowCount()
    
    grid.col_names = columnNames
    grid.col_types = columnTypes

    grid.setRowCount( len(data) + row_idx )
    if appending == False:
        if columnNames != None:
            grid.setColumnCount(len(columnNames))
            for i,x in enumerate(columnNames):
                item  = QTableWidgetItem()
                item.setText(x)
                grid.setHorizontalHeaderItem(i, item) 

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
##
## ==============================================================================================


class HOracle:
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
            r1,r2 = self.connect(db.p_usuario, db.p_senha, db.p_tns, db.is_direct)
            self.status_code = r1
            self.status_msg  = r2
        return self.is_connected

    def connect(self, p_usuario, p_senha, p_tns, p_is_direct):
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
            self.cur.execute(C_SQL_START)

            for r in self.cur.execute("select global_name, banner, Sys_Context('USERENV', 'SID') from global_name, v$version").fetchall():
                self.login_global_name = r[0]
                self.login_banner      = r[1]
                self.login_sid         = r[2]

            self.sql_session = C_SQL_SESSIONS_ORA
            if p_is_direct == False:
                self.executeSQL(p_sql="SELECT OWNER FROM ALL_VIEWS WHERE VIEW_NAME = 'VW_SESSIONS' ORDER BY 1")
                if self.status_code == 0:
                    rr = self.cur.fetchone()
                    self.sql_session = C_SQL_SESSIONS_ALGAR.replace("<TABELA>", rr[0] + ".VW_SESSIONS")

            self.con.autocommit = False
            self.is_connected   = True
            return (0,"OK")
        except Exception as e:
            return (-1,str(e))

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
    
    def executeSQL(self,p_sql, p_Log=False, p_tipo="SELECT", p_bind_values=None, p_many=False):
        self.dbms_output  = ""
        self.col_names    = []
        self.col_data     = []
        self.col_types    = []
        self.in_execution = True
        
        if p_Log and self.last_sql != p_sql:
            configSave(self.login_global_name, p_sql,"SQL_HISTORY")
            self.last_sql = p_sql
        
        try:
            if p_tipo.startswith('EXEC'):
                if "DIRECT" in p_tipo or self.is_direct:
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
                        self.cur.callproc(C_SQL_EXEC, (p_sql, ret1, ret2))

                    retorno          = f"{ret1.getvalue()}-{ret2.getvalue()}"
                    self.status_code = ret1.getvalue()
                    self.status_msg  = retorno

                retorno             = self.cur.var(str)
                self.cur.execute(C_SQL_DBMS,retorno=retorno)                
                self.dbms_output    = retorno.getvalue()
                self.in_transaction = True

            if p_tipo.startswith('SELECT'):
                if "DIRECT" in p_tipo or self.is_direct:
                    self.cur.arraysize = 5000
                    self.cur.execute(p_sql)
                else:
                    myvar = self.cur.var(oracledb.CURSOR)
                    self.cur.callproc(C_SQL_SELECT, (p_sql, myvar))
                    self.cur    = myvar.getvalue()
                self.col_names     = [  self.cur.description[i][0] for i in range(0, len(self.cur.description))  ]
                self.col_types     = [  str(self.cur.description[i][1]) for i in range(0, len(self.cur.description))  ]
                self.status_code   = 0
                self.status_msg    = "SUCESSO"

            if p_tipo == 'DML':
                dados   = p_sql.split("/")
                ddl     = self.cur.var(oracledb.CLOB)
                SQL_DML = (C_SQL_DML_DIRECT if self.is_direct else C_SQL_DML).replace("<1>", dados[1]).replace("<2>",dados[0]).replace("<3>", dados[2])
                self.cur.execute(SQL_DML,ddl=ddl)
                self.status_code = 0
                self.status_msg  = ddl.getvalue().read().replace("CCRREEAATTEE",'CREATE')
        except Exception as e:
            self.status_code = -1
            self.status_msg  = str(e)
        self.in_execution = False


## ==============================================================================================
## SQLHigLigth
## ==============================================================================================

class SyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super(SyntaxHighlighter, self).__init__(parent)

        self.highlightingRules = []
        self._mapping = {}
        is_dm = configValue(tag="EditorSqlDarkMode") == "1"

        stringF = QTextCharFormat()
        stringF.setForeground(Qt.magenta if is_dm else Qt.blue)
        stringPatterns = [ "'([^'']*)'"]

        funcF = QTextCharFormat()
        funcF.setForeground(Qt.cyan)
        funcPatterns = ['REPLACE','TRANSLATE','EXISTS','INSTR','REVERSE','REGEXP_INSTR','REGEXP_REPLACE','REGEXP_SUBSTR','REGEXP_COUNT','ADD_MONTHS','SQLERRM','RETURN','EXIT', 'LPAD','RPAD','TRUNC','TO_DATE','TO_CHAR','TO_NUMBER','NVL','DECODE','SYSDATE', 'COUNT','AVG','SUM','MAX','MIN','CASE','NULL','NVL2','TRIM','SUBSTR','UPPER','LOWER','INITCAP']

        typeF = QTextCharFormat()
        typeF.setForeground(Qt.magenta)
        typePatterns = ['TYPE','PLS_INTEGER','LONG','RAW','NUMBER','VARCHAR','VARCHAR2','CLOB','INTEGER','CHAR','DATE','TIMESTAMP','INT','BLOB']

        reservedF = QTextCharFormat()
        reservedF.setForeground(Qt.yellow if is_dm else QColor(0,128,128))
        reservedPatterns = ['INTO','EXECUTE', 'IMMEDIATE', 'ROWNUM', 'VALUES', 'GROUP','HAVING','ORDER','WITH','AS','UNION','ALL','DESC','ASC',
                            'TO','PUBLIC','GRANT','DROP','ALTER','SET','IS','NOT','DISTINCT','DEFAULT',
                            'BY','SELECT','INSERT','UPDATE','DELETE','FROM', 'WHERE', 'AND', 'TABLESPACE','THEN', 'BEFORE','AFTER','REFERENCING',
                            'LEVEL','CONNECT','COMPILE','PRIOR','SYNONYM','LIKE','SEGMENT','CREATION','EACH', 'ROW',
                            'IN', 'FOR','BREAK','LOOP','BEGIN','DECLARE','EXCEPTION','WHEN','STORAGE','OLD','NEW',
                            'PCTFREE','PCTUSED','INITRANS','MAXTRANS','NOCOMPRESS','LOGGING','ENABLE','DISABLE','OUT',
                            'END','INNER','LEFT','JOIN','ON','CURSOR','ROWTYPE','OTHERS','UNIQUE','INDEX','ROLLBACK',
                            'ELSE',' THEN','IF','ELSIF','CREATE','OR','FORCE','EDITIONABLE','BETWEEN',
                            'VIEW','TABLE','PROCEDURE','PACKAGE','BODY','TRIGGER','FUNCTION','FREELIST',
                            'MODIFY', 'RENAME', 'ADD','COLUMN','GLOBAL','TEMPORARY','COMMIT','PRESERVE','ROWS',
                            'USING','COMPUTE','STATISTICS','BUFFER_POOL','FLASH_CACHE','CELL_FLASH_CACHE',
                            'INITIAL','NEXT','MINEXTENTS','MAXEXTENTS','PCTINCREASE','FREELISTS','GROUPS']


        self.commentF = QTextCharFormat()
        self.commentF.setForeground(Qt.gray)
        self.commentF.setFontItalic(True)
        commentPatterns = [ r'--.*$' ]

        for r in typePatterns:
            self._mapping["\\b" + r + "\\b"] = typeF

        for r in reservedPatterns:
            self._mapping["\\b" + r + "\\b"] = reservedF

        for r in funcPatterns:
            self._mapping["\\b" + r + "\\b"] = funcF

        for r in stringPatterns:
            self._mapping[r] = stringF

        for r in commentPatterns:
            self._mapping[r] = self.commentF

     

    def highlightBlock(self, text_block):
        for pattern, fmt in self._mapping.items():
            for match in re.finditer(pattern,text_block, re.I):
                start,end = match.span()
                self.setFormat(start,end-start,fmt)

        commentStartExpression = QRegExp("/\\*")
        commentEndExpression = QRegExp("\\*/")  
        self.setCurrentBlockState(0)
        startIndex = 0
        if self.previousBlockState() != 1:
            startIndex = commentStartExpression.indexIn(text_block)
        while startIndex >= 0:
            endIndex      = commentEndExpression.indexIn(text_block, startIndex)
            commentLength = 0
            if endIndex == -1:
                self.setCurrentBlockState(1)
                commentLength = len(text_block) - startIndex
            else:
                commentLength = endIndex - startIndex + commentEndExpression.matchedLength()
            self.setFormat(startIndex, commentLength, self.commentF)
            startIndex = commentStartExpression.indexIn(text_block, startIndex + commentLength);            

## ==============================================================================================
## thread
## ==============================================================================================

class Worker(QObject):
    finished = pyqtSignal()
    def init(self, proc_run, proc_fim = None):
        self.thread = QThread()
        self.proc_run = proc_run
        self.moveToThread(self.thread)
        self.finished.connect(self.thread.quit)        
        self.thread.started.connect( self.run )
        if proc_fim != None:
            self.thread.finished.connect(proc_fim) 
        return self
    
    def start(self):
        self.thread.start()

    def run(self):
        self.proc_run()
        self.finished.emit()  

## ==============================================================================================
## Constantes
## ==============================================================================================

C_APP_VERSION         = "AlgarSQL 2.3"
C_SQL_SELECT          = "user_exec.pc_exec_dml.pr_exec_select"
C_SQL_EXEC            = "user_exec.pc_exec_dml.pr_exec_dml"
C_SQL_ALL_TAB_COLUMNS = "SELECT COLUMN_NAME FROM ALL_TAB_COLUMNS WHERE TABLE_NAME = upper('%s') ORDER BY OWNER, COLUMN_ID"
C_SQL_ALL_TABLES      = "SELECT TABLE_NAME FROM ALL_TABLES WHERE OWNER = upper('%s') ORDER BY 1"
C_SQL_PROPERTIES      = "SELECT * FROM ALL_TABLES WHERE TABLE_NAME = '%s' ORDER BY OWNER"
C_SQL_DESCRIBE        = "SELECT column_name, data_type, data_length, nullable, table_name, owner FROM all_tab_columns t where table_name = '%s'  order by owner, t.column_id"
C_SQL_FIND_OBJECT     = "SELECT * FROM ALL_OBJECTS WHERE OBJECT_NAME LIKE upper('%s') AND OBJECT_TYPE IN (%s)"
C_SQL_ALL_ERRORS      = "SELECT ATTRIBUTE, LINE, TEXT  FROM ALL_ERRORS  WHERE OWNER = '%s' AND NAME = '%s'  ORDER BY SEQUENCE"
C_SQL_START           = "begin dbms_output.enable(100000); DBMS_APPLICATION_INFO.SET_CLIENT_INFO('ALGAR SQL'); end;"

C_SQL_DML             = """
begin
  :ddl := user_exec.PC_EXEC_DML.f_get_ddl( '<1>' , '<2>', '<3>') 
            ||  
          case when '<1>'  = 'PACKAGE' then
                '<end_package_spec>' || user_exec.PC_EXEC_DML.f_get_ddl( 'PACKAGE BODY', '<2>', '<3>') 
          end;
end;
"""

C_SQL_DML_DIRECT      = """
declare
  v_type  varchar2(100) := '<1>';
  v_owner varchar2(100) := '<2>';
  v_name  varchar2(100) := '<3>';
  v_ret   clob;
  v_tipo  varchar2(32000);
begin
  dbms_lob.createtemporary(v_ret, true);
  
  if v_type not in ('TABLE', 'VIEW', 'MATERIALIZED VIEW') then
    dbms_lob.append(v_ret, 'CCRREEAATTEE OR REPLACE ');
    for cx in (select case when line = 1 and upper(text) not like '%' || upper(owner) || '.%' then
                             REGEXP_REPLACE(text,name, owner || '.' || name, 1, 0, 'i')
                           else
                             text
                      end text, 
                      line, 
                      type
                 from all_source
                where name = v_name
                  and type like replace(v_type,'PACKAGE','PACKAGE%')
                  and owner = v_owner
                order by type, line)
    loop
      if (cx.line = 1 and cx.type = 'PACKAGE BODY') then
        dbms_lob.append(v_ret, '<end_package_spec>CCRREEAATTEE OR REPLACE ');
      end if;
      dbms_lob.append(v_ret, cx.text);
    end loop;
  end if;

  if v_type = 'TABLE' then
    dbms_lob.append(v_ret, 'CCRREEAATTEE TABLE ' || v_owner || '.' || v_name || '(' || chr(10));
    for cx in (
                SELECT '  '
                       || RPAD(COLUMN_NAME,40,' ') || DATA_TYPE 
                       || (
                            CASE WHEN DATA_TYPE NOT IN ('DATE','CLOB','BLOB') THEN
                            '(' || DATA_LENGTH || nvl2(data_precision, ',' || data_precision, '') || ')'
                            END
                          ) 
                       ||' ' || (CASE WHEN NULLABLE = 'N' THEN 'NOT NULL' END)   text,
                       DATA_DEFAULT,
                       case when COLUMN_ID = (max(COLUMN_ID) over()) then '' else ',' end fim
                  FROM ALL_TAB_COLUMNS
                 WHERE OWNER = v_owner
                   AND TABLE_NAME = v_name
                ORDER BY COLUMN_ID               
              )
    loop
      v_tipo := CX.DATA_DEFAULT;
      if v_tipo is not null then
        v_tipo := ' DEFAULT ' || trim(v_tipo);
      end if;

      dbms_lob.append(v_ret, cx.text || v_tipo || cx.fim || chr(10));
    end loop;
    dbms_lob.append(v_ret, ');' || chr(10));
  
    FOR cx IN (SELECT index_name,
                      RTRIM(XMLAGG(XMLELEMENT(e, column_name || ',') ORDER BY column_position).EXTRACT('//text()'), ',') campos
                 FROM all_ind_columns t
                WHERE table_name = v_name
                  AND table_owner = v_owner
                GROUP BY index_name)
    LOOP
      SELECT UNIQUENESS
        INTO v_tipo
        FROM ALL_INDEXES
       WHERE OWNER = v_owner
         AND INDEX_NAME = CX.INDEX_NAME;
    
      dbms_lob.append(v_ret,'CCRREEAATTEE ' || (CASE WHEN v_tipo = 'UNIQUE' THEN v_tIpo END) || ' INDEX ' || v_owner || '.' || cx.index_name || ' ON ' || v_owner || '.' || v_name || '(' || cx.campos || ');' || CHR(10));
    END LOOP;
  
  end if;

  if v_type like '%VIEW%' then
    SELECT A INTO V_TIPO FROM
    (
            SELECT TEXT A FROM ALL_VIEWS WHERE OWNER = v_owner AND VIEW_NAME = v_name
            UNION ALL
            SELECT QUERY A FROM ALL_MVIEWS WHERE OWNER = v_owner AND MVIEW_NAME = v_name
    );        
  
    dbms_lob.append(v_ret, 'CCRREEAATTEE OR REPLACE ' || v_type || ' ' || v_owner || '.' || v_name || ' AS ' || chr(10));
    dbms_lob.append(v_ret, V_TIPO);
  end if;
  :ddl := v_ret;
end;
"""

C_SQL_TREE = """
    SELECT OWNER,         
        OBJECT_TYPE,   
        OBJECT_NAME,
        STATUS  
    FROM ALL_OBJECTS    
    WHERE OBJECT_TYPE IN ('PROCEDURE', 'TABLE', 'VIEW', 'FUNCTION', 'TRIGGER', 'MATERIALIZED VIEW', 'PACKAGE', 'TRIGGER')
    AND OWNER not in ( 'SYSTEM', 'SYS',
            'ORDDATA', 'FLOWS_FILES', 'APEX_030200', 'APEX_040200', 'APEX_PUBLIC_USER', 'OLAPSYS', 'QUEST', 'OUTLN', 'RMAN', 'XDB', 'C##CLOUD$SERVICE', 'ANONYMOUS',
            'APPQOSSYS', 'AUDSYS', 'CTXSYS', 'DBSFWUSER', 'DBSNMP', 'DIP', 'DMSYS', 'DVF', 'DVSYS', 'DUMMY', 'EXFSYS', 'GGSYS', 'GSMADMIN_INTERNAL', 'GSMCATUSER', 'GSMUSER', 'LBACSYS',
            'MDDATA', 'MDSYS', 'MGMT_VIEW', 'OJVMSYS', 'OLAPSYS', 'ORACLE_OCM', 'ORDDATA', 'ORDPLUGINS', 'ORDSYS', 'OUTLN', 'REMOTE_SCHEDULER_AGENT', 'SI_INFORMTN_SCHEMA', 'SCOTT',
            'SYS$UMF', 'SYSBACKUP', 'SYSDG', 'SYSKM', 'SYSMAN', 'SYSRAC', 'TSMSYS', 'WMSYS', 'XDB', 'XS$NULL', 'OWBSYSOWBSYS_AUDIT', 'SPATIAL_WFS_ADMIN_USR', 'SPATIAL_CSW_ADMIN_USR',
            'OWBSYS', 'OWBSYS_AUDIT', 'SPATIAL_WFS_ADMIN_USR', 'SPATIAL_CSW_ADMIN_USR')
    order by OWNER,OBJECT_TYPE,OBJECT_NAME
"""


C_SQL_RECOMPILE = """
    SELECT owner || '.' || object_name || '(' || object_type  || ')' obj,
           'ALTER ' 
           || DECODE(object_type,'PACKAGE BODY','PACKAGE', object_type) 
           || ' ' 
           || owner 
           || '.' || object_name 
           || ' COMPILE ' 
           || DECODE(object_type,'PACKAGE BODY','BODY', '') cmd
    FROM all_objects
    WHERE status != 'VALID'
    ORDER BY DECODE(object_type,'PACKAGE',1,'PACKAGE BODY',2,2)
"""

C_SQL_SESSIONS_ALGAR = """
    SELECT  USERNAME || '(' || count(1) over (partition by username order by 1) || ')' username,
            STATUS|| '(' || count(1) over (partition by username, status order by 1) || ')' status,
            SID,
            SERIAL#,
            LOGON_TIME,
            OSUSER,
            MACHINE,
            PROGRAM,
            SQL_ID,
            CLIENT_INFO,
            SQL_FULLTEXT
    FROM <TABELA> 
   WHERE STATUS LIKE '<WHERE>'
ORDER BY USERNAME, STATUS, LOGON_TIME    
"""

C_SQL_SESSIONS_ORA = """
SELECT x.username || '(' || count(1) over (partition by x.username order by 1) || ')' username,
       x.STATUS|| '(' || count(1) over (partition by x.username, x.status order by 1) || ')' status,
       x.sid,
       x.serial#,
       x.logon_time,
       x.osuser,
       x.machine,
       x.program,
       x.sql_id,
       x.client_info,
       sql_fulltext
FROM   sys.v_$sqlarea sqlarea, sys.v_$session x
WHERE  x.sql_hash_value = sqlarea.hash_value(+)
   and x.sql_address = sqlarea.address(+)
   and x.username is not null
   AND x.status LIKE '<WHERE>'
ORDER BY x.username, x.status, X.LOGON_TIME    
"""

C_SQL_EXPLAIN = """
  select id,
         nvl(parent_id, -1) parent_id,
         operation || ' ' || decode(id, 0, optimizer, options),
         object_owner,
         object_name,
         object_type,
         to_char(cost),
         to_char(cardinality),
         to_char(bytes)
    from plan_table
   order by id
"""

C_SQL_DBMS = """
    declare                                                   
        l_data_qtd NUMBER          := 32000;                                      
        p_ret      varchar2(32000) := '';  
        lines      DBMS_OUTPUT.CHARARR;                   
    BEGIN                                                     
        DBMS_OUTPUT.get_lines(lines, l_data_qtd);  
        FOR x IN lines.FIRST .. lines.LAST
        LOOP
          p_ret := p_ret || lines(x) || chr(10);
        END LOOP;         
        :retorno := p_ret;                                      
    END;
"""

## ==============================================================================================
## variaveis globais
## ==============================================================================================

app           = QApplication(sys.argv)
setDarkMode(app)
fontSQL       = QFont()
fontSQL.setFamily( "Monospace" if platform.system() == "Linux" else "Courier New")
fontSQL.setPointSize(10)

all_tables    = []
all_users     = []
db            = HOracle()

iconBlue      = QIcon()
iconRed       = QIcon()
iconObject    = QIcon()
iconUser      = QIcon()
iconBlue.addPixmap(QPixmap(":/png/ico/blue.png"), QIcon.Normal, QIcon.Off)       
iconRed.addPixmap(QPixmap(":/png/ico/red.png"), QIcon.Normal, QIcon.Off)       
iconObject.addPixmap(QPixmap(":/png/ico/tree_obj.png"), QIcon.Normal, QIcon.Off)       
iconUser.addPixmap(QPixmap(":/png/ico/tree_usr.png"), QIcon.Normal, QIcon.Off)   

clipboard     = app.clipboard()
f_logon       = logon.form()
f_principal   = principal.form()
f_editor_form = editor_form.form()
f_editor      = editor.form()
f_editor_find = editor_find.form()

def main():
    try:
        od = configValue(tag="OracleInstantClientDir")
        if len(od) > 1 and os.path.exists(od):
            oracledb.init_oracle_client(lib_dir=od)    
    except Exception as e:
        print(str(e))

    f_principal.showMaximized()
    ret = app.exec_()

    return ret


