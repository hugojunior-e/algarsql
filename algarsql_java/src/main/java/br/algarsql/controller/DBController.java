package br.algarsql.controller;

import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RestController;
import com.fasterxml.jackson.databind.ObjectMapper;

import br.algarsql.utils.Constants;
import br.algarsql.utils.ORACLE;
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

    private void calculateTreeObjects(ORACLE db) {
        db.tree_str = "";
        db.tree_tables.clear();
        db.tree_users.clear();

        try {
            db.SELECT(Constants.C_SQL_TREE, false, false, -2);
            while (db.rs.next()) {
                String tree = db.rs.getString("OWNER") + "|" + db.rs.getString("OBJECT_TYPE") + "|"
                        + db.rs.getString("OBJECT_NAME");
                db.tree_str += tree + "\n";
                if (db.rs.getString("OBJECT_TYPE").equals("TABLE")
                        || db.rs.getString("OBJECT_TYPE").equals("VIEW")) {
                    db.tree_tables.add(db.rs.getString("OBJECT_NAME"));
                    db.tree_users.add(db.rs.getString("OWNER"));
                }
            }
        } catch (Exception e) {
            // Handle exception
        }

        db.tree_users = db.tree_users.stream().distinct().sorted()
                .collect(Collectors.toCollection(ArrayList::new));
    }

    // ==========================================================================================
    //
    // ==========================================================================================

    @SuppressWarnings("unchecked")
    private void executeUpdateFromForm(ORACLE db, String rowid, String sql, String json_items)
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
                    fv = db.create_lob(fv.toString(), ft.contains("BLOB"));
                }
                HashMap<String, Object> obj = new HashMap<>();
                obj.put("name", fn);
                obj.put("value", fv);

                params.add(obj);
                set_clause += fn + " = :" + fn + ", ";
            }
        }
        set_clause = set_clause.substring(0, set_clause.length() - 2);

        String SQL_UPDATE_AUX =
                "UPDATE (" + sql + ") SET " + set_clause + " WHERE ROWID = '" + rowid + "'";

        db.EXECUTE(SQL_UPDATE_AUX, false, params.toArray(), false);
    }

    private String describeObject(ORACLE db, String object_name) {
        String ret = "";

        String sql = String.format(Constants.C_SQL_TABLE_DESCRIBE_COLS, object_name);
        db.SELECT(sql, false, false, -1);
        ret += "<h3>Table Columns</h3>";
        ret += Utils.htmlTable(db.col_names, db.col_data);

        sql = String.format(Constants.C_SQL_TABLE_INDEXES, object_name);
        db.SELECT(sql, false, false, -1);
        ret += "<h3>Table Indexes</h3>";
        ret += Utils.htmlTable(db.col_names, db.col_data);

        sql = String.format(Constants.C_SQL_TABLE_DESCRIBE_PROP, object_name);
        db.SELECT(sql, false, false, -1);

        List<Map<String, Object>> col_prop = new ArrayList<>();
        for (Map<String, Object> linha : db.col_data) {
            for (Map.Entry<String, Object> entry : linha.entrySet()) {
                Map<String, Object> reg = new HashMap<>();
                reg.put("Property", entry.getKey());
                reg.put("Value", entry.getValue());
                col_prop.add(reg);
            }
        }

        ret += "<h3>Table Properties</h3>";
        ret += Utils.htmlTable(List.of("Property", "Value"), col_prop);

        return ret;
    }

    @RequestMapping(value = "/db_execute", method = {RequestMethod.GET, RequestMethod.POST})
    public Map<String, Object> dbExecute(HttpServletRequest request, HttpServletResponse response, HttpSession session) {
        Map<String, Object> ret = new HashMap<>();

        ORACLE db = null;
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
                db = new ORACLE();
                db.CONNECT(request.getParameter("usr").toString(),
                        request.getParameter("pwd").toString(),
                        request.getParameter("tns").toString(),
                        request.getParameter("direct").toString().equals("1"));
                db.username = username;
                session.setAttribute(xTabId, db);
                ret.put("status_msg", db.status_msg);
                ret.put("status_code", db.status_code);
                return ret;
            }

            if (action.equals("change_password_get_user")) {
                String[] msg = Utils.changePasswordGetUser(request.getParameter("alias"),
                        request.getParameter("username"));
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

          
            db = (ORACLE) session.getAttribute(xTabId);

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
                db.stopSQL();
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
                    db.SELECT(sql, false, true, 50);
                }
                if (sql_tipo.sql_type == SQLCodeType.EXECUTE) {
                    db.EXECUTE(sql, true, null, false);
                }
                if (sql_tipo.sql_type == SQLCodeType.COMPILE) {
                    db.EXECUTE(sql, false, null, false);
                    if (db.status_code == 0) {
                        db.SELECT(String.format(Constants.C_SQL_ALL_ERRORS, sql_tipo.object_owner,
                                sql_tipo.object_name), false, false, -1);
                        sql_tipo.sql_type = SQLCodeType.SELECT;
                    }
                }
            }

            if (action.equals("findobj")) {
                String sql = String.format(Constants.C_SQL_FIND_OBJECT,
                        request.getParameter("object_name").toString());
                db.SELECT(sql, false, false, -1);

            }

            if (action.equals("view_sessions")) {
                String sql = db.sql_session.replaceAll("<WHERE>",
                        request.getParameter("status").toString());
                db.SELECT(sql, false, false, -1);
            }

            if (action.equals("save_row_grid")) {
                sql_tipo.sql_type = SQLCodeType.NONE;
                String itens = request.getParameter("itens").toString();
                String rowid = request.getParameter("rowid").toString();
                String sql = request.getParameter("sql").toString();
                executeUpdateFromForm(db, rowid, sql, itens);
            }

            if (action.equals("describe")) {
                describe = describeObject(db, request.getParameter("object_name").toString());
            }

            if (action.equals("test_procedure")) {
                String ret_proc = db.PROCEDURE(request.getParameter("object_name").toString());
                ret.put("status_code", 0);
                ret.put("status_msg", ret_proc);
                return ret;
            }

            if (action.equals("tab_columns")) {
                String type_object = request.getParameter("type_object").toString();
                String type_filter = request.getParameter("type_filter").toString();
                String sql = String.format(Constants.C_SQL_ALL_TABLES_COLUMNS, type_filter);

                if (type_object.contains("TABLE")) {
                    sql = String.format(Constants.C_SQL_ALL_TAB_COLUMNS, type_filter);
                }
                sql_tipo.sql_type = SQLCodeType.NONE;
                db.SELECT(sql, false, false, -1);
            }

            if (action.equals("ddl")) {
                String[] x = request.getParameter("object_name").toString().toUpperCase()
                        .split("\\.\\.\\.");
                ddl = db.DDL(x[0], x[1], x[2]);
            }

            if (action.equals("explain")) {
                String sql = Utils.compactSQL(request.getParameter("sql").toString());
                explain = db.EXPLAIN(sql);
            }

            if (action.equals("connect_after")) {
                calculateTreeObjects(db);
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
                db.FETCH(500);
            }

            if (action.equals("csv_completer")) {
                String sql = Utils.compactSQL(request.getParameter("sql").toString());
                boolean first_line_titles =
                        request.getParameter("first_line_titles").toString().equals("true");
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
        ret.put("object_tables", db.tree_tables.toArray());
        ret.put("object_users", db.tree_users.toArray());
        return ret;
    }
}
