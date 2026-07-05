package br.algarsql.utils;

import oracle.jdbc.OracleConnection;
import oracle.jdbc.OracleTypes;
import java.sql.Blob;
import java.sql.CallableStatement;
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
    public int status_code = 0;
    public int status_code_parallel = 0;
    public int stop_status_count = 0;
    public String status_msg = "OK";

    public Connection con = null;
    public PreparedStatement cur = null;
    protected CallableStatement cs = null;
    public ResultSet rs = null;

    public String last_sql = "-";

    public String  login_global_name = "";
    public int     login_sid = 0;
    public String  login_banner = "";

    protected String   db_usuario = null;
    protected String   db_senha = null;
    protected String   db_tns = null;
    protected boolean  db_is_direct = false;

    public List<String>               col_names = new ArrayList<>();
    public List<String>               col_types = new ArrayList<>();
    public List<Map<String, Object>>  col_data  = new ArrayList<>();

    public String dbms_output = "";
    public String username = "";
    public String sql_session = "";
    SimpleDateFormat sdf = new java.text.SimpleDateFormat("dd/MM/yyyy HH:mm:ss");

    public boolean is_running = false;

    public String tree_str = "";
    public ArrayList<String> tree_tables = new ArrayList<>();
    public ArrayList<String> tree_users = new ArrayList<>();




    public static DATABASE createConnection(String p_usuario, String p_senha, String p_tns, boolean p_is_direct) {
        DATABASE o = null;

        if ( p_tns.startsWith("jdbc") ) {
            if ( p_tns.contains("oracle") )  o = new TDBOracle();
            if ( p_tns.contains("mysql")  )  o = new TDBMySql();
        } else {
            o = new TDBOracle();
        }

        o.db_usuario   = p_usuario;
        o.db_senha     = p_senha;
        o.db_tns       = p_tns.startsWith("jdbc") ? p_tns : "jdbc:oracle:thin:@" + p_tns;
        o.db_is_direct = p_is_direct;

        if ( !(o instanceof TDBOracle) ) {
            o.db_is_direct = true;
        }

        return o;
    }


    public void connectDatabase() {
        this.login_sid    = 0;
        this.status_code  = 0;
        this.status_msg   = "OK";

        try {
            this.con = DriverManager.getConnection(db_tns,this.db_usuario, this.db_senha);
            this.con.setAutoCommit(false);

            this.afterConnect();

        } catch (Exception e) {
            this.status_code = -1;
            this.status_msg = e.getMessage();
        }
    }    


    // =========================================================================
    // createOracleLob
    // =========================================================================

    public Object createOracleLob(Object data, boolean is_blob) throws Exception {
        OracleConnection oc = con.unwrap(OracleConnection.class);

        if (is_blob) {
            Blob blob = oc.createBlob();
            //byte[] bytes = data.toString().getBytes()
            byte[] bytes = java.util.Base64.getDecoder().decode(data.toString());

            blob.setBytes(1, bytes );
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

        if (v instanceof java.util.Date || v instanceof java.sql.Date || v instanceof java.sql.Timestamp) {
            return "to_date('" + sdf.format(v).replaceAll("/", "-") + "','DD-MM-YYYY HH24:MI:SS')";
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

     protected abstract void pingConnection();
    

    // =========================================================================
    // AFTER CONNECT
    // =========================================================================

    public abstract void afterConnect();

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

    public void stopExecution() {
        try {
            if ( this.db_tns.contains("oracle") ) {
                OracleConnection oc = con.unwrap(OracleConnection.class);
                oc.cancel();
                stop_status_count++;
                if (stop_status_count > 3) {
                    oc.abort();
                }
            } else {
                this.cur.cancel();                    
            }
        } catch (Exception ignored) {
            ignored.printStackTrace();
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

    public abstract void executeStatement(String p_sql, boolean logger, Object[] p_bind_values);

    // =========================================================================
    // SELECT
    // =========================================================================

    public void executeSelect(String p_sql, boolean logger, Integer fetchSize) {
        prepareVars(p_sql, logger);

        try {
            this.is_running = true;
            if (rs != null && !rs.isClosed()) {
                rs.close();
                cur.close();
            }

            cur = con.prepareStatement(p_sql);
            cur.setFetchSize(1000);

            if (this.db_is_direct) {
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
                col_names.add(md.getColumnLabel(i));
                col_types.add(md.getColumnTypeName(i));
            }

            if (fetchSize != -2) {
                this.fetchData(fetchSize);
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
    // fetchData
    // =========================================================================

    public void fetchData(int fetchSize) throws Exception {
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
                        //value = new String(blob.getBytes(1, (int) blob.length()));
                        
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
    // extractDDL
    // =========================================================================

    public abstract String extractDDL(String owner, String type, String name) ;

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
    // executeUpdateFromPrimaryKey
    // =========================================================================
        

    public void executeUpdateFromPrimaryKey(String rowid, String sql, String json_items)
            throws Exception {

        String tableName = "";
        String pkName    = "ROWID";

        Pattern p = Pattern.compile("\\bfrom\\s+([a-zA-Z0-9_]+(?:\\.[a-zA-Z0-9_]+)?)",Pattern.CASE_INSENSITIVE);
        Matcher m = p.matcher(sql);

        if (m.find()) {
            tableName = m.group(1);
        } 
        
        p = Pattern.compile("(?i)\\b(?:\\w+\\.)?(\\w+)\\s+(?:AS\\s+)?ROWID\\b");
        m = p.matcher(sql);

        if (m.find()) {
            pkName = m.group(1);
        }

                
        ObjectMapper mapper = new ObjectMapper();

        @SuppressWarnings("unchecked")
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
                    DateTimeFormatter formatter = DateTimeFormatter.ofPattern("dd/MM/yyyy HH:mm:ss");
                    LocalDate localDate = LocalDate.parse(fv.toString(), formatter);
                    fv = java.sql.Date.valueOf(localDate);
                } else if (ft.contains("LOB")) {
                    fv = this.createOracleLob(fv.toString(), ft.contains("BLOB"));
                }
                HashMap<String, Object> obj = new HashMap<>();
                obj.put("name", fn);
                obj.put("value", fv);

                params.add(obj);
                set_clause += fn + " = :" + fn + ", ";
            }
        }
        set_clause = set_clause.substring(0, set_clause.length() - 2);

        //String SQL_UPDATE_AUX = "UPDATE (" + sql + ") SET " + set_clause + " WHERE ROWID = '" + rowid + "'";
        String SQL_UPDATE_AUX = "UPDATE " + tableName + " SET " + set_clause + " WHERE " + pkName + " = '" + rowid + "'";

        this.executeStatement(SQL_UPDATE_AUX, false, params.toArray());
    }    

}
