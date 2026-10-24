package br.algarsql.utils;

import java.sql.Blob;
import java.sql.CallableStatement;
import java.sql.Clob;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.TreeSet;
import oracle.jdbc.OracleConnection;
import oracle.jdbc.OracleTypes;

public class TDBOracle extends DATABASE {

    public static final String C_ORACLE_SELECT = "{ call user_exec.pc_exec_dml.pr_exec_select(?, ?) }";

    public static final String C_ORACLE_EXEC = "{ call user_exec.pc_exec_dml.pr_exec_dml(?, ?, ?) }";

    public static final String C_ORACLE_BIND_PREPARE = "{ call user_exec.pc_exec_dml.pr_bind_prepare(?,?,?) }";

    public static final String C_ORACLE_BIND_EXECUTE = "{ call user_exec.pc_exec_dml.pr_bind_execute(?,?) }";

    public static final String C_ORACLE_BIND_VAR = "{ call user_exec.pc_exec_dml.pr_bind_var(p_var => ?, p_tip => ?, %s => ?) }";

    public static final String C_ORACLE_ALL_TABLES_COLUMNS = """
              SELECT TABLE_NAME N, OWNER O,
                     lpad( row_number() over(order by OWNER, TABLE_NAME) , 10,'0') I
                FROM ALL_TABLES
               WHERE OWNER = upper('%s')
               ORDER BY 1
            """;

    public static final String C_ORACLE_TABLE_DESCRIBE_PROP = "SELECT * FROM ALL_TABLES WHERE TABLE_NAME = upper('%s') ORDER BY OWNER";

    public static final String C_ORACLE_TABLE_DESCRIBE_COLS = """
            SELECT t.column_name,
                   t.data_type,
                   t.data_length,
                   t.nullable,
                   t.table_name,
                   t.owner,
                   c.comments AS column_description
              FROM all_tab_columns t
              LEFT JOIN all_col_comments c
                     ON ( c.owner = t.owner
                      AND c.table_name = t.table_name
                      AND c.column_name = t.column_name )
             WHERE t.table_name = UPPER('%s')
             ORDER BY t.owner, t.column_id
            """;

    public static final String C_ORACLE_TABLE_INDEXES = """
            select (SELECT decode(UNIQUENESS,'UNIQUE','UNIQUE','NORMAL')
                      FROM ALL_INDEXES
                     WHERE OWNER = vw.table_owner
                       and INDEX_NAME = vw.INDEX_NAME) INDEX_TYPE,
                   vw.*
              from (
                      SELECT index_name,
                             table_owner,
                             RTRIM(
                                 XMLAGG(
                                     XMLELEMENT(e, column_name || ',')
                                     ORDER BY column_position
                                 ).EXTRACT('//text()'),
                             ',') campos
                        FROM all_ind_columns t
                       WHERE table_name = UPPER('%s')
                       GROUP BY index_name, table_owner
                   ) vw
             order by 1
            """;

    public static final String C_ORACLE_ALL_ERRORS = """
            SELECT ATTRIBUTE, LINE, TEXT
              FROM ALL_ERRORS
             WHERE OWNER = upper('%s')
               AND NAME = upper('%s')
             ORDER BY SEQUENCE
            """;

    public static final String C_ORACLE_START = """
            begin
              dbms_output.enable(100000);
              DBMS_APPLICATION_INFO.SET_CLIENT_INFO('ALGAR SQL');
            end;
            """;

    public static final String C_ORACLE_DBMS = """
                declare
                    l_data_qtd NUMBER := 32000;
                    p_ret      varchar2(32000) := '';
                    lines      DBMS_OUTPUT.CHARARR;
                BEGIN
                    DBMS_OUTPUT.get_lines(lines, l_data_qtd);

                    FOR x IN lines.FIRST .. lines.LAST
                    LOOP
                      p_ret := p_ret || lines(x) || chr(10);
                    END LOOP;

                    :retorno := p_ret;
                END;
            """;

    public static final String C_ORACLE_TREE = """
                SELECT OWNER , OBJECT_TYPE , OBJECT_NAME
                  FROM ALL_OBJECTS
                 WHERE OBJECT_TYPE IN ('PROCEDURE', 'TABLE', 'VIEW', 'FUNCTION', 'TRIGGER', 'MATERIALIZED VIEW', 'PACKAGE', 'TRIGGER')
                   AND OWNER not in ( 'SYSTEM', 'SYS',
                        'ORDDATA', 'FLOWS_FILES', 'APEX_030200', 'APEX_040200', 'APEX_PUBLIC_USER', 'OLAPSYS', 'QUEST', 'OUTLN', 'RMAN', 'XDB', 'C##CLOUD$SERVICE', 'ANONYMOUS',
                        'APPQOSSYS', 'AUDSYS', 'CTXSYS', 'DBSFWUSER', 'DBSNMP', 'DIP', 'DMSYS', 'DVF', 'DVSYS', 'DUMMY', 'EXFSYS', 'GGSYS', 'GSMADMIN_INTERNAL', 'GSMCATUSER', 'GSMUSER', 'LBACSYS',
                        'MDDATA', 'MDSYS', 'MGMT_VIEW', 'OJVMSYS', 'OLAPSYS', 'ORACLE_OCM', 'ORDDATA', 'ORDPLUGINS', 'ORDSYS', 'OUTLN', 'REMOTE_SCHEDULER_AGENT', 'SI_INFORMTN_SCHEMA', 'SCOTT',
                        'SYS$UMF', 'SYSBACKUP', 'SYSDG', 'SYSKM', 'SYSMAN', 'SYSRAC', 'TSMSYS', 'WMSYS', 'XDB', 'XS$NULL', 'OWBSYSOWBSYS_AUDIT', 'SPATIAL_WFS_ADMIN_USR', 'SPATIAL_CSW_ADMIN_USR',
                        'OWBSYS', 'OWBSYS_AUDIT', 'SPATIAL_WFS_ADMIN_USR', 'SPATIAL_CSW_ADMIN_USR')
                order by OWNER,OBJECT_TYPE,OBJECT_NAME
            """;

    public static final String C_ORACLE_FIND_OBJECT = """
            SELECT * FROM
            (
               SELECT owner,
                      object_name,
                      object_type,
                      'by name' method
                 FROM ALL_OBJECTS
                WHERE 1=<3>
                  AND OBJECT_NAME LIKE upper('<1>')
                  AND OBJECT_TYPE NOT IN ('SYNONYM')
                order by owner,object_type,object_name
             )
             union
             select * from
             (
               SELECT s.owner, s.name, s.type, 'by code' method FROM all_source s
               WHERE 2=<3>
               AND s.name LIKE upper('<1>')
               AND upper(s.text) LIKE upper('%<2>%')
               group by s.owner, s.name, s.type
             )
             """;

    public static final String C_ORACLE_ALL_TAB_COLUMNS = """
              SELECT COLUMN_NAME N, OWNER O,
                     lpad( row_number() over(order by OWNER, COLUMN_ID) , 10,'0') I
                FROM ALL_TAB_COLUMNS
               WHERE TABLE_NAME = upper('%s')
               ORDER BY OWNER, COLUMN_ID
            """;

    public static final String C_ORACLE_SESSIONS_ORA = """
            SELECT  x.username || '(' || count(1) over (partition by x.username order by 1) || ')' username,
                    x.STATUS|| '(' || count(1) over (partition by x.username, x.status order by 1) || ')' status,
                    x.sid,
                    x.serial#,
                    x.logon_time,
                    x.osuser,
                    x.machine,
                    x.program,
                    x.sql_id,
                    x.client_info,
            sql_fulltext
            FROM   sys.v_$sqlarea sqlarea, sys.v_$session x
            WHERE  x.sql_hash_value = sqlarea.hash_value(+)
            and x.sql_address = sqlarea.address(+)
            and x.username is not null
            AND x.status LIKE '<WHERE>'
            ORDER BY x.username, x.status, X.LOGON_TIME
            """;

    public static final String C_ORACLE_SESSIONS_ALGAR = """
                SELECT  USERNAME || '(' || count(1) over (partition by username order by 1) || ')' username,
                        STATUS|| '(' || count(1) over (partition by username, status order by 1) || ')' status,
                        SID,
                        SERIAL#,
                        LOGON_TIME,
                        OSUSER,
                        MACHINE,
                        PROGRAM,
                        SQL_ID,
                        CLIENT_INFO,
                        SQL_FULLTEXT
                FROM <TABELA>
               WHERE STATUS LIKE '<WHERE>'
            ORDER BY USERNAME, STATUS, LOGON_TIME
            """;

    public static final String C_ORACLE_PROCEDURE_ARGS = """
                  select argument_name,
                         position,
                         data_type,
                         in_out,
                         owner
                    from all_arguments
                   where owner like '%s'
                     and object_name   = '%s'
                     and nvl(package_name,'-') = '%s'
                     and argument_name is not null
                    order by position
            """;

    public static final String C_ORACLE_DML = """
            begin
              :ddl := user_exec.PC_EXEC_DML.f_get_ddl( '<1>' , '<2>', '<3>')
                        ||
                      case when '<1>'  = 'PACKAGE' then
                            '<end_package_spec>' || user_exec.PC_EXEC_DML.f_get_ddl( 'PACKAGE BODY', '<2>', '<3>')
                      end;
            end;
            """;

    public static final String C_ORACLE_DML_DIRECT = """
            declare
              v_type  varchar2(100) := '<1>';
              v_owner varchar2(100) := '<2>';
              v_name  varchar2(100) := '<3>';
              v_ret   clob;
              v_tipo  varchar2(32000);
            begin
              dbms_lob.createtemporary(v_ret, true);

              if v_type not in ('TABLE', 'VIEW', 'MATERIALIZED VIEW') then
                dbms_lob.append(v_ret, 'CREATE OR REPLACE ');
                for cx in (select case when line = 1 and upper(text) not like '%' || upper(owner) || '.%' then
                                         REGEXP_REPLACE(text,name, owner || '.' || name, 1, 0, 'i')
                                       else
                                         text
                                  end text,
                                  line,
                                  type
                             from all_source
                            where name = v_name
                              and type like REPLACE( trim(replace(v_type,'BODY','')) , 'PACKAGE', 'PACKAGE%' )
                              and owner = v_owner
                            order by type, line)
                loop
                  if (cx.line = 1 and cx.type = 'PACKAGE BODY') then
                    dbms_lob.append(v_ret, '<end_package_spec>CREATE OR REPLACE ');
                  end if;
                  dbms_lob.append(v_ret, cx.text);
                end loop;
              end if;

              if v_type = 'TABLE' then
                dbms_lob.append(v_ret, 'CREATE TABLE ' || v_owner || '.' || v_name || '(' || chr(10));
                for cx in (
                            SELECT '  '
                                   || RPAD(COLUMN_NAME,40,' ')
                                   || DATA_TYPE
                                   || (
                                        CASE WHEN DATA_TYPE NOT IN ('DATE','CLOB','BLOB') THEN
                                        '(' || DATA_LENGTH || nvl2(data_precision, ',' || data_precision, '') || ')'
                                        END
                                      )
                                   || ' '
                                   || (CASE WHEN NULLABLE = 'N' THEN 'NOT NULL' END)   text,
                                   DATA_DEFAULT,
                                   case when COLUMN_ID = (max(COLUMN_ID) over()) then '' else ',' end fim
                              FROM ALL_TAB_COLUMNS
                             WHERE OWNER = v_owner
                               AND TABLE_NAME = v_name
                            ORDER BY COLUMN_ID
                          )
                loop
                  v_tipo := CX.DATA_DEFAULT;
                  if v_tipo is not null then
                    v_tipo := ' DEFAULT ' || trim(v_tipo);
                  end if;

                  dbms_lob.append(v_ret, cx.text || v_tipo || cx.fim || chr(10));
                end loop;
                dbms_lob.append(v_ret, ');' || chr(10));

                FOR cx IN (SELECT index_name,
                                  RTRIM(XMLAGG(XMLELEMENT(e, column_name || ',') ORDER BY column_position).EXTRACT('//text()'), ',') campos
                             FROM all_ind_columns t
                            WHERE table_name = v_name
                              AND table_owner = v_owner
                            GROUP BY index_name)
                LOOP
                  SELECT UNIQUENESS
                    INTO v_tipo
                    FROM ALL_INDEXES
                   WHERE OWNER = v_owner
                     AND INDEX_NAME = CX.INDEX_NAME;

                  dbms_lob.append(v_ret,'CREATE ' || (CASE WHEN v_tipo = 'UNIQUE' THEN v_tIpo END) || ' INDEX ' || v_owner || '.' || cx.index_name || ' ON ' || v_owner || '.' || v_name || '(' || cx.campos || ');' || CHR(10));
                END LOOP;

              end if;

              if v_type like '%VIEW%' then
                SELECT A INTO V_TIPO FROM
                (
                        SELECT TEXT A FROM ALL_VIEWS WHERE OWNER = v_owner AND VIEW_NAME = v_name
                        UNION ALL
                        SELECT QUERY A FROM ALL_MVIEWS WHERE OWNER = v_owner AND MVIEW_NAME = v_name
                );

                dbms_lob.append(v_ret, 'CREATE OR REPLACE ' || v_type || ' ' || v_owner || '.' || v_name || ' AS ' || chr(10));
                dbms_lob.append(v_ret, V_TIPO);
              end if;
              :ddl := v_ret;
            end;
            """;

         

    // =========================================================================
    // pingConnection
    // =========================================================================

    @Override
    protected void pingConnection() {
        try {
            OracleConnection oc = global_con.unwrap(OracleConnection.class);
            global_con.isValid(3);
            if (oc.pingDatabase() != OracleConnection.DATABASE_OK) {
                throw new Exception("Connection lost.");
            }
        } catch (Exception e) {
            connectDatabase();
        }
    }

    // =========================================================================
    // CONNECT
    // =========================================================================

    @Override
    public void afterConnect() throws Exception {
        global_con.createStatement().execute(C_ORACLE_START);
        global_con.setAutoCommit(false);

        this.sql_session = C_ORACLE_SESSIONS_ORA;
        if (this.db_is_direct == false) {
            this.executeSelect(
                    "SELECT OWNER FROM ALL_VIEWS WHERE VIEW_NAME = 'VW_SESSIONS' ORDER BY 1",
                    false, -2);
            if (this.status_code == 0 && global_rs != null) {
                if (global_rs.next()) {
                    this.sql_session = C_ORACLE_SESSIONS_ALGAR.replace("<TABELA>",
                            global_rs.getString(1) + ".VW_SESSIONS");
                }
            } else {
                this.db_is_direct = false;
            }
        }
    }

    // =========================================================================
    // afterExecuteStatement
    // =========================================================================

    @Override
    public void afterExecuteStatement() throws Exception {
        try (CallableStatement cs = global_con.prepareCall(C_ORACLE_DBMS)) {
            cs.registerOutParameter(1, OracleTypes.VARCHAR);
            cs.execute();
            this.db_dbms = cs.getString(1);
        }
    }

    // =========================================================================
    // executeStatement
    // =========================================================================

    @Override
    public void executeStatementBySecurity(String p_sql, boolean logger, Object[] p_bind_values)  throws Exception {
        if (p_bind_values != null && p_bind_values.length > 0) {
            CallableStatement cs1 = global_con.prepareCall(C_ORACLE_BIND_PREPARE);
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

            for (int i = 0; i < p_bind_values.length; i++) {
                String var_name = "p_str";
                int var_idx = 1;
                @SuppressWarnings("unchecked")
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
                cs1 = global_con.prepareCall(String.format(C_ORACLE_BIND_VAR, var_name));
                cs1.setString(1, fn);
                cs1.setInt(2, var_idx);
                cs1.setObject(3, fv);
                cs1.execute();
                cs1.close();

            }

            cs1 = global_con.prepareCall(C_ORACLE_BIND_EXECUTE);
            cs1.registerOutParameter(1, OracleTypes.INTEGER);
            cs1.registerOutParameter(2, OracleTypes.VARCHAR);
            cs1.execute();
            status_code = cs1.getInt(1);
            status_msg = cs1.getString(2);
            cs1.close();

        } else {
            CallableStatement cs1 = global_con.prepareCall(C_ORACLE_EXEC);
            cs1.registerOutParameter(2, OracleTypes.INTEGER);
            cs1.registerOutParameter(3, OracleTypes.VARCHAR);
            cs1.setString(1, p_sql);
            cs1.execute();
            status_code = cs1.getInt(2);
            status_msg = cs1.getString(3);
            cs1.close();
        }
    }

    // =========================================================================
    // extractDDL
    // =========================================================================

    @Override
    public String extractDDL(String owner, String type, String name) {
        this.prepareVars("", false);
        String ret = "";
        try {
            String sql = C_ORACLE_DML;
            if (db_is_direct) {
                sql = C_ORACLE_DML_DIRECT;
            }

            CallableStatement ps1 = global_con
                    .prepareCall(sql.replaceAll("<1>", type).replaceAll("<2>", owner).replaceAll("<3>", name));
            ps1.registerOutParameter(1, java.sql.Types.CLOB);
            ps1.execute();
            status_code = 0;
            status_msg = "Sucess";
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

    @Override
    public String createProcedureTest(String obj) {
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

            String sql = String.format(C_ORACLE_PROCEDURE_ARGS, v_owner, v_name, v_package);
            this.executeSelect(sql, false, -2);

            List<String> decls = new ArrayList<>();
            List<String> params = new ArrayList<>();
            List<String> prints = new ArrayList<>();

            while (global_rs.next()) {
                String arg_name = global_rs.getString(1);
                String data_type = global_rs.getString(3);
                String in_out = global_rs.getString(4);

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
            global_rs.close();

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
    // describeObject
    // =========================================================================

    @Override
    public String describeObject(String p_object_name) {
        String ret = "";

        String sql = String.format(C_ORACLE_TABLE_DESCRIBE_COLS, p_object_name);
        this.executeSelect(sql, false, -1);
        ret += "<h3>Table Columns</h3>";
        ret += Utils.htmlTable(this.col_names, this.col_data);

        sql = String.format(C_ORACLE_TABLE_INDEXES, p_object_name);
        this.executeSelect(sql, false, -1);
        ret += "<h3>Table Indexes</h3>";
        ret += Utils.htmlTable(this.col_names, this.col_data);

        sql = String.format(C_ORACLE_TABLE_DESCRIBE_PROP, p_object_name);
        this.executeSelect(sql, false, -1);

        List<Map<String, Object>> col_prop = new ArrayList<>();
        for (Map<String, Object> linha : this.col_data) {
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

    @Override
    public void treeObjects() {
        StringBuilder sb = new StringBuilder(64 * 1024);

        global_tree_str = "";
        global_tree_tables = new ArrayList<>();
        TreeSet<String> users = new TreeSet<>();

        try {
            this.executeSelect(C_ORACLE_TREE, false, -2);

            while (global_rs.next()) {

                String owner = global_rs.getString("OWNER");
                String type = global_rs.getString("OBJECT_TYPE");
                String name = global_rs.getString("OBJECT_NAME");

                sb.append(owner)
                        .append('|')
                        .append(type)
                        .append('|')
                        .append(name)
                        .append('\n');

                if ("TABLE".equals(type) || "VIEW".equals(type)) {
                    global_tree_tables.add(name);
                    users.add(owner);
                }
            }

        } catch (Exception e) {
            // tratar
        }

        global_tree_str = sb.toString();
        global_tree_users = new ArrayList<>(users);
    }

    // =========================================================================
    // executeExplain
    // =========================================================================

    @Override
    public String executeExplain(String p_sql) {
        String ret = "";

        try {
            global_con.createStatement().executeUpdate("DELETE FROM PLAN_TABLE");
            global_con.createStatement().executeUpdate("EXPLAIN PLAN FOR\n" + p_sql);
            String sql = "SELECT PLAN_TABLE_OUTPUT FROM TABLE(DBMS_XPLAN.DISPLAY())";
            PreparedStatement ps = global_con.prepareStatement(sql);
            ResultSet rs2 = ps.executeQuery();
            while (rs2.next()) {
                ret = ret + rs2.getString(1) + "\n";
            }
            ps.close();

        } catch (Exception e) {
            ret = e.toString();
        }

        return ret.trim();
    }

    // =========================================================================
    // allErrors
    // =========================================================================

    @Override
    public void allErrors(String object_owner, String object_name) {
        this.executeSelect(String.format(C_ORACLE_ALL_ERRORS, object_owner, object_name), false, -1);
    }

    // =========================================================================
    // findObject
    // =========================================================================

    @Override
    public void findObject(String object_name, String code_text) {
        String sql = C_ORACLE_FIND_OBJECT
                .replaceAll("<1>", object_name)
                .replaceAll("<2>", code_text)
                .replaceAll("<3>", code_text.length() < 3 ? "1" : "2");

        this.executeSelect(sql, false, -1);
    }

    // =========================================================================
    // filterTableColumns
    // =========================================================================

    @Override
    public void filterTableColumns(String type_object, String type_filter) {
        this.prepareVars("", false);
        String sql = String.format(C_ORACLE_ALL_TABLES_COLUMNS, type_filter);

        if (type_object.contains("TABLE")) {
            sql = String.format(C_ORACLE_ALL_TAB_COLUMNS, type_filter);
        }
        this.executeSelect(sql, false, -1);
    }

    // =========================================================================
    // executeSelectBySecurity
    // =========================================================================

    @Override
    public ResultSet executeSelectBySecurity(String sql) throws Exception {
        CallableStatement cs = global_con.prepareCall(C_ORACLE_SELECT);
        cs.setString(1, sql);
        cs.registerOutParameter(2, OracleTypes.CURSOR);
        cs.execute();
        return (ResultSet) cs.getObject(2);
    }

    // =========================================================================
    // createBinaryObject
    // =========================================================================

    @Override
    public Object createBinaryObject(Object data, boolean is_blob) throws Exception {
        OracleConnection oc = global_con.unwrap(OracleConnection.class);

        if (is_blob) {
            Blob blob = oc.createBlob();
            byte[] bytes = java.util.Base64.getDecoder().decode(data.toString());

            blob.setBytes(1, bytes );
            return blob;
        }
        Clob clob = oc.createClob();
        clob.setString(1, data.toString());
        return clob;
    }

    // =========================================================================
    // stopExecution
    // =========================================================================

    @Override
    public void stopExecution() {
        try {
            OracleConnection oc = global_con.unwrap(OracleConnection.class);
            oc.cancel();
            this.status_stop_count++;
            if (this.status_stop_count > 3) {
                oc.abort();
            }
        } catch (Exception ignored) {
            ignored.printStackTrace();
        }        
    }    
}
