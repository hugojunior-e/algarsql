#!/usr/bin/python3

import os
import zipfile
import sys
import dm
import csv
import json
import dm_const
import datetime
from flask import Flask, render_template, request
from html import escape



app       = Flask(__name__)
db_list   = {}



TABLE_STYLE = """
<style>
  table {
    border-collapse: collapse;
    font-size: 12px;
    margin-bottom: 20px;
  }
  th, td {
    border: 1px solid black;
    padding: 4px 8px;
    text-align: left;
  }
  th {
    background-color: #f0f0f0;
  }
</style>
"""


def _html_table(headers, rows):
    html = "<table>"
    html += "<tr>" + "".join(f"<th>{escape(str(h))}</th>" for h in headers) + "</tr>"

    for row in rows:
        html += "<tr>" + "".join(
            f"<td>{escape(str(col))}</td>" for col in row
        ) + "</tr>"

    html += "</table>"
    return html




def get_code_in_zip():
    x          = zipfile.ZipFile(sys.argv[0], "r")
    index_html = x.read("templates/index.html").decode("utf-8")
    style_css  = x.read("static/style-dark.css").decode("utf-8")
    tree_js    = x.read("static/tree.js").decode("utf-8") 
    funcs_js   = x.read("static/funcs.js").decode("utf-8") 

    return index_html.replace("INLINE_START-->","").replace("<!--INLINE_END","").replace("<!--INLINE-->", f"<style>{ style_css }</style> <script>{ tree_js }</script> <script>{ funcs_js }</script>")




@app.route("/")
def index():
    if "AlgarSQL" in os.path.basename(sys.argv[0]):
        return get_code_in_zip()
    return render_template('index.html')



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
        r[col] = "" if val is None else val
    return r




def db_objects_view(db):
    ret = ""
    tables = []
    users = []

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
    try:
        l_filenames = ["exported_to_insert.sql", "exported.csv"]
        db.SELECT(p_sql=sql )
        if db.status_code == 0:
            f_file = open( file=dm.generateFileName( l_filenames[file_type],inOutputDir=True), mode="w", encoding="utf-8" )
            qtd      = 0 

            if file_type == 0:
                s_insert_title = f"""insert into {table_name} ({",".join(db.col_names)}) """
                for data in iter(lambda: db.cur.fetchmany(5000), []):
                    qtd  += len(data)
                    for r in data:
                        f_file.write( f"""{s_insert_title} values ({ ",".join(  [ db.value(xx) for xx in r]   ) });\n""" )

            if file_type == 1:
                arq      = csv.writer(f_file,delimiter=";",quotechar='"', escapechar="\\",quoting=csv.QUOTE_ALL)
                arq.writerow( db.col_names )
                for data in iter(lambda: db.cur.fetchmany(5000), []):
                    qtd += len(data)
                    arq.writerows(data)

            f_file.close()
            return f"Exported { qtd } rows to { f_file.name }"
        else:
            return f"Error: { db.status_msg }"
    except Exception as e:
        return f"Error: { str(e) }"
    

def describeObject(db, object_name):
    ret = TABLE_STYLE

    # === Columns ===
    sql = dm_const.C_SQL_TABLE_DESCRIBE_COLS % object_name
    db.SELECT(p_sql=sql)

    if db.status_code == 0:
        data = db.cur.fetchall()
        ret += "<h3>Table Columns</h3>"
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


@app.route( "/db_execute" , methods=['GET','POST'] )
def db_execute():
    action        = request.form.get("action")   
    session_id    = request.form.get("session_id") 
    dados         = []
    tree          = ""
    explain       = ""
    sql_tipo      = 1
    object_tables = []
    object_users  = []
    db            = None
    describe      = ""
    try:   
        if action == "connect":
            db = dm.ORACLE()
            db.CONNECT(
                p_usuario=request.form.get("usr"),
                p_senha=request.form.get("pwd"),
                p_tns=request.form.get("tns"),
                p_is_direct=(request.form.get("direct") == "1")
            )
            db_list[session_id] = db    
            if db.status_code == 0:
                tree,object_tables,object_users = db_objects_view(db)
        else:
            if action == "recall_sql":
                dados_brutos  = dm.configValue(tag="*recall", params=[ request.form.get('text'), request.form.get('database') ] )
                dados         = [row_to_dict(["Data","Dbname","SQL"], linha, ["STRING","STRING","STRING"]) for linha in dados_brutos]
                return {"data"          : dados, 
                        "columns"       : ["Data","Dbname","SQL"],
                        "columns_types" : ["DATETIME","STRING","STRING"] }
                    
            if session_id not in db_list:
                return { "status_code" : 1 , "status_msg" : "No Connections Found"  }
            
            db         = db_list[session_id]

            if action == "stop":
                db.stopSQL()

            elif action == "commit":
                db.commit()

            elif action == "rollback":
                db.rollback()

            elif action == "explain":
                explain = db.EXPLAIN( p_sql=request.form.get("sql") ) 

            elif action == "ddl":
                x = request.form.get("object_name").split("...")
                db.DDL( owner=x[0], name=x[2], type=x[1] )

            elif action == "execute":
                sql        = request.form.get("sql")
                sql_tipo   = dm.tipoSQL(SQL=sql)
                
                if sql_tipo == 1:
                    db.SELECT( p_sql=sql , logger=True)  
                    if db.status_code == 0:
                        dados_brutos  = db.cur.fetchmany(50)
                        dados         = [row_to_dict(db.col_names, linha, db.col_types) for linha in dados_brutos]                    
                else:
                    db.EXECUTE( p_sql=sql , logger=True)

            elif action == "save_row_grid":
                sql_tipo = 0
                itens    = request.form.get('itens')
                rowid    = request.form.get('rowid')
                sql      = request.form.get('sql')
                executeUpdateFromForm(db, rowid, sql, json.loads( itens ) )
            
            elif action == "tab_columns":
                if "TABLE" in request.form.get("type_object"):
                    sql = dm_const.C_SQL_ALL_TAB_COLUMNS % ( request.form.get('type_filter') )
                else:
                    sql = dm_const.C_SQL_ALL_TABLES_COLUMNS % ( request.form.get('type_filter') )
                sql_tipo = 0
                db.SELECT( p_sql=sql )  
                return db.cur.fetchall()
            
            elif action == "describe":
                object_name = request.form.get('object_name')
                describe    = describeObject(db, object_name)

            elif action == "export_to_file":
                sql = request.form.get("sql")
                file_type = request.form.get("type")
                table_name = request.form.get("table_name")
                return { "status_msg" : exportToFile(db, sql, int(file_type), table_name )  }
            
            elif action == "view_sessions":
                sql      = db.sql_session.replace("<WHERE>", request.form.get('status') )
                sql_tipo = 1
                db.SELECT( p_sql=sql )  
                dados_brutos  = db.cur.fetchall()
                dados         = [row_to_dict(db.col_names, linha, db.col_types) for linha in dados_brutos]

            elif action == "findobj":
                sql      = dm_const.C_SQL_FIND_OBJECT % ( request.form.get('object_name') )
                print(sql)
                sql_tipo = 1
                db.SELECT( p_sql=sql )  
                dados_brutos  = db.cur.fetchall()
                dados         = [row_to_dict(db.col_names, linha, db.col_types) for linha in dados_brutos]

            elif action == "fetch":
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




@app.route( "/get_config" , methods=['GET','POST'] )
def get_config():
    ret = {
        "tnsSaved" : dm.configValue( tag="tnsSaved" ),
        "tns" : dm.configValue( tag="tns" ),
        "OracleInstantClientDir" : dm.configValue( tag="OracleInstantClientDir" ),
        "template_dir" : dm.configValue( tag="template_dir" ),
        "output_dir" : dm.configValue( tag="output_dir" ),
    }
    return ret

@app.route( "/save_config" , methods=['GET','POST'] )
def save_config():
    dm.configSave( tagName="tnsSaved", tagValue=request.form.get("tnsSaved"), p_tipo="CONFIG" )
    dm.configSave( tagName="tns", tagValue=request.form.get("tns"), p_tipo="CONFIG" )
    dm.configSave( tagName="OracleInstantClientDir", tagValue=request.form.get("OracleInstantClientDir"), p_tipo="CONFIG" )
    dm.configSave( tagName="template_dir", tagValue=request.form.get("template_dir"), p_tipo="CONFIG" )
    dm.configSave( tagName="output_dir", tagValue=request.form.get("output_dir"), p_tipo="CONFIG" )
    return {"status_msg": "Configuration saved successfully."}

#######################################################################################
# main
#######################################################################################

if __name__ == "__main__":
    dm.configOracleHome()
    app.run(host='0.0.0.0',port=5000)
