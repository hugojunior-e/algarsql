import datetime

import oracledb
oracledb.init_oracle_client(lib_dir="/opt/instantclient_21_12")

import os
import sys
import sqlite3
import re
import dm_const
import datetime
import json

from threading import Thread


WORKDIR = "/algarsql"


## ==============================================================================================
## alteração de senha
## ==============================================================================================

FARMPRD_USR = "deployapp"
FARMPRD_PWD = "P7RT6L#A5TI4B"
FARMPRD_DSN = 'exa07-scan-prd.network.ctbc:1521/FARMPRD'


def change_password_get_user(alias, username):
    con_farm = oracledb.connect(dsn=FARMPRD_DSN, user=FARMPRD_USR, password=FARMPRD_PWD)
    cur      = con_farm.cursor()

    dados = cur.execute( f" select TNS_NAMES from deployadm.T_CFG_BASE tcb WHERE  upper(tcb.NAME) = upper('{alias}') ").fetchone()

    if dados:
        tns = dados[0]
    else:
        return "ERROR: Database entry not found.",None
  
    dados = cur.execute( f"""
          SELECT * FROM
          (
                  SELECT --+ parallel
                      distinct SUBSTR(tb_recurso.name,18) data_base, tb_conta.accountIdentifier
                  FROM blazonadm.MembershipEntitlement tb_membrododireito
                  INNER JOIN blazonadm.Account tb_conta                             ON tb_membrododireito.account_id = tb_conta.id
                  INNER JOIN blazonadm.b_Resource tb_recurso                          ON tb_conta.resource_id = tb_recurso.id
                  INNER JOIN blazonadm.B_USER tb_user                          ON tb_user.id = tb_conta.user_id
                  WHERE 1 = 1
                  AND upper(tb_recurso.name) LIKE '%BANCO DE DADOS%PRD' -- NOME DO RECURSO
                  and upper( tb_user.USERNAME ) = upper('{username}')  --entre aq com o usuario de rede ( logado no app algarsql )

                  UNION

                  SELECT --+ parallel
                  'CMPRD' data_base, tb_conta.accountIdentifier
                  FROM blazonadm.MembershipEntitlement tb_membrododireito
                  INNER JOIN blazonadm.Account tb_conta                             ON tb_membrododireito.account_id = tb_conta.id
                  INNER JOIN blazonadm.b_Resource tb_recurso                          ON tb_conta.resource_id = tb_recurso.id
                  INNER JOIN blazonadm.B_USER tb_user                          ON tb_user.id = tb_conta.user_id
                  WHERE 1 = 1
                  AND upper(tb_recurso.name) = 'CONNECT MASTER' -- NOME DO RECURSO
                  and upper( tb_user.USERNAME ) = upper('{username}') --entre aq com o usuario de rede ( logado no app algarsql )
                  
          )
          WHERE DATA_BASE IN (
                  select NAME
                  from deployadm.T_CFG_BASE tcb
                  START WITH tcb.NAME = '{alias}'  --ENTRE AQ COM A BASE QUE QUER TROCAR A SENHA
                  CONNECT BY PRIOR ID = BASE_DEP_ID
          )
    """).fetchone()

    userNameFound = None

    if dados:
        userNameFound = dados[1]
    else:
        return "ERROR: User not found.",None
    
    try:
        con_db = oracledb.connect(dsn=tns, user=FARMPRD_USR, password=FARMPRD_PWD)
        cur_db = con_db.cursor()

        cur_db.execute(f"""select count(1) from all_users where username = upper('{userNameFound}')""")
        user_exists = cur_db.fetchone()[0]
        if user_exists == 0:
            return f"ERROR: User {userNameFound} does not exist in database {alias}.",None
        
        return userNameFound, tns
    except oracledb.DatabaseError as e:
        error, = e.args
        return f"ERROR: Database error: {error.message}",None


def change_password(db_tns, db_user, db_password):
  try:
      con_db = oracledb.connect(dsn=db_tns, user=FARMPRD_USR, password=FARMPRD_PWD)
      cur_db = con_db.cursor()
      
      cur_db.execute(f"""
                DECLARE
                  P_Nm_Usuario    VARCHAR2(128)  := '{db_user}';
                  P_Senha_Usuario VARCHAR2(4000) := '{db_password}';
                  P_Msg_Retorno   VARCHAR2(2048) := 'SUCESSO';
                  v_user_banco    VARCHAR2(128);
                  v_qtd           number;
                BEGIN
                    PKG_RESET_SENHA_USUARIO.PRO_RESET_SENHA ( upper(P_Nm_Usuario) , P_Senha_Usuario , P_Msg_Retorno );

                    if (P_Msg_Retorno LIKE '%ERRO%') then
                        raise_application_error(-20003, P_Msg_Retorno );
                    end if;

                    -- DESBLOQUEANDO USUARIO
                    PKG_RESET_SENHA_USUARIO.PRO_UNLOCK_USUARIO (upper(v_user_banco), P_Msg_Retorno );


                    if (P_Msg_Retorno LIKE '%ERRO%') then
                        raise_application_error(-20004, P_Msg_Retorno );
                    end if;
                END;                     
      """)

  except oracledb.DatabaseError as e:
      error, = e.args
      return f"Database error: {error.message}"
  
  return f"Success Change Password for user {db_user}"


## ==============================================================================================
## operacoes com arquivos
## ==============================================================================================

def generateFileName(filename, temp=False):
    agora = datetime.datetime.now()
    w     = os.path.join( WORKDIR ,"workspace" ) 
    t     = os.path.join( WORKDIR ,"workspace", "temp" )
    f     = filename.replace("[]",agora.strftime("%Y%m%d_%H%M%S_%f"))

    os.makedirs( w , exist_ok=True)
    os.makedirs( t , exist_ok=True)

    return os.path.join( w if not temp else t, f ) 


## ==============================================================================================
## Configurações SQLite
## ==============================================================================================

def configOracleHome():
    oh = os.environ.get("ORACLE_HOME", "")
    oracledb.init_oracle_client(lib_dir=oh)

def configValue(tag=None, params=["%", "%"], username=""):
    fileConfig = generateFileName( username + ".db" )
    if not os.path.exists(fileConfig):
        return ""
    conn = sqlite3.connect(fileConfig)
    cursor = conn.cursor()
    ret = None
    if tag == "SQL_HISTORY":
        ret = cursor.execute( f"select * from sql_history where info like '{params[0]}' and dbname like '{params[1]}' order by 1 desc").fetchall()
        
    elif tag == "SQL_TEMPLATES":
        ret = cursor.execute( f"select * from sql_templates where node like '{params[0]}' order by node").fetchall()

    else:
        reg = cursor.execute(f"select info from config where node = '{tag}'").fetchall()
        ret = "" if len(reg) == 0 else reg[0][0]
    conn.close()
    return ret


def configSave(tagName, tagValue, p_tipo, username=""):
    fileConfig = generateFileName( username + ".db" )
    conn = sqlite3.connect( fileConfig )
    cursor = conn.cursor()
    
    cursor.execute("CREATE TABLE if not exists config (node text, info text)")
    cursor.execute("CREATE TABLE if not exists sql_history (dt datetime default current_timestamp, dbname text, info text)")
    cursor.execute("CREATE TABLE if not exists sql_templates (node text unique, info text)")

    if p_tipo == "CONFIG":
        cursor.execute(f"delete from config where node = '{tagName}'")
        cursor.execute("insert into config (node,info) values (?,?)", (tagName, tagValue))

    if p_tipo == "SQL_HISTORY":
        cursor.execute("insert into sql_history (dbname,info) values (?,?)", (tagName, tagValue))

    if p_tipo == "SQL_TEMPLATES":
        cursor.execute(f"delete from sql_templates where node = '{tagName}'")
        cursor.execute("insert into sql_templates (node,info) values (?,?)", (tagValue['node'], tagValue['info']))

    conn.commit()
    conn.close()


def tipoSQL(SQL):
    x = SQL.upper() + "\n"
    x = re.sub(r"--.*", "", x)
    x = re.sub(r"/\*.*?\*/", "", x, flags=re.S)
    if x.strip().startswith('CREATE'):
        pattern = re.compile(
            r'''
            CREATE\s+
            (?:OR\s+REPLACE\s+)? 
            (?:EDITIONABLE\s+|NONEDITIONABLE\s+)? 
            
            (?P<tipo>PACKAGE\s+BODY|PACKAGE|FUNCTION|PROCEDURE|SEQUENCE|VIEW)
            \s+
            
            (?:
                "?(?P<schema>[^\s".]+)"?\.
            )?
            
            "?(?P<objeto>[^\s"(]+)"?
            ''',
            re.IGNORECASE | re.VERBOSE | re.DOTALL
        )

        match = pattern.search(SQL)
        obj   = None
        if match:
            obj = {
                "object_type"  : match.group(1).upper(),
                "object_owner" : match.group("schema"),
                "object_name"  : match.group("objeto")
            }        
        return 3, obj
    if x.strip().startswith('SELECT') or x.strip().startswith('WITH'):
        return 1,None
    return 2,None


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
        self.username       = ""


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
            configSave(self.login_global_name, p_sql,"SQL_HISTORY", username=self.username)
            self.last_sql = p_sql            

    def get_line_column(self, sql, offset):
        lines = sql.splitlines(True)  # mantém \n
        current = 0

        for i, line in enumerate(lines, start=1):
            if current + len(line) >= offset:
                column = offset - current
                return i, column
            current += len(line)

        return None, None

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
            if self.cur.connection:
                self.cur.close()
                self.cur = self.con.cursor()

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
        except oracledb.DatabaseError as e:
            error_obj,       = e.args
            line, col        = self.get_line_column(p_sql, error_obj.offset)
            self.status_code = -1
            self.status_msg  = str(e) + "\n" + f"Error at line {line}, column {col}"
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


    def PROCEDURE(self, obj):
        dat            = obj.strip().upper().split(".")
        v_name         = "%"
        v_owner        = "%"
        v_package      = "-"
        v_obj_owner    = ""
        

        if len(dat) == 1:
            v_name  = dat[0]
        if len(dat) == 2:
            v_owner = dat[0]
            v_name  = dat[1]
        if len(dat) > 2:
            v_owner   = dat[0]
            v_package = dat[1]
            v_name    = dat[2]
        sql = dm_const.C_SQL_PROCEDURE_ARGS % ( v_owner , v_name , v_package )

        v_obj_name    = v_name if v_package == "-" else f"{v_package}.{v_name}"

        self.SELECT(p_sql=sql, fetchSize=0)

        decls  = []
        params = []
        prints = []
        rcur   = ""

        for arg_name, pos, data_type, in_out, v_obj_owner in self.col_data:

            v = f"v_{ arg_name.lower() }"
            t = ""

            if data_type in ("VARCHAR2","CHAR"):
                t = f"{data_type}(1000) := 'TESTE';"
            elif data_type == "NUMBER":
                t = f"{data_type} := 0;"
            elif data_type == "DATE":
                t = f"{data_type} := SYSDATE;"
            elif "CURSOR" in data_type:
                t = "SYS_REFCURSOR;"
                rcur = "\n\n" + dm_const.C_SQL_PROCEDURE_REFCURSOR + "\n"
            else:
                t = f"{data_type};"

            decls.append(f"{ v.ljust(40) } {t}")
            params.append(f"{arg_name} => {v}")
            if "OUT" in in_out:
                if t == "SYS_REFCURSOR;":
                    prints.append(f"print_refcursor({v});")
                else:
                    prints.append(f"DBMS_OUTPUT.PUT_LINE('{arg_name}=' || {v});")

        decl_block = "\n".join( [ f"  {x}" for x in decls])
        param_block = ",\n".join( [ f"    {x}" for x in params])
        print_block = "\n".join( [ f"  {x}" for x in prints])

        plsql = f"DECLARE\n{decl_block}{rcur}\nBEGIN\n  {v_obj_owner}.{v_obj_name}\n  (\n{param_block}\n  );\n{print_block}\nEND;"
        return plsql
    


    def EXPLAIN(self, p_sql):
        self.EXECUTE(p_sql='DELETE FROM PLAN_TABLE',direct=True)
        self.EXECUTE(p_sql='EXPLAIN PLAN FOR\n' + p_sql,direct=True)
        self.SELECT(p_sql=dm_const.C_SQL_EXPLAIN,direct=True,fetchSize=0)
        return "\n".join( [ x[0] for x in self.col_data] )