package br.algarsql.utils;

import java.sql.Blob;
import java.sql.Clob;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
import java.sql.SQLException;
import java.text.SimpleDateFormat;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import com.fasterxml.jackson.databind.ObjectMapper;

public abstract class DATABASE {

    // =========================================================================
    // VARS
    // =========================================================================
    public int                        status_code = 0;
    public int                        status_code_parallel = 0;
    public int                        status_stop_count = 0;
    public String                     status_msg = "OK";

    public Connection                 global_con = null;
    public PreparedStatement          global_cur = null;
    public ResultSet                  global_rs = null;


    private String                    db_usuario = null;
    private String                    db_senha = null;
    private String                    db_tns = null;
    private String                    db_name = null;
    protected boolean                 db_is_direct = false;
    public String                     db_dbms = "";

    public List<String>               col_names = new ArrayList<>();
    public List<String>               col_types = new ArrayList<>();
    public List<Map<String, Object>>  col_data  = new ArrayList<>();
    public  String                    col_for_update_rowid = null;
    public  String                    col_for_update_table = null;

    public String                     username = "";
    public String                     sql_session = "";
    public SimpleDateFormat           sdf = new java.text.SimpleDateFormat("dd/MM/yyyy HH:mm:ss");
    private String                    last_sql = "-";

    public String                     global_tree_str = "";
    public ArrayList<String>          global_tree_tables = new ArrayList<>();
    public ArrayList<String>          global_tree_users = new ArrayList<>();


    public static DATABASE createConnection(
            String p_usuario,
            String p_senha,
            String p_tns,
            boolean p_is_direct,
            String p_db_name) {

        if (p_tns == null || p_tns.isBlank()) {
            throw new IllegalArgumentException("A conexão TNS não pode ser vazia.");
        }

        String tns = p_tns.trim();
        String tnsLower = tns.toLowerCase(java.util.Locale.ROOT);

        DATABASE db;

        if (!tnsLower.startsWith("jdbc:")) {
            db = new TDBOracle();
            tns = "jdbc:oracle:thin:@" + tns;

        } else if (tnsLower.startsWith("jdbc:oracle:")) {
            db = new TDBOracle();

        } else if (tnsLower.startsWith("jdbc:mysql:")) {
            db = new TDBMySql();

        } else if (tnsLower.startsWith("jdbc:postgresql:")) {
            db = new TDBPosgreSql();

        } else {
            throw new IllegalArgumentException(
                "Tipo de conexão JDBC não suportado: " + tns
            );
        }

        db.db_usuario   = p_usuario;
        db.db_senha     = p_senha;
        db.db_tns       = tns;
        db.db_is_direct = db instanceof TDBOracle
                ? p_is_direct
                : true;
        db.db_name      = p_db_name;

        return db;
    }    


    public void connectDatabase() {
        this.status_code  = 0;
        this.status_msg   = "OK";

        try {
            global_con = DriverManager.getConnection(this.db_tns,this.db_usuario, this.db_senha);
            this.afterConnect();
        } catch (Exception e) {
            this.status_code = -1;
            this.status_msg = e.getMessage();
        }
    }    


    // =========================================================================
    // value
    // =========================================================================

    public String value(Object v) {
        if (v == null) {
            return "null";
        }

        if (v instanceof java.util.Date || v instanceof java.sql.Date || v instanceof java.sql.Timestamp) {
            return "to_date('" + sdf.format(v).replaceAll("/", "-") + "','DD-MM-YYYY HH24:MI:SS')";
        }
        return "'" + v.toString().replace("'", "''") + "'";
    }


    // =========================================================================
    // prepareVars
    // =========================================================================

    protected void prepareVars(String p_sql, boolean logger) {
        this.pingConnection();
        this.db_dbms = "";
        this.col_names.clear();
        this.col_types.clear();
        this.col_data.clear();
        this.status_stop_count = 0;
        if (logger && !this.last_sql.equals(p_sql)) {
            Utils.configSave(this.db_name, p_sql, "SQL_HISTORY", this.username);
            this.last_sql = p_sql;
        }
    }


    // =========================================================================
    // disconnect
    // =========================================================================

    public void disconnect() {
        try {
            if (global_con != null) {
                global_con.close();
            }
        } catch (Exception ignored) {
        }
    }

    // =========================================================================
    // commit
    // =========================================================================

    public void commit() {
        try {
            global_con.commit();
        } catch (Exception e) {
            this.status_code = -1;
            this.status_msg = e.getMessage();
        }
    }

    // =========================================================================
    // rollback
    // =========================================================================

    public void rollback() {
        try {
            global_con.rollback();
        } catch (Exception e) {
            this.status_code = -1;
            this.status_msg = e.getMessage();
        }
    }

    // =========================================================================
    // get_line_column
    // =========================================================================

    private int[] get_line_column(String sql, int offset) {
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
    // executeStatement
    // =========================================================================


    public void executeStatement(String p_sql, boolean logger, Object[] p_bind_values) {
        this.prepareVars(p_sql, logger);

        try {
            if (!this.db_is_direct) {
                this.executeStatementBySecurity(p_sql, logger, p_bind_values);
            } else {
                try (PreparedStatement cur1 = global_con.prepareStatement(p_sql)) {
                    if (p_bind_values != null) {
                        for (int i = 0; i < p_bind_values.length; i++) {
                            @SuppressWarnings("unchecked")
                            Map<String, Object> reg = (Map<String, Object>) p_bind_values[i];
                            cur1.setObject(i + 1, reg.get("value"));
                        }
                    }
                    int rows = cur1.executeUpdate();
                    status_code = 0;
                    status_msg = "SUCESSO - " + rows + " rows";
                }
            }
            this.afterExecuteStatement();
        } catch (Exception e) {
            status_code = -1;
            status_msg = e.getMessage();
        }
    }



    // =========================================================================
    // executeSelect
    // =========================================================================

    public void executeSelect(String p_sql, boolean logger, Integer fetchSize) {
        this.prepareVars(p_sql, logger);
        this.col_for_update_rowid = "";
        this.col_for_update_table = "";

        try {
            if ( global_rs != null && !global_rs.isClosed() ) {
                global_rs.close();
                global_cur.close();
            }

            global_cur = global_con.prepareStatement(p_sql);
            global_cur.setFetchSize(1000);

            if (this.db_is_direct) {
                global_rs = global_cur.executeQuery();
            } else {
                global_rs = this.executeSelectBySecurity(p_sql);
            }

            ResultSetMetaData md = global_rs.getMetaData();

            for (int i = 1; i <= md.getColumnCount(); i++) {
                this.col_names.add(md.getColumnLabel(i));
                this.col_types.add(md.getColumnTypeName(i));
                if ( md.getColumnName(i).toUpperCase().equals("ROWID") || md.getColumnLabel(i).toUpperCase().equals("ROWID")  ) {
                    this.col_for_update_rowid = md.getColumnName(i);

                    Pattern p = Pattern.compile("\\bfrom\\s+([a-zA-Z0-9_]+(?:\\.[a-zA-Z0-9_]+)?)",Pattern.CASE_INSENSITIVE);
                    Matcher m = p.matcher(p_sql);

                    if (m.find()) {
                        this.col_for_update_table = m.group(1);
                    } 
                }
            }

            if (fetchSize != -2) {
                this.fetchData(fetchSize);
            }

            this.status_code = 0;
            this.status_msg = "SUCESSO";

        } catch (SQLException e) {
            this.status_code = -1;
            int[] lc = get_line_column(p_sql, e.getErrorCode());
            this.status_msg = e.getMessage() + "\nError at line " + lc[0] + ", column " + lc[1];
        } catch (Exception e) {
            this.status_code = -1;
            this.status_msg = e.getMessage();
        }       
    }

    // =========================================================================
    // fetchData
    // =========================================================================

    public void fetchData(int fetchSize) throws Exception {
        this.col_data.clear();
        if (global_rs == null || global_rs.isClosed()) {
            return;
        }

        ResultSetMetaData md = global_rs.getMetaData();
        int count = 0;
        while ( global_rs.next() ) {
            count++;
            Map<String, Object> novo = new LinkedHashMap<>();

            for (int i = 1; i <= md.getColumnCount(); i++) {
                Object value = global_rs.getObject(i);

                if ( value == null ) {
                    value = "";
                    
                } else if (md.getColumnTypeName(i).toUpperCase().contains("LOB")) {
                    if (value instanceof Clob) {
                        Clob clob = (Clob) value;
                        value = clob.getSubString(1, (int) clob.length());
                    } else if (value instanceof Blob) {
                        Blob blob = (Blob) value;
                        byte[] bytes = blob.getBytes(1, (int) blob.length());
                        value = java.util.Base64.getEncoder().encodeToString(bytes);                       
                    }
                } else if (value instanceof java.sql.Timestamp || value instanceof java.sql.Date || value instanceof java.util.Date) {
                    value = sdf.format(value); 
                } else {
                    value = value.toString();
                }
                novo.put(md.getColumnLabel(i), value);
            }
            this.col_data.add(novo);

            if (count >= fetchSize && fetchSize != -1) {
                return;
            }
        }
        global_rs.close();
        global_cur.close();
        global_rs = null;
        global_cur = null;
    }

    // =========================================================================
    // executeUpdateFromPrimaryKey
    // =========================================================================
        
    public void executeUpdateFromPrimaryKey(String rowid, String sql, String json_items)
            throws Exception {
        ObjectMapper mapper = new ObjectMapper();

        @SuppressWarnings("unchecked")
        Map<String, Object> dados = mapper.readValue(json_items, Map.class);

        List<Object> params = new ArrayList<>();
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
                    DateTimeFormatter formatter = DateTimeFormatter.ofPattern("dd/MM/yyyy HH:mm:ss");
                    LocalDate localDate = LocalDate.parse(fv.toString(), formatter);
                    fv = java.sql.Date.valueOf(localDate);
                } else if (ft.contains("LOB")) {
                    fv = this.createBinaryObject(fv.toString(), ft.contains("BLOB"));
                }
                Map<String, Object> obj = new HashMap<>();
                obj.put("name", fn);
                obj.put("value", fv);

                params.add(obj);
                set_clause += fn + " = :" + fn + ", ";
            }
        }
        set_clause = set_clause.substring(0, set_clause.length() - 2);
        String SQL_UPDATE_AUX = "UPDATE " + col_for_update_table + " SET " + set_clause + " WHERE " + col_for_update_rowid + " = '" + rowid + "'";
        this.executeStatement(SQL_UPDATE_AUX, false, params.toArray());
    }    


    // =========================================================================
    // executeStatement
    // =========================================================================

    public abstract void executeStatementBySecurity(String p_sql, boolean logger, Object[] p_bind_values) throws Exception;

    // =========================================================================
    // extractDDL
    // =========================================================================

    public abstract String extractDDL(String owner, String type, String name) ;


    // =========================================================================
    // executeSelectBySecurity
    // =========================================================================

    public abstract ResultSet executeSelectBySecurity(String sql) throws Exception;

    // =========================================================================
    // createProcedureTest
    // =========================================================================

    public abstract String createProcedureTest(String obj);

    // =========================================================================
    // executeExplain
    // =========================================================================

    public abstract String executeExplain(String p_sql); 

    // =========================================================================
    // describeObject
    // =========================================================================

    public abstract String describeObject(String p_object_name);

    // =========================================================================
    // treeObjects
    // =========================================================================

    public abstract void treeObjects();

    // =========================================================================
    // createBinaryObject
    // =========================================================================

    public abstract Object createBinaryObject(Object data, boolean is_blob) throws Exception;

    // =========================================================================
    // STOP
    // =========================================================================

    public abstract void stopExecution();

    // =========================================================================
    // allErrors
    // =========================================================================

    public abstract void allErrors(String object_owner, String object_name);

    // =========================================================================
    // findObject
    // =========================================================================

    public abstract void findObject(String object_name, String code_text);

    // =========================================================================
    // filterTableColumns
    // =========================================================================

    public abstract void filterTableColumns(String type_object, String type_filter);

    // =========================================================================
    // pingConnection
    // =========================================================================

     protected abstract void pingConnection();
    
    // =========================================================================
    // afterConnect
    // =========================================================================

    public abstract void afterConnect() throws Exception;

    // =========================================================================
    // afterExecuteStatement
    // =========================================================================

    public abstract void afterExecuteStatement() throws Exception;    
}
