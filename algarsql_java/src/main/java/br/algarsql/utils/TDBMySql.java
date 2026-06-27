package br.algarsql.utils;

import java.sql.CallableStatement;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.stream.Collectors;

public class TDBMySql extends DATABASE {

    @Override
    protected void pingConnection() {
       
    }

    @Override
    public void afterConnect() {
    }

    @Override
    public void executeStatement(String p_sql, boolean logger, Object[] p_bind_values, boolean direct) {
        throw new UnsupportedOperationException("Unimplemented method 'executeStatement'");
    }


    @Override
    public String extractDDL(String owner, String type, String name) {
        String sql = "SHOW CREATE " + type + " `" + owner + "`.`" + name + "`";
        try {
            CallableStatement cs2 = con.prepareCall(sql);
            ResultSet rs2 = cs2.executeQuery();
            if (rs2.next()) {
                ResultSetMetaData md = rs2.getMetaData();
                for (int i = 1; i <= md.getColumnCount(); i++) {
                    String col = md.getColumnLabel(i).toUpperCase();
                    if (col.contains("CREATE")) {
                        return rs2.getString(i);
                    }
                }
            }
            cs2.close();
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
        this.tree_str = "";
        this.tree_tables.clear();
        this.tree_users.clear();

        try {
            this.executeSelect(Constants.C_MYSQL_TREE.replaceAll("<1>", "%"), false, -2);
            while (this.rs.next()) {
                String tree = this.rs.getString("OWNER") + "|" + this.rs.getString("OBJECT_TYPE") + "|"
                        + this.rs.getString("OBJECT_NAME");
                this.tree_str += tree + "\n";
                if (this.rs.getString("OBJECT_TYPE").equals("TABLE")
                        || this.rs.getString("OBJECT_TYPE").equals("VIEW")) {
                    this.tree_tables.add(this.rs.getString("OBJECT_NAME"));
                    this.tree_users.add(this.rs.getString("OWNER"));
                }
            }
        } catch (Exception e) {
            // Handle exception
        }

        this.tree_users = this.tree_users.stream().distinct().sorted()
                .collect(Collectors.toCollection(ArrayList::new));        
    }

    // =========================================================================
    // executeExplain
    // =========================================================================

    @Override
    public String executeExplain(String p_sql) {
        String ret = "";

        try {
            String sql = "EXPLAIN ANALYZE " + p_sql;
            PreparedStatement ps = con.prepareStatement(sql);
            ResultSet rs = ps.executeQuery();
            while (rs.next()) {
                ret = ret + rs.getString(1) + "\n";
            }
            ps.close();   
        } catch ( Exception e ) {
            ret = e.toString();
        }

        return ret.trim();
    }

    // =========================================================================
    // allErrors
    // =========================================================================

    @Override
    public void allErrors(String object_owner, String object_name) {
        prepareVars("",false);
    }


    // =========================================================================
    // findObject
    // =========================================================================

    @Override
    public void findObject(String object_name, String code_text) {
        String sql = Constants.C_MYSQL_TREE.replaceAll("<1>", object_name);
        executeSelect(sql, false, -1);        
    }

    // =========================================================================
    // filterTableColumns
    // =========================================================================    
    
    @Override
    public void filterTableColumns(String type_object, String type_filter) {
        prepareVars("",false);
    }    
    
}
