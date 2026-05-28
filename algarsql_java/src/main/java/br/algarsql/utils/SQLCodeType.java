package br.algarsql.utils;

public class SQLCodeType {
    public static final int NONE = 0;
    public static final int SELECT = 1;
    public static final int EXECUTE = 2;
    public static final int COMPILE = 3;

    public SQLCodeType() {
        this.sql_type = SELECT;
        this.object_owner = "";
        this.object_name = "";
        this.object_type = "";
    }

    public int sql_type;
    public String object_owner;
    public String object_name;
    public String object_type;
}
