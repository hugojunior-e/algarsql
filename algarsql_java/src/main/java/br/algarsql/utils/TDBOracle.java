package br.algarsql.utils;

import java.sql.CallableStatement;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import oracle.jdbc.OracleConnection;
import oracle.jdbc.OracleTypes;

public class TDBOracle extends DATABASE{

    // =========================================================================
    // pingConnection
    // =========================================================================

    protected void pingConnection() {
        try {
            OracleConnection oc = con.unwrap(OracleConnection.class);
            con.isValid(3);
            if ( oc.pingDatabase() != OracleConnection.DATABASE_OK ) {
                throw new Exception("Connection lost.");
            }
        } catch (Exception e) {
            //CONNECT(db_usuario, db_senha, db_tns, db_is_direct);
        }
    }
    

    // =========================================================================
    // CONNECT
    // =========================================================================

    public void afterConnect() {
        try {
            con.createStatement().execute(Constants.C_SQL_START);

            PreparedStatement ps = con.prepareStatement(
                    "select global_name, banner, Sys_Context('USERENV', 'SID') from global_name, v$version");
            rs = ps.executeQuery();
            if (rs.next()) {
                login_global_name = rs.getString(1);
                login_banner = rs.getString(2);
                login_sid = rs.getInt(3);
            }
            rs.close();

            this.sql_session = Constants.C_SQL_SESSIONS_ORA;
            if (this.db_is_direct == false) {
                this.SELECT(
                        "SELECT OWNER FROM ALL_VIEWS WHERE VIEW_NAME = 'VW_SESSIONS' ORDER BY 1",
                        this.db_is_direct, false, -2);
                if (this.rs.next()) {
                    this.sql_session = Constants.C_SQL_SESSIONS_ALGAR.replace("<TABELA>",
                            rs.getString(1) + ".VW_SESSIONS");
                }
                this.rs.close();
            }

        } catch (Exception e) {
            status_code = -1;
            status_msg = e.getMessage();
        }
    }

    // =========================================================================
    // STOP
    // =========================================================================

    public void STOP()  {
        try {
            OracleConnection oc = con.unwrap(OracleConnection.class);
            oc.cancel();
            stop_status_count++;
            if (stop_status_count > 3) {
                oc.abort();
            }
        } catch (Exception ignored) {
            ignored.printStackTrace();
        }
    }


    // =========================================================================
    // EXECUTE
    // =========================================================================

    @SuppressWarnings("unchecked")
    public void EXECUTE(String p_sql, boolean logger, Object[] p_bind_values, boolean direct) {
        prepareVars(p_sql, logger);

        try {
            this.is_running = true;

            if (direct || this.db_is_direct) {
                PreparedStatement cur1 = con.prepareStatement(p_sql);
                if (p_bind_values != null && p_bind_values.length > 0) {
                    for (int i = 0; i < p_bind_values.length; i++) {
                        HashMap<String, Object> reg = (HashMap<String, Object>) p_bind_values[i];
                        // String fn = reg.get("name").toString();
                        Object fv = reg.get("value");
                        cur1.setObject(i + 1, fv);
                    }
                }

                int rows = cur1.executeUpdate();
                status_code = 0;
                status_msg = "SUCESSO - " + rows + " rows";
                cur1.close();
            } else {
                if (p_bind_values != null && p_bind_values.length > 0) {

                    // prepara variaveis do bind

                    CallableStatement cs1 = con.prepareCall(Constants.C_SQL_BIND_PREPARE);
                    cs1.setString(1, p_sql);
                    cs1.registerOutParameter(2, OracleTypes.INTEGER);
                    cs1.registerOutParameter(3, OracleTypes.VARCHAR);
                    cs1.executeUpdate();
                    status_code = cs1.getInt(2);
                    status_msg = cs1.getString(3);
                    cs1.close();

                    if (status_code != 0) {
                        return;
                    }

                    // popula valores das variaveis do bind

                    for (int i = 0; i < p_bind_values.length; i++) {
                        String var_name = "p_str";
                        int var_idx = 1;
                        HashMap<String, Object> reg = (HashMap<String, Object>) p_bind_values[i];
                        String fn = reg.get("name").toString();
                        Object fv = reg.get("value");

                        if (fv instanceof java.sql.Clob) {
                            var_name = "p_clob";
                            var_idx = 3;
                        } else if (fv instanceof java.sql.Blob) {
                            var_name = "p_blob";
                            var_idx = 4;
                        } else if (fv instanceof java.sql.Timestamp) {
                            var_name = "p_date";
                            var_idx = 2;
                        }
                        cs1 = con.prepareCall(String.format(Constants.C_SQL_BIND_VAR, var_name));
                        cs1.setString(1, fn);
                        cs1.setInt(2, var_idx);
                        cs1.setObject(3, fv);
                        cs1.execute();
                        cs1.close();

                    }

                    // executa a sql com bind ja preparado e setado

                    cs1 = con.prepareCall(Constants.C_SQL_BIND_EXECUTE);
                    cs1.registerOutParameter(1, OracleTypes.INTEGER);
                    cs1.registerOutParameter(2, OracleTypes.VARCHAR);
                    cs1.execute();
                    status_code = cs1.getInt(1);
                    status_msg = cs1.getString(2);
                    cs1.close();

                } else {
                    CallableStatement cs1 = con.prepareCall(Constants.C_SQL_EXEC);
                    cs1.registerOutParameter(2, OracleTypes.INTEGER);
                    cs1.registerOutParameter(3, OracleTypes.VARCHAR);
                    cs1.setString(1, p_sql);
                    cs1.execute();
                    status_code = cs1.getInt(2);
                    status_msg = cs1.getString(3);
                    cs1.close();
                }
            }
            CallableStatement cs3 = con.prepareCall(Constants.C_SQL_DBMS);
            cs3.registerOutParameter(1, OracleTypes.VARCHAR);
            cs3.execute();
            this.dbms_output = cs3.getString(1);
            cs3.close();

        } catch (Exception e) {
            status_code = -1;
            status_msg = e.getMessage();
        } finally {
            this.is_running = false;
        }
    }

    // =========================================================================
    // SELECT
    // =========================================================================

    public void SELECT(String p_sql, boolean direct, boolean logger, Integer fetchSize) {
        prepareVars(p_sql, logger);

        try {
            this.is_running = true;
            if (rs != null && !rs.isClosed()) {
                rs.close();
                cur.close();
            }

            cur = con.prepareStatement(p_sql);
            cur.setFetchSize(1000);

            if (direct || this.db_is_direct) {
                this.rs = this.cur.executeQuery(p_sql);
            } else {
                this.cs = this.con.prepareCall(Constants.C_SQL_SELECT);
                cs.setString(1, p_sql);
                cs.registerOutParameter(2, OracleTypes.CURSOR);
                cs.execute();
                this.rs = (ResultSet) cs.getObject(2);
            }

            ResultSetMetaData md = rs.getMetaData();

            for (int i = 1; i <= md.getColumnCount(); i++) {
                col_names.add(md.getColumnName(i));
                col_types.add(md.getColumnTypeName(i));
            }

            if (fetchSize != -2) {
                this.FETCH(fetchSize);
            }

            status_code = 0;
            status_msg = "SUCESSO";

        } catch (SQLException e) {
            status_code = -1;
            int[] lc = get_line_column(p_sql, e.getErrorCode());
            status_msg = e.getMessage() + "\nError at line " + lc[0] + ", column " + lc[1];
        } catch (Exception e) {
            status_code = -1;
            status_msg = e.getMessage();
        } finally {
            this.is_running = false;
        }
    }

       // =========================================================================
    // DDL
    // =========================================================================

    public String DDL(String owner, String type, String name) {
        prepareVars("", false);
        String ret = "";
        try {

            String sql = Constants.C_SQL_DML;
            if (db_is_direct) {
                sql = Constants.C_SQL_DML_DIRECT;
            }

            CallableStatement ps1 = this.con.prepareCall(
                    sql.replaceAll("<1>", type).replaceAll("<2>", owner).replaceAll("<3>", name));
            ps1.registerOutParameter(1, java.sql.Types.CLOB);
            ps1.execute();
            status_code = 0;
            status_msg  = "Sucess";
            ret = ps1.getString(1);
            ps1.close();
        } catch (Exception e) {
            status_code = -1;
            status_msg = e.getMessage();
        }
        return ret;
    }

    // =========================================================================
    // PROCEDURE
    // =========================================================================

    public String PROCEDURE(String obj) {
        try {

            String[] dat = obj.trim().toUpperCase().split("\\.");

            String v_name = "%";
            String v_owner = "%";
            String v_package = "-";

            if (dat.length == 1) {
                v_name = dat[0];
            }

            if (dat.length == 2) {
                v_owner = dat[0];
                v_name = dat[1];
            }

            if (dat.length > 2) {
                v_owner = dat[0];
                v_package = dat[1];
                v_name = dat[2];
            }

            String sql = String.format(Constants.C_SQL_PROCEDURE_ARGS, v_owner, v_name, v_package);
            this.SELECT(sql, false, false, -2);

            List<String> decls = new ArrayList<>();
            List<String> params = new ArrayList<>();
            List<String> prints = new ArrayList<>();

            while (this.rs.next()) {
                String arg_name = this.rs.getString(1);
                String data_type = this.rs.getString(3);
                String in_out = this.rs.getString(4);

                String v = "v_" + arg_name.toLowerCase();
                String t;

                if ("VARCHAR2".equals(data_type) || "CHAR".equals(data_type)) {
                    t = data_type + "(1000) := 'TESTE';";
                } else if ("NUMBER".equals(data_type)) {
                    t = "NUMBER := 0;";
                } else if ("DATE".equals(data_type)) {
                    t = "DATE := SYSDATE;";
                } else {
                    t = data_type + ";";
                }

                decls.add(String.format("%-40s %s", v, t));
                params.add(arg_name + " => " + v);

                if (in_out != null && in_out.contains("OUT")) {
                    prints.add("DBMS_OUTPUT.PUT_LINE('" + arg_name + "=' || " + v + ");");
                }
            }
            this.rs.close();

            String decl_block = String.join("\n", decls);
            String param_block = String.join(",\n", params);
            String print_block = String.join("\n", prints);
            return """
                    DECLARE
                    """ + "\n" + decl_block + "\nBEGIN\n  " + v_owner + "." + v_name + "\n  (\n"
                    + param_block + "\n  );\n" + print_block + "\nEND;";

        } catch (Exception e) {
            return e.getMessage();
        }
    }

    // =========================================================================
    // EXPLAIN
    // =========================================================================

    public String EXPLAIN(String p_sql) {
        try {
            EXECUTE("DELETE FROM PLAN_TABLE", false, null, true);
            EXECUTE("EXPLAIN PLAN FOR\n" + p_sql, false, null, true);
            SELECT("SELECT PLAN_TABLE_OUTPUT FROM TABLE(DBMS_XPLAN.DISPLAY())", true, false, -1);
            List<String> lines = new ArrayList<>();

            for (Map<String, Object> row : col_data) {
                lines.add(row.get("PLAN_TABLE_OUTPUT").toString());
            }
            return String.join("\n", lines);
        } catch (Exception e) {
            return e.getMessage();
        }
    }    
}
