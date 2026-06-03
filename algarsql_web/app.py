import dm

import os
import threading
import zipfile
import sys

import csv
import re
import json
import dm_const
import datetime
from uuid import uuid4
from flask import Flask, redirect, render_template, request, send_file, session
from html import escape
from openpyxl import Workbook
from ldap3 import Server, Connection, ALL, core, SUBTREE


app                  = Flask(__name__)
app.secret_key       = 'algarsql_algar_2026_asdfg_zxcvb_qwerty'

dm.WORKDIR           = app.root_path

db_list              = {}
global_th_ret        = ""
global_th_stop       = False


#@app.before_request
#def before_requests():

#######################################################################################
#  autenticacao ldap
#######################################################################################

def ldap_get_groups(ad_servidor, usuario_dn, senha):
    servidor = Server(ad_servidor, get_info=ALL)
    conexao = Connection(
        servidor,
        user=usuario_dn,
        password=senha,
        authentication='SIMPLE',
        auto_bind=True
    )
    conexao.search(
        search_base=usuario_dn,
        search_filter='(objectClass=person)',
        search_scope=SUBTREE,
        attributes=['memberOf']
    )
    grupos = []
    if conexao.entries:
        entry = conexao.entries[0]
        if 'memberOf' in entry:
            grupos = entry.memberOf.values
    conexao.unbind()
    return grupos

def ldap_check(ad_servidor, usuario_dn, senha):
    try:
        servidor = Server(ad_servidor, get_info=ALL)
        conexao = Connection(
            servidor,
            user=usuario_dn, 
            password=senha,
            authentication='SIMPLE',
            auto_bind=True
        )
        conexao.unbind()
        return True
    except core.exceptions.LDAPBindError as e:
        return False

def ldap_login(username, password):
    ad_servidor = "10.51.47.125"
    for domains in ["associado","terceiro","temporario","estagiario"]:
        user_dn = f"CN={username},ou={domains},cn=Users,dc=network,dc=ctbc"
        if ldap_check(ad_servidor=ad_servidor, usuario_dn=user_dn, senha=password):
            #grupos = ldap_get_groups(ad_servidor, user_dn, password)
            return True
    return False


#######################################################################################
#
#######################################################################################


def _html_table(headers, rows):
    html = "<table>"
    html += "<tr>" + "".join(f"<th>{escape(str(h))}</th>" for h in headers) + "</tr>"

    for row in rows:
        html += "<tr>" + "".join(
            f"<td>{escape(str(col))}</td>" for col in row
        ) + "</tr>"

    html += "</table>"
    return html


def to_table_div(dados, titulos):
    html = []
    html.append('<div class="table-detail-div">')

    # Header
    for titulo in titulos:
        html.append(f'  <div class="cell label">{titulo}</div>')

    # Linhas de dados
    for linha in dados:
        for coluna in linha:
            html.append(f'  <div class="cell">{coluna}</div>')

    html.append('</div>')

    return "\n".join(html)



def get_code_in_zip():
    x          = zipfile.ZipFile(sys.argv[0], "r")
    index_html = x.read("templates/index.html").decode("utf-8")
    style_css  = x.read("static/style-dark.css").decode("utf-8")
    tree_js    = x.read("static/tree.js").decode("utf-8") 
    funcs_js   = x.read("static/funcs.js").decode("utf-8") 

    return index_html.replace("INLINE_START-->","").replace("<!--INLINE_END","").replace("<!--INLINE-->", f"<style>{ style_css }</style> <script>{ tree_js }</script> <script>{ funcs_js }</script>")




def row_to_dict(colunas, linha, tipos):
    r = {}
    for col, val in zip(colunas, linha):
        col_tipo = tipos[ colunas.index(col) ]

        if val is not None:
            if "LOB" in col_tipo:
                if "BLOB" in col_tipo:
                    val = val.read().decode("utf-8", errors='replace')
                else:
                    val = val.read()        
            elif "DATE" in col_tipo:
                val = val.strftime("%d/%m/%Y %H:%M:%S")                        
            elif "RAW" in col_tipo:
                val = str(val)
        r[col] = "" if val is None else val
    return r




def db_objects_view(db):
    ret    = ""
    tables = []
    users  = []

    db.SELECT( p_sql=dm_const.C_SQL_TREE )
    object_list = db.cur.fetchall()
    for x in object_list:
        ret = ret + x[0] + "\n"
        users.append(x[0].split("|")[0]) 
        if "|TABLE|" in x[0] or "|VIEW|" in x[0]:
            table_name = x[0].split("|")[2]
            tables.append( table_name )

    return ret, tables, sorted(set(users))



def exportToFile(db, sql, file_type, table_name):
    global global_th_ret
    global global_th_stop

    global_th_ret = "Exporting..."
    try:
        l_filenames = ["exported_to_insert.sql", "exported.csv", "exported.xlsx"]

        db.SELECT(p_sql=sql)

        if db.status_code != 0:
            return f"Error: { db.status_msg }"

        file_path = dm.generateFileName( "[]-" + l_filenames[file_type], temp=True)
        qtd = 0

        # ---------------------------------------
        # INSERT SCRIPT
        # ---------------------------------------
        if file_type == 0:
            with open(file=file_path, mode="w", encoding="utf-8") as f_file:
                s_insert_title = f"""insert into {table_name} ({",".join(db.col_names)}) """

                for data in iter(lambda: db.cur.fetchmany(5000), []):
                    qtd += len(data)
                    global_th_ret = f"Records: {qtd}"
                    for r in data:
                        f_file.write(
                            f"""{s_insert_title} values ({",".join([db.value(xx) for xx in r])});\n"""
                        )

        # ---------------------------------------
        # CSV
        # ---------------------------------------
        elif file_type == 1:
            with open(file=file_path, mode="w", encoding="utf-8", newline="") as f_file:
                arq = csv.writer(
                    f_file,
                    delimiter=";",
                    quotechar='"',
                    escapechar="\\",
                    quoting=csv.QUOTE_ALL,
                )

                arq.writerow(db.col_names)

                for data in iter(lambda: db.cur.fetchmany(5000), []):
                    qtd += len(data)
                    global_th_ret = f"Records: {qtd}"
                    arq.writerows(data)

        # ---------------------------------------
        # EXCEL (XLSX)
        # ---------------------------------------
        elif file_type == 2:
            wb = Workbook(write_only=True)
            ws = wb.create_sheet(title="Export")

            # Cabeçalho
            ws.append(db.col_names)

            for data in iter(lambda: db.cur.fetchmany(5000), []):
                qtd += len(data)
                global_th_ret = f"Records: {qtd}"
                for row in data:
                    ws.append(row)

            wb.save(file_path)

        global_th_ret  = f"""<a style="cursor: pointer;" onclick="js_download('{ os.path.basename(file_path) }')"> download file </a>"""
        global_th_stop = True
    except Exception as e:
        global_th_ret  = f"Error: {str(e)}"    
        global_th_stop = True


def describeObject(db, object_name):
    ret = ""

    # === Columns ===
    sql = dm_const.C_SQL_TABLE_DESCRIBE_COLS % object_name
    db.SELECT(p_sql=sql)

    if db.status_code == 0:
        data = db.cur.fetchall()
        ret += "<h3>Table Columns</h3>"
        ret += _html_table(db.col_names, data)

    # === Indexes ===
    sql = dm_const.C_SQL_TABLE_INDEXES % object_name
    db.SELECT(p_sql=sql)

    if db.status_code == 0:
        data = db.cur.fetchall()
        ret += "<h3>Table Index</h3>"
        ret += _html_table(db.col_names, data)


    # === Properties ===
    sql = dm_const.C_SQL_TABLE_DESCRIBE_PROP % object_name
    db.SELECT(p_sql=sql)

    if db.status_code == 0:
        data = db.cur.fetchall()
        rows = [
            (db.col_names[idx], value)
            for row in data
            for idx, value in enumerate(row)
        ]
        ret += "<h3>Table Properties</h3>"
        ret += _html_table(["Property", "Value"], rows)
    return ret    


def executeUpdateFromForm(db, rowid, sql, items):
    sql_bind_vars = {}
    for x in items:
        fn = x
        if fn.startswith("@") == False:
            fv = items[x]
            ft = items['@' + x]

            if len(fv) == 0:
                sql_bind_vars[fn] = None
            elif "DATE" in ft:
                sql_bind_vars[fn] = datetime.datetime.strptime(fv, '%d/%m/%Y %H:%M:%S')
            elif "LOB" in ft:
                sql_bind_vars[fn] = db.create_lob(fv, "BLOB" in ft)
            else:
                sql_bind_vars[fn] = fv

    SQL_UPDATE_AUX = (
        "UPDATE (" + sql + ") SET " +
        ",".join([x + " = :" + x for x in sql_bind_vars.keys()]) +
        " WHERE ROWID='" + rowid + "'"
    )

    db.EXECUTE(p_sql=SQL_UPDATE_AUX, p_bind_values=sql_bind_vars)



def csvCompleter(db, sql, first_line_titles,file):
    global global_th_ret
    global global_th_stop
    
    lines             = file.read().decode("utf-8").splitlines()
    f_saved_download  = "[]-" + file.filename + ".completed"
    fsaved            = dm.generateFileName(f_saved_download, temp=True)
    
    try:
        fp2   = open(fsaved,"w", encoding="utf-8")
        for idx, x in enumerate(lines):
            if first_line_titles and idx == 0:
                continue
            
            global_th_ret = f"Processing line {idx+1} of {len(lines)}"
            
            if global_th_stop:
                fp2.close()
                global_th_ret = "Process stopped by user."
                return
            
            records = x.split(";")
            sql_aux = sql
            for idx, f in enumerate(records):
                sql_aux = sql_aux.replace(f"<{idx}>", f.strip())

            db.SELECT( p_sql=sql_aux , logger=True)  

            if db.status_code == 0:
                dados_brutos  = db.cur.fetchone()
                if dados_brutos is None:
                    fp2.write( x.strip() + "\n"  )
                else:
                    fp2.write( x.strip() + ";" +  ";".join(["" if x2 is None else str(x2) for x2 in dados_brutos]) + "\n"  )
            else:
                global_th_stop = True
                global_th_ret  = f"Error: { db.status_msg }"
                return
            
        fp2.close()
        global_th_stop = True
        global_th_ret  = f"""<a style="cursor: pointer;" onclick="js_download('{ os.path.basename(fsaved)  }')"> download file </a>"""

    except Exception as e:
        global_th_stop = True
        global_th_ret  = f"Error: {str(e)}"


def compactSQL(sql):
    if sql.strip().endswith(";"):
        sql = sql.strip()[:-1]      
    return sql

#######################################################################################
# ROTA: metodos de banco de dados
#######################################################################################

@app.route( "/db_execute" , methods=['GET','POST'] )
def db_execute():
    global global_th_stop

    action           = request.form.get("action")   
    x_tab_id         = request.headers.get("X-Tab-ID") #request.form.get("x_tab_id") 
    dados            = []
    tree             = ""
    explain          = ""
    sql_tipo         = 1
    object_tables    = []
    object_users     = []
    db               = None
    describe         = ""

    try:
        if action == "connect":
            db = dm.ORACLE()
            db.CONNECT(
                p_usuario=request.form.get("usr"),
                p_senha=request.form.get("pwd"),
                p_tns=request.form.get("tns"),
                p_is_direct=(request.form.get("direct") == "1")
            )
            db.username       = session.get('username',None)
            db_list[x_tab_id] = db
            return { "status_code" : db.status_code , "status_msg" : db.status_msg  } 
        

        if action == "change_password_get_user":
            u,t = dm.change_password_get_user(
                alias=request.form.get("alias"),
                username=session.get('username',None)
            )
            return { "db_user": u, "db_tns": t }
        

        if action == "change_password":
            ret = dm.change_password(
                db_tns=request.form.get("db_tns"),
                db_user=request.form.get("db_user"),
                db_password=request.form.get("db_password")
            )
            return { "status_code" : 0 , "status_msg" : ret  }        
        
        if x_tab_id not in db_list:
            return { "status_code" : 1 , "status_msg" : "No Connections Found"  }
        
        db = db_list[x_tab_id]

        if action == "logoff":
            db.disconnect()
            return { "status_code" : 0 , "status_msg" : "Sucesso"  }

        if action == "stop":
            db.stopSQL()

        if action == "commit":
            db.commit()

        if action == "rollback":
            db.rollback()

        if action == "explain":
            sql = compactSQL( request.form.get("sql") )
            explain = db.EXPLAIN( p_sql=sql ) 

        if action == "test_procedure":
            ret = db.PROCEDURE( obj=request.form.get("object_name") ) 
            return { "status_msg" : ret  }

        if action == "connect_after":
            tree, object_tables, object_users = db_objects_view(db)

        if action == "ddl":
            x = request.form.get("object_name").split("...")
            db.DDL( owner=x[0], name=x[2], type=x[1] )

        if action == "execute":
            sql               = request.form.get("sql")
            sql_tipo, sql_obj = dm.tipoSQL(SQL=sql)
            
            if sql_tipo == 1:
                sql = compactSQL(sql)
                db.SELECT( p_sql=sql , logger=True)  
                if db.status_code == 0:
                    dados_brutos  = db.cur.fetchmany(50)
                    dados         = [row_to_dict(db.col_names, linha, db.col_types) for linha in dados_brutos]                    
            
            elif sql_tipo == 2:
                db.EXECUTE( p_sql=sql , logger=True)
            
            elif sql_tipo == 3:
                db.EXECUTE( p_sql=sql )
                if db.status_code == 0:
                    db.SELECT( p_sql=dm_const.C_SQL_ALL_ERRORS % (sql_obj["object_owner"], sql_obj["object_name"]) , logger=True)  
                    if db.status_code == 0:
                        dados_brutos  = db.cur.fetchall()
                        if len(dados_brutos) > 0:
                            dados         = [row_to_dict(db.col_names, linha, db.col_types) for linha in dados_brutos]
                            sql_tipo      = 1

        if action == "save_row_grid":
            sql_tipo = 0
            itens    = request.form.get('itens')
            rowid    = request.form.get('rowid')
            sql      = compactSQL( request.form.get('sql') )
            executeUpdateFromForm(db, rowid, sql, json.loads( itens ) )
        
        if action == "tab_columns":
            if "TABLE" in request.form.get("type_object"):
                sql = dm_const.C_SQL_ALL_TAB_COLUMNS % ( request.form.get('type_filter') )
            else:
                sql = dm_const.C_SQL_ALL_TABLES_COLUMNS % ( request.form.get('type_filter') )
            sql_tipo = 0
            db.SELECT( p_sql=sql )  
            if db.status_code == 0:
                dados = db.cur.fetchall()
        
        if action == "describe":
            object_name = request.form.get('object_name')
            describe    = describeObject(db, object_name)

        if action == "csv_completer":
            global_th_stop    = False
            sql               = compactSQL( request.form.get("sql") )
            first_line_titles = request.form.get("first_line_titles") == "true"
            file              = request.files["file_data"]
            global_th = threading.Thread(target=csvCompleter, args=(db, sql, first_line_titles, file))
            global_th.start()

            return { "status_msg" : "Thread started."  }
        
        if action == "export_to_file":
            global_th_stop    = False
            sql               = compactSQL( request.form.get("sql") )
            file_type         = request.form.get("type")
            table_name        = request.form.get("table_name")
            global_th         = threading.Thread(target=exportToFile, args=(db, sql, int(file_type), table_name))
            global_th.start()
            return { "status_msg" : "Thread started."  }
        
        if action == "view_sessions":
            sql      = db.sql_session.replace("<WHERE>", request.form.get('status') )
            sql_tipo = 1
            db.SELECT( p_sql=sql )  
            dados_brutos  = db.cur.fetchall()
            dados         = [row_to_dict(db.col_names, linha, db.col_types) for linha in dados_brutos]

        if action == "findobj":
            sql      = dm_const.C_SQL_FIND_OBJECT % ( request.form.get('object_name') )
            sql_tipo = 1
            db.SELECT( p_sql=sql )  
            dados_brutos  = db.cur.fetchall()
            dados         = [row_to_dict(db.col_names, linha, db.col_types) for linha in dados_brutos]

        if action == "fetch":
            dados_brutos  = db.cur.fetchmany(50 if action=="execute" else 500 )
            dados         = [row_to_dict(db.col_names, linha, db.col_types) for linha in dados_brutos]
            
    except Exception as e:
        return { "status_code" : 1 , "status_msg" : str(e)  }

    return { "status_msg"    : db.status_msg, 
             "status_code"   : db.status_code,
             "data"          : dados, 
             "columns"       : db.col_names, 
             "columns_types" : db.col_types, 
             "tree"          : tree, 
             "describe"      : describe,
             "explain"       : explain, 
             "dbms"          : db.dbms_output, 
             "sql_type"      : sql_tipo,
             "object_tables" : object_tables,
             "object_users"  : object_users }


#######################################################################################
# ROTA: download
#######################################################################################

@app.route( "/download" , methods=['GET','POST'] )
def download():
    file_path = dm.generateFileName( request.form.get("filename") ,temp=True)
    return send_file(
            file_path,
            as_attachment=True,
            download_name=os.path.basename(file_path)
        )



#######################################################################################
# ROTA: metodos de processos em background (threads)
#######################################################################################

@app.route( "/th_status" , methods=['GET','POST'] )
def th_status():
    return { "global_th_ret" : global_th_ret, "global_th_stop" : global_th_stop }



@app.route( "/th_stop" , methods=['GET','POST'] )
def th_stop():
    global global_th_stop
    global_th_stop = True
    return { "status_msg" : f"{global_th_ret} > Stop signal sent." }
    


#######################################################################################
# ROTA: templates
#######################################################################################

@app.route( "/template" , methods=['GET','POST'] )
def template_actions():
    action = request.form.get("action")
    
    if action == "save":
        newName  = request.form.get("name")
        newValue = request.form.get("value")
        oldName  = request.form.get("old_name")
        
        if "|" not in newName:
            newName = f"root|{newName}"

        dm.configSave( 
            tagName  = oldName, 
            tagValue = { "node": newName, "info" : newValue }, 
            p_tipo   = "SQL_TEMPLATES", 
            username = session.get('username',None) 
        ) 

        return { "status_msg" : "Success"  }
    
    elif action == "load":
        list = dm.configValue( tag="SQL_TEMPLATES", params=[ "%" ], username=session.get('username',None) )
        ret  = "\n".join( [ (x[0] if "|" in x[0] else f"root|{x[0]}" ) for x in list ] )
        return {"templates": ret }

    elif action == "open":
        name = request.form.get("name")
        list = dm.configValue( tag="SQL_TEMPLATES", params=[name], username=session.get('username',None) )
        if list:
            return {"code": list[0][1]}
        return {"code": "Template not found."}

#######################################################################################
# ROTA: metodos de configuração
#######################################################################################

@app.route( "/config_tnsnames" , methods=['GET','POST'] )
def config_tnsnames():
    fp      = os.environ.get("TNS_ADMIN", "-")
    caminho = os.path.join(fp, "tnsnames.ora")
    results = [ f"File {caminho} not found." ]

    if os.path.exists(caminho):
        with open( caminho, 'r') as f:
            content = f.read()

        # Remove comentários
        content = re.sub(r'#.*', '', content)

        # Junta tudo em uma linha só para facilitar parsing
        content = re.sub(r'\s+', ' ', content)

        content = content.strip().replace(' ', '')

        # Regex para capturar blocos de conexão
        pattern = re.compile(
            r'(\w+)\s*=\s*\(DESCRIPTION=.*?HOST\s*=\s*([^)]+).*?PORT\s*=\s*(\d+).*?(SERVICE_NAME|SID)\s*=\s*([^)]+).*?\)',
            re.IGNORECASE
        )

        results = []

        for match in pattern.finditer(content):
            alias   = match.group(1)
            host    = match.group(2)
            port    = match.group(3)
            service = match.group(5)

            formatted = f"{alias:<35} | {host}:{port}/{service}"
            results.append(formatted)

    return {"tnsnames": "\n".join( results )}


@app.route( "/config_get" , methods=['GET','POST'] )
def config_get():
    u = session.get('username',None)
    ret = {
        "tnsSaved" : dm.configValue( tag="tnsSaved", username=u ),
        "tns" : dm.configValue( tag="tns", username=u ),
        "oracle_home" : os.environ.get("ORACLE_HOME", ""),
    }
    return ret

@app.route( "/config_save" , methods=['GET','POST'] )
def config_save():
    u = session.get('username',None)
    dm.configSave( tagName="tnsSaved", tagValue=request.form.get("tnsSaved"), p_tipo="CONFIG" , username=u)
    dm.configSave( tagName="tns", tagValue=request.form.get("tns"), p_tipo="CONFIG" , username=u)
    return {"status_msg": "Configuration saved successfully."}


@app.route( "/config_recall" , methods=['GET','POST'] )
def config_recall():
    u             = session.get('username',None)
    dados_brutos  = dm.configValue(tag="SQL_HISTORY", params=[ request.form.get('text'), request.form.get('database') ],  username=u )
    dados         = [row_to_dict(["Data","Dbname","SQL"], linha, ["STRING","STRING","STRING"]) for linha in dados_brutos]
    return {"data"          : dados, 
            "columns"       : ["Data","Dbname","SQL"],
            "columns_types" : ["DATETIME","STRING","STRING"] }



#######################################################################################
# ROTA: login/logoff
#######################################################################################

@app.route("/error")
def error():
    return render_template("error.html")


@app.route("/logout")
def logout():
    session['username'] = None
    return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get("username")
        senha   = request.form.get("password")
        theme   = request.form.get("theme")

        if ldap_login(username=usuario, password=senha):
            session['username'] = usuario
            session['theme']    = theme
            return redirect("/") 
        else:
            return redirect("/error")

    return render_template("login.html")




#######################################################################################
# ROTA: START
#######################################################################################

@app.route("/ia")
def ia():
    return render_template('ia.html')

    
@app.route("/")
def index():
    username = session.get('username',None)
    css      = session.get('theme',"vs-dark")
    edt      = "vs" if "plsql" in css else "vs-dark"

    if username == None:
        return redirect("/login")
        
    return render_template('index.html', login=username, css=css, edt=edt)



#######################################################################################
# ROTA: main
#######################################################################################

if __name__ == "__main__":
    dm.configOracleHome()
    app.run(host='0.0.0.0')
