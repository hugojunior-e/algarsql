package br.algarsql.utils;

public class TDBMySql extends DATABASE {

    @Override
    protected void pingConnection() {
       
    }

    @Override
    public void afterConnect() {
    }

    @Override
    public void STOP() {
        throw new UnsupportedOperationException("Unimplemented method 'STOP'");
    }

    @Override
    public void EXECUTE(String p_sql, boolean logger, Object[] p_bind_values, boolean direct) {
        throw new UnsupportedOperationException("Unimplemented method 'EXECUTE'");
    }


    @Override
    public String DDL(String owner, String type, String name) {
        return "Unimplemented method 'DDL'";
    }

    @Override
    public String PROCEDURE(String obj) {
        return "Unimplemented method 'PROCEDURE'";
    }

    @Override
    public String EXPLAIN(String p_sql) {
        return "Unimplemented method 'EXPLAIN'";
    }

    
}
