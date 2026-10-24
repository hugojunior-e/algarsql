package br.algarsql.utils;

import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.Locale;
import java.util.Set;
import java.util.TreeSet;

public class TDBMySql extends DATABASE {

    public static final String C_MYSQL_TREE = """
                  SELECT *
                  FROM (
                      SELECT
                          TABLE_SCHEMA AS OWNER,
                          TABLE_NAME AS OBJECT_NAME,
                          'TABLE' AS OBJECT_TYPE
                      FROM information_schema.TABLES

                      UNION ALL

                      SELECT
                          ROUTINE_SCHEMA AS OWNER,
                          ROUTINE_NAME AS OBJECT_NAME,
                          ROUTINE_TYPE AS OBJECT_TYPE
                      FROM information_schema.ROUTINES

                      UNION ALL

                      SELECT
                          TRIGGER_SCHEMA AS OWNER,
                          TRIGGER_NAME AS OBJECT_NAME,
                          'TRIGGER' AS OBJECT_TYPE
                      FROM information_schema.TRIGGERS

                      UNION ALL

                      SELECT
                          EVENT_SCHEMA AS OWNER,
                          EVENT_NAME AS OBJECT_NAME,
                          'EVENT' AS OBJECT_TYPE
                      FROM information_schema.EVENTS
                  ) AS xxx
                  WHERE UPPER(OBJECT_NAME) LIKE UPPER('<1>')
                  ORDER BY OWNER, OBJECT_TYPE, OBJECT_NAME
            """;

    @Override
    protected void pingConnection() {

    }

    @Override
    public void afterConnect() throws Exception {
        global_con.setAutoCommit(false);
    }

    @Override
    public void executeStatementBySecurity(String p_sql, boolean logger, Object[] p_bind_values) throws Exception{
        throw new UnsupportedOperationException("Unimplemented method 'executeStatement'");
    }

    @Override
    public String extractDDL(String owner, String type, String name) {
        if (owner == null || owner.isBlank()
                || type == null || type.isBlank()
                || name == null || name.isBlank()) {
            return "Erro: owner, type e name são obrigatórios.";
        }

        String objectType = type.trim().toUpperCase(Locale.ROOT);

        // Evita inserir comandos arbitrários no SQL.
        if (!Set.of("TABLE", "VIEW", "PROCEDURE", "FUNCTION",
                "TRIGGER", "EVENT").contains(objectType)) {
            return "Erro: tipo de objeto MySQL não suportado: " + type;
        }

        String sql = "SHOW CREATE " + objectType + " `"
                + owner.replace("`", "``") + "`.`"
                + name.replace("`", "``") + "`";

        try (PreparedStatement ps = global_con.prepareStatement(sql);
                ResultSet rs = ps.executeQuery()) {

            if (!rs.next()) {
                return null;
            }

            ResultSetMetaData md = rs.getMetaData();

            for (int i = 1; i <= md.getColumnCount(); i++) {
                String column = md.getColumnLabel(i);

                if (column != null
                        && column.toUpperCase(Locale.ROOT).contains("CREATE")) {
                    return rs.getString(i);
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
            this.executeSelect(C_MYSQL_TREE.replace("<1>", "%"), false, -2);

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

                if ("TABLE".equals(objectType) || "VIEW".equals(objectType)) {
                    global_tree_tables.add(objectName);
                    users.add(owner);
                }
            }

            global_tree_str = treeBuilder.toString();
            global_tree_users = new ArrayList<>(users);

        } catch (Exception e) {
            System.err.println("Erro ao carregar objetos do MySQL: " + e.getMessage());
        }
    }

    // =========================================================================
    // executeExplain
    // =========================================================================

    @Override
    public String executeExplain(String p_sql) {
        StringBuilder ret = new StringBuilder();

        try {
            String sql = "EXPLAIN " + p_sql;

            try (PreparedStatement ps = global_con.prepareStatement(sql);
                    ResultSet rs = ps.executeQuery()) {

                ResultSetMetaData meta = rs.getMetaData();
                int columns = meta.getColumnCount();

                while (rs.next()) {
                    for (int i = 1; i <= columns; i++) {
                        if (i > 1) {
                            ret.append(" | ");
                        }

                        ret.append(meta.getColumnLabel(i))
                                .append(": ")
                                .append(rs.getString(i));
                    }

                    ret.append("\n");
                }
            }

        } catch (Exception e) {
            ret.append(e.toString());
        }

        return ret.toString().trim();
    }

    // =========================================================================
    // allErrors
    // =========================================================================

    @Override
    public void allErrors(String object_owner, String object_name) {
        this.prepareVars("", false);
    }

    // =========================================================================
    // findObject
    // =========================================================================

    @Override
    public void findObject(String object_name, String code_text) {
        String sql = C_MYSQL_TREE.replaceAll("<1>", object_name);
        this.executeSelect(sql, false, -1);
    }

    // =========================================================================
    // filterTableColumns
    // =========================================================================

    @Override
    public void filterTableColumns(String type_object, String type_filter) {
        this.prepareVars("", false);
    }

    // =========================================================================
    // selectBySecurity
    // =========================================================================

    @Override
    public ResultSet executeSelectBySecurity(String sql) throws Exception {
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

    // =========================================================================
    // afterExecuteStatement
    // =========================================================================

    @Override
    public void afterExecuteStatement() throws Exception {
        throw new UnsupportedOperationException("Unimplemented method 'afterExecuteStatement'");
    }

}
