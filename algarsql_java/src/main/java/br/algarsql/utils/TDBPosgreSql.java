package br.algarsql.utils;

import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.Set;
import java.util.TreeSet;

public class TDBPosgreSql extends DATABASE {
  public static final String C_POSTGRESQL_TREE = """
        WITH xxx AS
        (
            SELECT table_schema AS "OWNER",
                  table_name    AS "OBJECT_NAME",
                  replace(table_type,'BASE TABLE','TABLE')   AS "OBJECT_TYPE"
            FROM information_schema.tables
            WHERE table_type  IN('BASE TABLE','VIEW' )

            UNION ALL

            SELECT routine_schema AS "OWNER",
                  routine_name    AS "OBJECT_NAME",
                  routine_type    AS "OBJECT_TYPE"
            FROM information_schema.routines

            UNION ALL

            SELECT trigger_schema AS "OWNER",
                  trigger_name    AS "OBJECT_NAME",
                  'TRIGGER'       AS "OBJECT_TYPE"
            FROM information_schema.triggers
        )
        SELECT *
        FROM xxx
        WHERE UPPER("OBJECT_NAME") LIKE UPPER('<1>')
        ORDER BY "OWNER", "OBJECT_TYPE", "OBJECT_NAME"
      """; 




    @Override
    protected void pingConnection() {
       
    }

    @Override
    public void afterConnect() throws Exception {
        global_con.setAutoCommit(true);
    }

    @Override
    public void executeStatement(String p_sql, boolean logger, Object[] p_bind_values) {
        throw new UnsupportedOperationException("Unimplemented method 'executeStatement'");
    }


    @Override
    public String extractDDL(String owner, String type, String name) {

        String sql;
        String tipo = type.toUpperCase();

        switch (tipo) {

            case "VIEW":
            case "MATERIALIZED VIEW":
                sql = """
                    SELECT
                        'CREATE ' ||
                        CASE WHEN c.relkind = 'm'
                            THEN 'MATERIALIZED VIEW '
                            ELSE 'OR REPLACE VIEW '
                        END ||
                        quote_ident(n.nspname) || '.' ||
                        quote_ident(c.relname) ||
                        ' AS ' || pg_get_viewdef(c.oid, true)
                    FROM pg_class c
                    JOIN pg_namespace n
                    ON n.oid = c.relnamespace
                    WHERE n.nspname = ?
                    AND c.relname = ?
                    AND c.relkind = ?
                    """;
                break;

            case "FUNCTION":
                sql = """
                    SELECT pg_get_functiondef(p.oid)
                    FROM pg_proc p
                    JOIN pg_namespace n
                    ON n.oid = p.pronamespace
                    WHERE n.nspname = ?
                    AND p.proname = ?
                    AND p.proisagg = false
                    AND p.proiswindow = false
                    ORDER BY p.oid
                    LIMIT 1
                    """;
                break;

            case "BASE TABLE":
            case "TABLE":
                sql = """
                    SELECT
                        'CREATE TABLE ' ||
                        quote_ident(n.nspname) || '.' ||
                        quote_ident(c.relname) || E' (\\n' ||
                        string_agg(
                            '    ' || quote_ident(a.attname) || ' ' ||
                            pg_catalog.format_type(
                                a.atttypid, a.atttypmod
                            ) ||
                            CASE WHEN a.attnotnull
                                THEN ' NOT NULL'
                                ELSE ''
                            END,
                            E',\\n'
                            ORDER BY a.attnum
                        ) ||
                        E'\\n);'
                    FROM pg_class c
                    JOIN pg_namespace n
                    ON n.oid = c.relnamespace
                    JOIN pg_attribute a
                    ON a.attrelid = c.oid
                    WHERE n.nspname = ?
                    AND c.relname = ?
                    AND c.relkind = 'r'
                    AND a.attnum > 0
                    AND NOT a.attisdropped
                    GROUP BY n.nspname, c.relname
                    """;
                break;

            default:
                return "Tipo de objeto não suportado: " + type;
        }

        try (PreparedStatement ps1 = global_con.prepareStatement(sql)) {

            ps1.setString(1, owner);
            ps1.setString(2, name);

            if (tipo.equals("VIEW")) {
                ps1.setString(3, "v");
            } else if (tipo.equals("MATERIALIZED VIEW")) {
                ps1.setString(3, "m");
            }

            try (ResultSet rs2 = ps1.executeQuery()) {
                if (rs2.next()) {
                    return rs2.getString(1);
                }
            }

            return null;

        } catch (SQLException e) {
            return e.toString();
        }
    }

    @Override
    public String createProcedureTest(String obj) {
        return "Unimplemented method 'PROCEDURE'";
    }



    @Override
    public String describeObject(String p_object_name) {
        return "Unimplemented method 'describeObject'";
    }


    @Override
    public void treeObjects() {
        global_tree_str = "";
        global_tree_tables.clear();
        global_tree_users.clear();

        StringBuilder treeBuilder = new StringBuilder();
        Set<String> users = new TreeSet<>();

        try {
            this.executeSelect(
                C_POSTGRESQL_TREE.replace("<1>", "%"),
                false,
                -2
            );

            while (global_rs.next()) {
                String owner = global_rs.getString("OWNER");
                String objectType = global_rs.getString("OBJECT_TYPE");
                String objectName = global_rs.getString("OBJECT_NAME");

                treeBuilder.append(owner)
                        .append('|')
                        .append(objectType)
                        .append('|')
                        .append(objectName)
                        .append('\n');

                if ("TABLE".equals(objectType)
                        || "VIEW".equals(objectType)) {
                    global_tree_tables.add(objectName);

                    if (owner != null) {
                        users.add(owner);
                    }
                }
            }

            global_tree_str = treeBuilder.toString();
            global_tree_users = new ArrayList<>(users);

        } catch (Exception e) {
            System.err.println(
                "Erro ao carregar objetos do PostgreSQL: "
                + e.getMessage()
            );
        }
    }


    // =========================================================================
    // executeExplain
    // =========================================================================


    @Override
    public String executeExplain(String p_sql) {
        StringBuilder ret = new StringBuilder();
        try {
            String sql = "EXPLAIN " + p_sql.trim();

            try (PreparedStatement ps = global_con.prepareStatement(sql);
                ResultSet rs = ps.executeQuery()) {

                ResultSetMetaData md = rs.getMetaData();
                int columns = md.getColumnCount();

                while (rs.next()) {
                    for (int i = 1; i <= columns; i++) {
                        if (i > 1) {
                            ret.append(" | ");
                        }
                        ret.append(md.getColumnLabel(i))
                        .append(": ")
                        .append(rs.getString(i));
                    }
                    ret.append('\n');
                }
            }

        } catch (SQLException e) {
            return e.toString();
        }
        return ret.toString().trim();
    }


    // =========================================================================
    // allErrors
    // =========================================================================

    @Override
    public void allErrors(String object_owner, String object_name) {
        this.prepareVars("",false);
    }


    // =========================================================================
    // findObject
    // =========================================================================

    @Override
    public void findObject(String object_name, String code_text) {
        String sql = C_POSTGRESQL_TREE.replaceAll("<1>", object_name);
        this.executeSelect(sql, false, -1);        
    }

    // =========================================================================
    // filterTableColumns
    // =========================================================================    
    
    @Override
    public void filterTableColumns(String type_object, String type_filter) {
        this.prepareVars("",false);
    }

    // =========================================================================
    // selectBySecurity
    // =========================================================================   

    @Override
    public ResultSet selectBySecurity(String sql) throws Exception {
        throw new UnsupportedOperationException("Unimplemented method 'selectBySecurity'");
    }

    // =========================================================================
    // createBinaryObject
    // =========================================================================

    @Override
    public Object createBinaryObject(Object data, boolean is_blob) throws Exception {
        throw new UnsupportedOperationException("Unimplemented method 'createBinaryObject'");
    }

    // =========================================================================
    // stopExecution
    // =========================================================================

    @Override
    public void stopExecution() {
        try {
            global_cur.cancel();                    
        } catch(Exception ex) {
            ex.printStackTrace();
        }
    }    
}
