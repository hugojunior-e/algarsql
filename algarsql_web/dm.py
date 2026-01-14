import oracledb
import os
import sys
import sqlite3
import re
import dm_const
from threading import Thread

## ==============================================================================================
## operacoes com arquivos
## ==============================================================================================

def generateFileName(filename, inOutputDir=False):
    v_path = configValue(tag="output_dir") if inOutputDir else os.path.dirname(sys.argv[0])
    return os.path.join(v_path, filename)

## ==============================================================================================
## Configurações SQLite
## ==============================================================================================

def configOracleHome():
    oracledb.init_oracle_client()

def configValue(tag=None, params=["%", "%"]):
    fileConfig = sys.argv[0].replace('__main__.py','AlgarSQL') + ".db"
    if not os.path.exists(fileConfig):
        return ""
    conn = sqlite3.connect(fileConfig)
    cursor = conn.cursor()
    ret = None
    if tag == "*recall":
        ret = cursor.execute(
            f"select * from sql_history where info like '{params[0]}' and dbname like '{params[1]}' order by 1 desc").fetchall()
    else:
        reg = cursor.execute(f"select info from config where node = '{tag}'").fetchall()
        ret = "" if len(reg) == 0 else reg[0][0]
    conn.close()
    return ret


def configSave(tagName, tagValue, p_tipo):
    fileConfig = sys.argv[0].replace('__main__.py','AlgarSQL') + ".db"
    conn = sqlite3.connect( fileConfig )
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE if not exists config (node VARCHAR(11), info text)")
    cursor.execute("CREATE TABLE if not exists sql_history (dt datetime default current_timestamp, dbname varchar(50), info text)")
    if p_tipo == "CONFIG":
        cursor.execute(f"delete from config where node = '{tagName}'")
        cursor.execute("insert into config (node,info) values (?,?)", (tagName, tagValue))
    if p_tipo == "SQL_HISTORY":
        cursor.execute("insert into sql_history (dbname,info) values (?,?)", (tagName, tagValue))
    conn.commit()
    conn.close()


def tipoSQL(SQL, checkCreateObj=False):
    x = SQL.upper() + "\n"
    x = re.sub(r"--.*", "", x)
    x = re.sub(r"/\*.*?\*/", "", x, flags=re.S)
    if checkCreateObj:
        if x.strip().startswith('CREATE'):
            x = x.replace("\n", " ").replace(" BODY ", " ").replace("(", " ").replace('"', "")
            while "  " in x:
                x = x.replace("  ", " ")
            b = ""
            d = x.split(" ")
            for i, dd in enumerate(d):
                if dd in ["PROCEDURE", "TABLE", "TRIGGER", "VIEW", "PACKAGE", "FUNCTION"]:
                    b = d[i + 1].strip()
                    break
            return 3, b
        else:
            return -3, None
    if x.strip().startswith('SELECT') or x.strip().startswith('WITH'):
        return 1
    return 2


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
        self.col_names      = []
        self.col_types      = []


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
            self.CONNECT(p_usuario=self.p_usuario, p_senha=self.p_senha, p_tns=self.p_tns, p_is_direct=self.is_direct)
    
    def __connect(self):
        try:
            self.con = oracledb.connect( user=self.p_usuario, password=self.p_senha, dsn=self.p_tns )
        except Exception as e:
            self.status_code = -1
            self.status_msg  = str(e)

    def CONNECT(self, p_usuario, p_senha, p_tns, p_is_direct):
        self.in_transaction = False
        self.in_execution   = False
        self.is_connected   = False
        self.is_direct      = p_is_direct
        self.login_sid      = 0
        self.status_code    = 0
        self.status_msg     = 'OK'
        
        try:
            if p_usuario == None or p_senha == None or p_tns == None:
                raise ValueError("Parameter User/Pass Invalid!")
            
            self.p_usuario    = p_usuario
            self.p_senha      = p_senha
            self.p_tns        = p_tns

            t1 = Thread(target=self.__connect)
            t1.start()
            t1.join(30)
            if t1.is_alive():
                raise ValueError("Timeout Connection Required...")
            if self.status_code != 0:
                raise ValueError(self.status_msg)
            
            self.cur          = self.con.cursor()
            self.cur.execute(dm_const.C_SQL_START)

            

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
        except Exception as e:
            self.status_code = -1
            self.status_msg  = str(e)



    def disconnect(self):
        if self.con != None:
            t1 = Thread(target=lambda: self.con.close())
            t1.start()
            t1.join(3)
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
        self.prepare()
        self.dbms_output  = ""
        self.col_names    = []
        self.col_types    = []
        self.col_data     = []        
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
                self.status_msg    = f"SUCESSO - {self.cur.rowcount} rows"
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
                
            for i in range(0, len(self.cur.description)):    
                self.col_names.append( self.cur.description[i][0])
                self.col_types.append(re.sub(r"^DB_TYPE_", "", self.cur.description[i][1].name))

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
        self.EXECUTE(p_sql='DELETE FROM PLAN_TABLE',direct=True)
        self.EXECUTE(p_sql='EXPLAIN PLAN FOR\n' + p_sql,direct=True)
        self.SELECT(p_sql=dm_const.C_SQL_EXPLAIN,direct=True,fetchSize=0)
        return "\n".join( [ x[0] for x in self.col_data] )