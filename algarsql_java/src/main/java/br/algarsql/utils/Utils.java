package br.algarsql.utils;

import java.io.File;
import java.nio.file.Paths;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import org.springframework.web.util.HtmlUtils;
import oracle.dbtools.app.Format.Breaks;
import oracle.dbtools.app.Format.BreaksX2;
import oracle.dbtools.app.Format.FlowControl;
import oracle.dbtools.app.Format.InlineComments;
import java.sql.Statement;

import java.text.SimpleDateFormat;

import java.util.ArrayList;
import java.util.Date;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import java.util.regex.Matcher;
import java.util.regex.Pattern;


import oracle.dbtools.app.Format;
import oracle.dbtools.app.Format.Case;
import oracle.dbtools.app.Format.Space;

public class Utils {



    public static String formatCode(String code) {
        try {
            Format format = new Format();
            format.options.put("singleLineComments", InlineComments.CommentsUnchanged);
            format.options.put("kwCase", Case.UPPER);
            format.options.put("idCase", Case.NoCaseChange);
            format.options.put("adjustCaseOnly", false);
            format.options.put("formatThreshold", 1);
            format.options.put("alignTabColAliases", false);
            format.options.put("alignTypeDecl", true);
            format.options.put("alignNamedArgs", true);
            format.options.put("alignEquality", true);
            format.options.put("alignAssignments", true);
            format.options.put("alignRight", true);
            format.options.put("identSpaces", 2);
            format.options.put("useTab", false);
            format.options.put("breaksComma", Breaks.After);
            format.options.put("breaksProcArgs", false);
            format.options.put("breaksConcat", Breaks.Before);
            format.options.put("breaksAroundLogicalConjunctions", Breaks.Before);
            format.options.put("breaksAfterSelect", false);
            format.options.put("commasPerLine", 0);
            format.options.put("breakOnSubqueries", false);
            format.options.put("breakAnsiiJoin", false);
            format.options.put("breakParenCondition", false);
            format.options.put("maxCharLineSize", 120);
            format.options.put("forceLinebreaksBeforeComment", false);
            format.options.put("extraLinesAfterSignificantStatements", BreaksX2.Keep);
            format.options.put("flowControl", FlowControl.IndentedActions);
            format.options.put("spaceAroundOperators", true);
            format.options.put("spaceAfterCommas", true);
            format.options.put("spaceAroundBrackets", Space.Default);
            return format.format(code);
        } catch (Exception e) {
            return code;
        }
    }


    // ==========================================================================================
    //
    // ==========================================================================================

    public static String[] changePasswordGetUser(String alias, String username) {
        String[] ret = new String[] {"", "", ""};
        try {
            Connection conn =
                    DriverManager.getConnection("jdbc:oracle:thin:@" + Constants.FARMPRD_DSN,
                            Constants.FARMPRD_USR, Constants.FARMPRD_PWD);
            Statement st = conn.createStatement();
            ResultSet rs =
                    st.executeQuery(String.format(Constants.C_CHANGE_PASSWORD_GET_TNS, alias));
            if (!rs.next()) {
                ret[0] = "ERROR: Database entry not found.";
            }
            rs.close();
            String db_tns = rs.getString(1);

            rs = st.executeQuery(String.format(Constants.C_CHANGE_PASSWORD_GET_USER_FOUND, username,
                    username, alias));
            if (!rs.next()) {
                ret[0] = "ERROR: User not found.";
            }
            String userNameFound = rs.getString(2);
            rs.close();

            conn.close();

            ret[1] = userNameFound;
            ret[2] = db_tns;

            conn = DriverManager.getConnection("jdbc:oracle:thin:@" + db_tns, Constants.FARMPRD_USR,
                    Constants.FARMPRD_PWD);
            rs = st.executeQuery(String.format(Constants.C_CHANGE_PASSWOR_GET_USER, userNameFound));
            if (!rs.next()) {
                ret[0] = "ERROR: User " + userNameFound + " does not exist in database " + alias
                        + ".";
            }
            rs.close();

            conn.close();
            ret[0] = "Success Change Password for user " + userNameFound;
        } catch (Exception e) {
            ret[0] = "ERROR: Database error: " + e.getMessage();
        }
        return ret;
    }

    public static String changePassword(String db_tns, String db_user, String db_password) {
        try {
            Connection conn = DriverManager.getConnection("jdbc:oracle:thin:@" + db_tns,
                    Constants.FARMPRD_USR, Constants.FARMPRD_PWD);
            Statement st = conn.createStatement();
            st.execute(String.format(Constants.C_CHANGE_PASSWORD, db_user, db_password));
            conn.close();
            return "Success Change Password for user " + db_user;
        } catch (Exception e) {
            return "Error Change Password for user " + db_user + ": " + e.getMessage();
        }
    }

    // ==========================================================================================
    //
    // ==========================================================================================

    public static String generateFileName(String filename, boolean temp) {

        String data = new SimpleDateFormat("yyyyMMdd_HHmmss_SSS").format(new Date());

        String workspace = Paths.get(Constants.WORKDIR, "workspace").toString();
        String tempDir = Paths.get(Constants.WORKDIR, "workspace", "temp").toString();
        String finalName = filename.replace("[]", data);
        new File(workspace).mkdirs();
        new File(tempDir).mkdirs();

        return Paths.get(temp ? tempDir : workspace, finalName).toString();
    }
    // ==========================================================================================
    //
    // ==========================================================================================

    public static Object configValue(String tag, String[] params, String username) {

        if (params == null) {
            params = new String[] {"%", "%"};
        }

        String fileConfig = generateFileName(username + ".db", false);
        if (!new File(fileConfig).exists()) {
            return "";
        }
        Connection conn;

        try {
            conn = DriverManager.getConnection("jdbc:sqlite:" + fileConfig);
            Statement st = conn.createStatement();
            if ("SQL_HISTORY".equals(tag)) {
                ResultSet rs = st.executeQuery("select * from sql_history " + "where info like '"
                        + params[0] + "' and dbname like '" + params[1] + "' " + "order by 1 desc");

                List<Map<String, String>> rows = new ArrayList<>();

                while (rs.next()) {

                    Map<String, String> row = new LinkedHashMap<>();

                    row.put("dt", rs.getString(1));
                    row.put("dbname", rs.getString(2));
                    row.put("info", rs.getString(3));

                    rows.add(row);
                }

                return rows;
            }

            if ("SQL_TEMPLATES".equals(tag)) {

                ResultSet rs = st.executeQuery("select * from sql_templates where node like '"
                        + params[0] + "' order by node");
                List<Map<String, Object>> rows = new ArrayList<>();
                while (rs.next()) {
                    Map<String, Object> row = new LinkedHashMap<>();
                    row.put("node", rs.getString(1));
                    row.put("info", rs.getString(2));
                    rows.add(row);
                }
                return rows;
            }
            String ret = "";
            ResultSet rs = st.executeQuery("select info from config where node = '" + tag + "'");
            if (rs.next()) {
                ret = rs.getString(1);
            }
            conn.close();

            return ret;
        } catch (Exception e) {
            e.printStackTrace();
            return "";
        }
    }

    // ==========================================================================================
    //
    // ==========================================================================================

    public static void configSave(String tagName, Object tagValue, String tipo, String username) {

        String fileConfig = generateFileName(username + ".db", false);

        try {
            Connection conn = DriverManager.getConnection("jdbc:sqlite:" + fileConfig);
            Statement st = conn.createStatement();

            st.execute("CREATE TABLE if not exists config (node text, info text)");
            st.execute(
                    "CREATE TABLE if not exists sql_history (dt datetime default current_timestamp, dbname text, info text)");
            st.execute("CREATE TABLE if not exists sql_templates(node text unique, info text)");

            // -------------------------------------------------------------
            // CONFIG
            // -------------------------------------------------------------

            if ("CONFIG".equals(tipo)) {
                st.execute("delete from config where node = '" + tagName + "'");
                PreparedStatement ps =
                        conn.prepareStatement("insert into config (node,info) values (?,?)");
                ps.setString(1, tagName);
                ps.setString(2, String.valueOf(tagValue));
                ps.execute();
            }

            // -------------------------------------------------------------
            // SQL_HISTORY
            // -------------------------------------------------------------

            if ("SQL_HISTORY".equals(tipo)) {
                PreparedStatement ps =
                        conn.prepareStatement("insert into sql_history (dbname,info) values (?,?)");
                ps.setString(1, tagName);
                ps.setString(2, String.valueOf(tagValue));
                ps.execute();
            }

            // -------------------------------------------------------------
            // SQL_TEMPLATES
            // -------------------------------------------------------------

            if ("SQL_TEMPLATES".equals(tipo)) {
                Map<?, ?> obj = (Map<?, ?>) tagValue;
                st.execute("delete from sql_templates  where node = '" + tagName + "'");
                PreparedStatement ps =
                        conn.prepareStatement("insert into sql_templates (node,info) values (?,?)");
                ps.setString(1, String.valueOf(obj.get("node")));
                ps.setString(2, String.valueOf(obj.get("info")));
                ps.execute();
            }
            conn.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    // ==========================================================================================
    //
    // ==========================================================================================

    public static SQLCodeType tipoSQL(String sql) {
        SQLCodeType ret = new SQLCodeType();
        String x = sql.toUpperCase() + "\n";
        x = x.replaceAll("--.*", "");
        x = x.replaceAll("/\\*.*?\\*/", "");
        if (x.trim().startsWith("CREATE")) {
            Pattern pattern = Pattern.compile("""
                    CREATE\\s+
                    (?:OR\\s+REPLACE\\s+)?
                    (?:EDITIONABLE\\s+|NONEDITIONABLE\\s+)?

                    (PACKAGE\\s+BODY|PACKAGE|FUNCTION|PROCEDURE|SEQUENCE|VIEW)
                    \\s+

                    (?:
                        "?(?<schema>[^\\s".]+)"?\\.
                    )?

                    "?(?<objeto>[^\\s"(]+)"?
                    """, Pattern.CASE_INSENSITIVE | Pattern.DOTALL | Pattern.COMMENTS);

            Matcher match = pattern.matcher(sql);

            if (match.find()) {
                ret.object_type = match.group(1).toUpperCase();
                ret.object_name = match.group("objeto");
                ret.object_owner = match.group("schema");
            }

            ret.sql_type = 3;
        }

        else if (x.trim().startsWith("SELECT") || x.trim().startsWith("WITH")) {

            ret.sql_type = 1;
        } else {
            ret.sql_type = 2;
        }

        return ret;
    }


    // ==========================================================================================
    //
    // ==========================================================================================

    public static String htmlTable(List<String> headers, List<Map<String, Object>> rows) {

        StringBuilder html = new StringBuilder();

        html.append("<table>");
        html.append("<tr>");

        // HEADER
        for (String h : headers) {
            html.append("<th>").append(HtmlUtils.htmlEscape(String.valueOf(h))).append("</th>");
        }
        html.append("</tr>");

        // ROWS
        for (Map<String, Object> row : rows) {
            html.append("<tr>");
            for (String h : headers) {
                Object value = row.get(h);
                html.append("<td>")
                        .append(HtmlUtils.htmlEscape(value == null ? "" : String.valueOf(value)))
                        .append("</td>");
            }
            html.append("</tr>");
        }
        html.append("</table>");
        return html.toString();
    }

    // ==========================================================================================
    //
    // ==========================================================================================

    public static String compactSQL(String sql) {
        if (sql == null) {
            return null;
        }

        sql = sql.trim();

        if (sql.endsWith(";")) {
            sql = sql.substring(0, sql.length() - 1);
        }

        return sql;
    }
}


