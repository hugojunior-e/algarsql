package br.algarsql.utils;

import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
import java.sql.SQLException;

public class TDBMySql extends DATABASE {

    @Override
    protected void pingConnection() {
       
    }

    @Override
    public void afterConnect() {
    }

    @Override
    public void EXECUTE(String p_sql, boolean logger, Object[] p_bind_values, boolean direct) {
        throw new UnsupportedOperationException("Unimplemented method 'EXECUTE'");
    }


    @Override
    public String DDL(String owner, String type, String name) {
        String sql = "SHOW CREATE " + type.toUpperCase() + " `" + owner + "`.`" + name + "`";
        try {
            this.cs = con.prepareCall(sql);
            ResultSet rs = this.cs.executeQuery();
            if (rs.next()) {
                ResultSetMetaData md = rs.getMetaData();
                for (int i = 1; i <= md.getColumnCount(); i++) {
                    String col = md.getColumnLabel(i).toUpperCase();
                    if (col.contains("CREATE")) {
                        return rs.getString(i);
                    }
                }
            }
            return null;
        } catch (SQLException e) {
            return e.toString();
        }
    }

    @Override
    public String PROCEDURE(String obj) {
        return "Unimplemented method 'PROCEDURE'";
    }


    @Override
    public String EXPLAIN(String p_sql) {
        String sql = "EXPLAIN ANALYZE " + p_sql;
        String ret = "";

        try {
            PreparedStatement ps = con.prepareStatement(sql);
            ResultSet rs = ps.executeQuery();
            while (rs.next()) {
                ret = rs.getString(1);
            }
            ps.close();
        } catch(Exception e) {
        }
        return ret;
    }


    @Override
    public String DESCRIBE(String p_object_name) {
        return "Unimplemented method 'DESCRIBE'";
    }

    @Override
    public void TREE_OBJECTS() {
    }

    
}
