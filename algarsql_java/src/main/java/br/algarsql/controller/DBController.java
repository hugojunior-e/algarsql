package br.algarsql.controller;

import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RestController;
import com.fasterxml.jackson.databind.ObjectMapper;

import br.algarsql.utils.Constants;
import br.algarsql.utils.DATABASE;
import br.algarsql.utils.ParallelProcess;
import br.algarsql.utils.SQLCodeType;
import br.algarsql.utils.Utils;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.servlet.http.HttpSession;

@RestController
public class DBController {

    // ==========================================================================================
    //
    // ==========================================================================================

    @SuppressWarnings("unchecked")
    private void executeUpdateFromForm(DATABASE db, String rowid, String sql, String json_items)
            throws Exception {
        ObjectMapper mapper = new ObjectMapper();
        Map<String, Object> dados = mapper.readValue(json_items, Map.class);
        ArrayList<Object> params = new ArrayList<>();
        String set_clause = "";
        for (Map.Entry<String, Object> entry : dados.entrySet()) {
            String fn = entry.getKey();

            if (!fn.startsWith("@")) {
                String ft = dados.get("@" + fn).toString();
                Object fv = entry.getValue();

                if ( fv == null || fv.toString().isEmpty()) {
                    fv = null;
                }
                else if (ft.contains("DATE")) {
                    DateTimeFormatter formatter =
                            DateTimeFormatter.ofPattern("dd/MM/yyyy HH:mm:ss");
                    LocalDate localDate = LocalDate.parse(fv.toString(), formatter);
                    fv = java.sql.Date.valueOf(localDate);
                } else if (ft.contains("LOB")) {
                    fv = db.createOracleLob(fv.toString(), ft.contains("BLOB"));
                }
                HashMap<String, Object> obj = new HashMap<>();
                obj.put("name", fn);
                obj.put("value", fv);

                params.add(obj);
                set_clause += fn + " = :" + fn + ", ";
            }
        }
        set_clause = set_clause.substring(0, set_clause.length() - 2);

        String SQL_UPDATE_AUX = "UPDATE (" + sql + ") SET " + set_clause + " WHERE ROWID = '" + rowid + "'";

        db.executeStatement(SQL_UPDATE_AUX, false, params.toArray(), false);
    }



    @RequestMapping(value = "/db_execute", method = {RequestMethod.GET, RequestMethod.POST})
    public Map<String, Object> dbExecute(HttpServletRequest request, HttpServletResponse response, HttpSession session) {
        Map<String, Object> ret = new HashMap<>();

        DATABASE db = null;
        String action = request.getParameter("action");
        String xTabId = request.getHeader("X-Tab-ID");
        String describe = "";
        String username = "";
        String explain = "";
        String ddl = "";
        SQLCodeType sql_tipo = new SQLCodeType();

        try {
            Object o = session.getAttribute("username");

            if ( o == null ) {
                response.setStatus(401);
                ret.put("redirect", Constants.PAGE_LOGIN);
                return ret;
            }  
            username = o.toString();

            if (action.equals("connect")) {
                db = DATABASE.createConnection(
                        request.getParameter("usr").toString(),
                        request.getParameter("pwd").toString(),
                        request.getParameter("tns").toString(),
                        request.getParameter("direct").toString().equals("1")
                );
                db.username = username;
                db.connectDatabase();
                db.treeObjects();

                session.setAttribute(xTabId, db);
                ret.put("status_msg", db.status_msg);
                ret.put("status_code", db.status_code);
                ret.put("tree", db.tree_str);
                ret.put("object_tables", db.tree_tables.toArray());
                ret.put("object_users", db.tree_users.toArray());
                return ret;
            }

            if (action.equals("change_password_get_user")) {
                String[] msg = Utils.changePasswordGetUser(request.getParameter("alias"),
                        o.toString());
                ret.put("db_user", msg[1]);
                ret.put("db_tns", msg[2]);
                ret.put("status_msg", msg[0]);
                return ret;
            }

            if (action.equals("change_password")) {
                String msg = Utils.changePassword(request.getParameter("db_tns").toString(),
                        request.getParameter("db_user").toString(),
                        request.getParameter("db_password").toString());
                ret.put("status_code", 0);
                ret.put("status_msg", msg);
                return ret;
            }

          
            db = (DATABASE) session.getAttribute(xTabId);

            ret.put("status_code", 0);
            ret.put("status_msg", "Sucesso");

            if (db == null) {
                ret.put("status_code", 1);
                ret.put("status_msg", "No Connections Found");
                return ret;
            }

            if (action.equals("logoff")) {
                db.disconnect();
                session.removeAttribute(xTabId);
            }

            if (action.equals("stop")) {
                db.stopExecution();
            }

            if (action.equals("commit")) {
                db.commit();
            }

            if (action.equals("rollback")) {
                db.rollback();
            }

            if (action.equals("execute")) {
                String sql = request.getParameter("sql").toString();

                sql_tipo = Utils.tipoSQL(sql);

                if (sql_tipo.sql_type == SQLCodeType.SELECT) {
                    sql = Utils.compactSQL(sql);
                    db.executeSelect(sql, true, 50);
                }
                if (sql_tipo.sql_type == SQLCodeType.DML) {
                    sql = Utils.compactSQL(sql);
                    db.executeStatement(sql, true, null, false);
                }
                if (sql_tipo.sql_type == SQLCodeType.PLSQL_BLOCK) {
                    db.executeStatement(sql, true, null, false);
                }
                if (sql_tipo.sql_type == SQLCodeType.COMPILE) {
                    db.executeStatement(sql, false, null, false);
                    if (db.status_code == 0) {
                        db.allErrors(sql_tipo.object_owner,sql_tipo.object_name);
                        sql_tipo.sql_type = SQLCodeType.SELECT;
                    }
                }
            }

            if (action.equals("findobj")) {
                String on = request.getParameter("object_name").toString();
                String ct = request.getParameter("code_text").toString();
                db.findObject(on, ct);
            }

            if (action.equals("view_sessions")) {
                String sql = db.sql_session.replaceAll("<WHERE>", request.getParameter("status").toString());
                db.executeSelect(sql, false, -1);
            }

            if (action.equals("save_row_grid")) {
                sql_tipo.sql_type = SQLCodeType.NONE;
                String itens = request.getParameter("itens").toString();
                String rowid = request.getParameter("rowid").toString();
                String sql = request.getParameter("sql").toString();
                sql = Utils.compactSQL(sql);
                executeUpdateFromForm(db, rowid, sql, itens);
            }

            if (action.equals("describe")) {
                describe = db.describeObject( request.getParameter("object_name").toString() );
            }

            if (action.equals("test_procedure")) {
                String ret_proc = db.createProcedureTest(request.getParameter("object_name").toString());
                ret.put("status_code", 0);
                ret.put("status_msg", ret_proc);
                return ret;
            }

            if (action.equals("tab_columns")) {
                String type_object = request.getParameter("type_object").toString();
                String type_filter = request.getParameter("type_filter").toString();
                db.filterTableColumns(type_object, type_filter);
                sql_tipo.sql_type = SQLCodeType.NONE;
            }

            if (action.equals("ddl")) {
                String[] x = request.getParameter("object_name").toString()
                        .split("\\.\\.\\.");
                ddl = db.extractDDL(x[0], x[1], x[2]);
            }

            if (action.equals("explain")) {
                String sql = Utils.compactSQL(request.getParameter("sql").toString());
                explain = db.executeExplain(sql);
            }

            if (action.equals("connect_after")) {
                db.treeObjects();
            }

            if (action.equals("export_to_file")) {
                String sql = Utils.compactSQL(request.getParameter("sql").toString());
                int file_type = Integer.parseInt(request.getParameter("type").toString());
                String table_name = request.getParameter("table_name").toString();
                new ParallelProcess(0, db, sql, file_type, table_name).start();
                ret.put("status_code", 0);
                ret.put("status_msg", "Export started successfully");
                return ret;
            }

            if (action.equals("fetch")) {
                db.fetchData(500);
            }

            if (action.equals("csv_completer")) {
                String sql = Utils.compactSQL(request.getParameter("sql").toString());
                boolean first_line_titles = request.getParameter("first_line_titles").toString().equals("true");
                String csv_data = request.getParameter("file_data").toString();
                String file_name = request.getParameter("file_name").toString();
                new ParallelProcess(1, db, sql, first_line_titles, csv_data, file_name).start();
                ret.put("status_code", 0);
                ret.put("status_msg", "Export started successfully");
                return ret;

            }
        } catch (Exception e) {
            ret.put("status_code", -1);
            ret.put("status_msg", e.getMessage());
            return ret;
        }

        // ---------------------------------------------------------
        // RETURN
        // ---------------------------------------------------------
        ret.put("ddl", ddl);
        ret.put("status_msg", db.status_msg);
        ret.put("status_code", db.status_code);
        ret.put("data", db.col_data);
        ret.put("columns", db.col_names.toArray());
        ret.put("columns_types", db.col_types.toArray());
        ret.put("tree", db.tree_str);
        ret.put("describe", describe);
        ret.put("explain", explain);
        ret.put("dbms", db.dbms_output);
        ret.put("sql_type", sql_tipo.sql_type);
        return ret;
    }
}
