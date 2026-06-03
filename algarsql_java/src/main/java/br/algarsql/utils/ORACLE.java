package br.algarsql.utils;

import java.sql.Blob;
import java.sql.CallableStatement;
import java.sql.Clob;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
import java.sql.SQLException;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Properties;
import oracle.jdbc.OracleConnection;
import oracle.jdbc.OracleTypes;

public class ORACLE {

    // =========================================================================
    // VARS
    // =========================================================================
    public int status_code = 0;
    public int status_code_parallel = 0;
    public int stop_status_count = 0;
    public String status_msg = "OK";

    public Connection con = null;
    public PreparedStatement cur = null;
    private CallableStatement cs = null;
    public ResultSet rs = null;

    public String last_sql = "-";

    public String login_global_name = "";
    public int login_sid = 0;
    public String login_banner = "";

    private String db_usuario = null;
    private String db_senha = null;
    private String db_tns = null;
    private boolean db_is_direct = false;

    public List<String> col_names = new ArrayList<>();
    public List<String> col_types = new ArrayList<>();
    public List<Map<String, Object>> col_data = new ArrayList<>();

    public String dbms_output = "";
    public String username = "";
    public String sql_session = "";
    DateTimeFormatter fmt = DateTimeFormatter.ofPattern("dd/MM/yyyy HH:mm:ss");

    public boolean is_running = false;

    public String tree_str = "";
    public ArrayList<String> tree_tables = new ArrayList<>();
    public ArrayList<String> tree_users = new ArrayList<>();

    // =========================================================================
    // =========================================================================
    // value
    // =========================================================================

    public String value(Object v) {
        if (v == null) {
            return "null";
        }

        if (v instanceof java.util.Date) {
            return "to_date('" + v + "','YYYY-MM-DD HH24:MI:SS')";
        }
        return "'" + v.toString().replace("'", "''") + "'";
    }

    // =========================================================================
    // pingConnection
    // =========================================================================

    private void pingConnection() {
        try {
            OracleConnection oc = con.unwrap(OracleConnection.class);
            con.isValid(3);
            if ( oc.pingDatabase() != OracleConnection.DATABASE_OK ) {
                throw new Exception("Connection lost.");
            }
        } catch (Exception e) {
            CONNECT(db_usuario, db_senha, db_tns, db_is_direct);
            System.out.print("Reconnecting user " + db_usuario);
        }
    }
    

    // =========================================================================
    // prepareVars
    // =========================================================================

    private void prepareVars(String p_sql, boolean logger) {
        pingConnection();
        dbms_output = "";
        col_names.clear();
        col_types.clear();
        col_data.clear();
        stop_status_count = 0;
        if (logger && !last_sql.equals(p_sql)) {
            Utils.configSave(login_global_name, p_sql, "SQL_HISTORY", username);
            last_sql = p_sql;
        }
    }

    // =========================================================================
    // CONNECT
    // =========================================================================

    public void CONNECT(String p_usuario, String p_senha, String p_tns, boolean p_is_direct) {
        db_is_direct = p_is_direct;
        login_sid = 0;
        status_code = 0;
        status_msg = "OK";

        try {
            if (p_usuario == null || p_senha == null || p_tns == null) {
                throw new Exception("Parameter User/Pass Invalid!");
            }
            this.db_usuario = p_usuario;
            this.db_senha = p_senha;
            this.db_tns = p_tns;

            Properties props = new Properties();
            props.put("user", p_usuario);
            props.put("password", p_senha);            
            props.put("oracle.net.keepAlive", "true");
            props.put("oracle.jdbc.ReadTimeout", "3600000");
            props.put("oracle.net.CONNECT_TIMEOUT", "3600000");

            con = DriverManager.getConnection("jdbc:oracle:thin:@" + p_tns, props);
            con.setAutoCommit(false);
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
            if (p_is_direct == false) {
                this.SELECT(
                        "SELECT OWNER FROM ALL_VIEWS WHERE VIEW_NAME = 'VW_SESSIONS' ORDER BY 1",
                        p_is_direct, false, -2);
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
    // disconnect
    // =========================================================================

    public void disconnect() {
        try {
            if (con != null) {
                con.close();
            }
        } catch (Exception ignored) {
        }
    }

    // =========================================================================
    // commit
    // =========================================================================

    public void commit() {
        try {
            con.commit();
        } catch (Exception e) {
            status_code = -1;
            status_msg = e.getMessage();
        }
    }

    // =========================================================================
    // rollback
    // =========================================================================

    public void rollback() {
        try {
            con.rollback();
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
    // create_lob
    // =========================================================================

    public Object create_lob(Object data, boolean is_blob) throws Exception {
        OracleConnection oc = con.unwrap(OracleConnection.class);

        if (is_blob) {
            Blob blob = oc.createBlob();
            blob.setBytes(1, data.toString().getBytes() );
            return blob;
        }
        Clob clob = oc.createClob();
        clob.setString(1, data.toString());
        return clob;
    }



    // =========================================================================
    // get_line_column
    // =========================================================================

    public int[] get_line_column(String sql, int offset) {
        String[] lines = sql.split("\n");
        int current = 0;
        for (int i = 0; i < lines.length; i++) {
            String line = lines[i] + "\n";
            if (current + line.length() >= offset) {
                int column = offset - current;
                return new int[] {i + 1, column};
            }
            current += line.length();
        }
        return new int[] {-1, -1};
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

    public void FETCH(int fetchSize) throws Exception {
        this.col_data.clear();
        if (this.rs == null || rs.isClosed()) {
            return;
        }

        ResultSetMetaData md = rs.getMetaData();
        int count = 0;
        while (rs.next()) {
            count++;
            Map<String, Object> novo = new LinkedHashMap<>();

            for (int i = 1; i <= md.getColumnCount(); i++) {
                Object value = rs.getObject(i);

                if (md.getColumnTypeName(i).toUpperCase().contains("LOB")) {
                    if (value instanceof Clob) {
                        Clob clob = (Clob) value;
                        value = clob.getSubString(1, (int) clob.length());
                    } else if (value instanceof Blob) {
                        Blob blob = (Blob) value;
                        value = new String(blob.getBytes(1, (int) blob.length()));
                    }
                } else if (value instanceof java.sql.Timestamp) {
                    value = fmt.format(rs.getTimestamp(i).toLocalDateTime());
                } else {
                    value = rs.getString(i);
                }
                novo.put(md.getColumnName(i), value);
            }
            col_data.add(novo);

            if (count >= fetchSize && fetchSize != -1) {
                return;
            }
        }
        this.rs.close();
        this.cur.close();
        this.rs = null;
        this.cur = null;
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
