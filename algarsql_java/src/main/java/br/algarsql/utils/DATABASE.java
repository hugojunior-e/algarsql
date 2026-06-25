package br.algarsql.utils;

import oracle.jdbc.OracleConnection;
import java.sql.Blob;
import java.sql.CallableStatement;
import java.sql.Clob;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public abstract class DATABASE {

    // =========================================================================
    // VARS
    // =========================================================================
    public int status_code = 0;
    public int status_code_parallel = 0;
    public int stop_status_count = 0;
    public String status_msg = "OK";

    public Connection con = null;
    public PreparedStatement cur = null;
    protected CallableStatement cs = null;
    public ResultSet rs = null;

    public String last_sql = "-";

    public String login_global_name = "";
    public int login_sid = 0;
    public String login_banner = "";

    protected String db_usuario = null;
    protected String db_senha = null;
    protected String db_tns = null;
    protected boolean db_is_direct = false;

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


    public static DATABASE createConnection(String p_usuario, String p_senha, String p_tns, boolean p_is_direct) {
        TDBOracle o = new TDBOracle();

        o.db_is_direct = p_is_direct;
        o.login_sid    = 0;
        o.status_code  = 0;
        o.status_msg   = "OK";

        try {
            if (p_usuario == null || p_senha == null || p_tns == null) {
                throw new Exception("Parameter User/Pass Invalid!");
            }
            o.db_usuario = p_usuario;
            o.db_senha   = p_senha;
            o.db_tns     = p_tns;

            String db_type = p_tns.startsWith("jdbc") ? p_tns : "jdbc:oracle:thin:@";

            o.con = DriverManager.getConnection(db_type + p_tns,p_usuario, p_senha);
            o.con.setAutoCommit(false);

            o.afterConnect();

        } catch (Exception e) {
            o.status_code = -1;
            o.status_msg = e.getMessage();
        }
        return o;
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
    // prepareVars
    // =========================================================================

    protected void prepareVars(String p_sql, boolean logger) {
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
    // pingConnection
    // =========================================================================

     abstract protected void pingConnection();
    

    // =========================================================================
    // AFTER CONNECT
    // =========================================================================

    abstract public void afterConnect();

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

    abstract public void STOP();

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

    abstract public void EXECUTE(String p_sql, boolean logger, Object[] p_bind_values, boolean direct);

    // =========================================================================
    // SELECT
    // =========================================================================

    abstract public void SELECT(String p_sql, boolean direct, boolean logger, Integer fetchSize);

    // =========================================================================
    // FETCH
    // =========================================================================

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

                if ( value == null ) {
                    value = "";
                    
                } else if (md.getColumnTypeName(i).toUpperCase().contains("LOB")) {
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
                    value = value.toString();
                }
                novo.put(md.getColumnName(i), value);
            }
            col_data.add(novo);

            if (count >= fetchSize && fetchSize != -1) {
                break;
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

    abstract public String DDL(String owner, String type, String name) ;

    // =========================================================================
    // PROCEDURE
    // =========================================================================

    abstract public String PROCEDURE(String obj);

    // =========================================================================
    // EXPLAIN
    // =========================================================================

    abstract public String EXPLAIN(String p_sql);
}
