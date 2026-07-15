package br.algarsql.utils;

import java.io.File;
import java.io.FileOutputStream;
import java.io.FileWriter;
import java.sql.Blob;
import java.sql.Clob;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
import java.sql.Statement;
import java.sql.Types;
import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import org.apache.poi.ss.usermodel.Row;
import org.apache.poi.ss.usermodel.Sheet;
import org.apache.poi.xssf.streaming.SXSSFWorkbook;

public class ParallelProcess extends Thread {
    private DATABASE db;
    String sql;
    int file_type;
    String file_name;
    String table_name;
    int i_block;
    boolean first_line_titles;
    String csv_data;

    // ==========================================================================================
    //
    // ==========================================================================================

    public ParallelProcess(int i_block, DATABASE db, String sql, int file_type, String table_name) {
        this.i_block = i_block;
        this.db = db;
        this.sql = sql;
        this.file_type = file_type;
        this.table_name = table_name;
        db.status_code_parallel = 1;
    }

    public ParallelProcess(int i_block, DATABASE db, String sql, boolean first_line_titles,
            String csv_data, String file_name) {
        this.i_block = i_block;
        this.db = db;
        this.sql = sql;
        this.first_line_titles = first_line_titles;
        this.csv_data = csv_data;
        this.file_name = file_name;
        db.status_code_parallel = 1;
    }

    public ParallelProcess(int i_block, DATABASE db, String sql) {
        this.i_block = i_block;
        this.db = db;
        this.sql = sql;
        db.status_code_parallel = 1;
    }    

    // ==========================================================================================
    //
    // ==========================================================================================

    private void csvCompleter() {
        String[] lines = csv_data.split("\n");
        String f_saved_download = "[]-" + file_name + ".completed";
        String fsaved = Utils.generateFileName(f_saved_download, true);

        try (FileWriter fw = new FileWriter(fsaved)) {
            for (int i = 0; i < lines.length; i++) {

                if (i == 0 && first_line_titles) {
                    continue;
                }

                String line = lines[i].trim();

                String[] records = line.split(";");
                String sql_aux = sql;

                for (int reg = 0; reg < records.length; reg++) {
                    sql_aux = sql_aux.replace("<" + reg + ">", records[reg].trim());
                }

                db.executeSelect(sql_aux, false, -2);
                if (db.status_code != 0) {
                    db.status_msg =
                            "ERROR: Executing SQL for line " + (i + 1) + ": " + db.status_msg;
                    return;
                }
                ResultSetMetaData meta = db.rs.getMetaData();
                if (db.rs.next()) {
                    for (int idx = 1; idx <= meta.getColumnCount(); idx++) {
                        String value = db.rs.getString(idx);
                        line += ";" + value;
                    }
                    fw.write(line + "\n");
                }
                db.rs.close();

                db.status_msg = "Process Record " + (i + 1) + "....";
            }

            String ffp = new File(fsaved).getName();
            db.status_msg = "<a style=\"cursor: pointer;\" onclick=\"js_download('" + ffp
                    + "')\"> download file </a>";
        } catch (Exception e) {
            db.status_msg = "ERROR: Exporting data...." + e.getMessage();
        }
    }


    // ==========================================================================================
    //
    // ==========================================================================================

    private String toSQLiteType(int jdbcType) {

        switch (jdbcType) {

            case Types.INTEGER:
            case Types.SMALLINT:
            case Types.TINYINT:
            case Types.BIGINT:
                return "INTEGER";

            case Types.FLOAT:
            case Types.REAL:
            case Types.DOUBLE:
            case Types.NUMERIC:
            case Types.DECIMAL:
                return "REAL";

            case Types.DATE:
            case Types.TIME:
            case Types.TIMESTAMP:
                return "TEXT";

            case Types.BLOB:
            case Types.BINARY:
            case Types.VARBINARY:
            case Types.LONGVARBINARY:
                return "BLOB";

            default:
                return "TEXT";
        }
    }


    // ==========================================================================================
    //
    // ==========================================================================================

    private void exportToFile() {
        String[] l_filenames = new String[] {"exported_to_insert.sql", "exported.csv",
                "exported.xlsx", "database.db"};
        db.status_msg = "Exporting data....";

        try {
            db.executeSelect(sql, false, -2);

            if (db.status_code != 0) {
                return;
            }
            String file_path = Utils.generateFileName("[]-" + l_filenames[file_type], true);
            int qtd = 0;

            ResultSetMetaData meta = db.rs.getMetaData();
            int colCount = meta.getColumnCount();

            // --
            // -- INSERT SCRIPT
            // --

            if (file_type == 0) {
                String s_insert_title = " INSERT INTO " + table_name + " ("
                        + String.join(", ", db.col_names) + ") VALUES (%s)";
                FileWriter fw = new FileWriter(file_path);
                while (db.rs.next()) {
                    List<String> values = new ArrayList<>();
                    for (int i = 1; i <= db.rs.getMetaData().getColumnCount(); i++) {
                        values.add(db.value(db.rs.getObject(i)));
                    }
                    String s_insert = String.format(s_insert_title, String.join(", ", values));

                    fw.write(s_insert + ";\n");
                    qtd++;
                    db.status_msg = "Exporting data.... " + qtd + " records exported.";
                }
                fw.close();
            }

            // --
            // -- CSV SCRIPT
            // --

            if (file_type == 1) {
                FileWriter fw = new FileWriter(file_path);


                for (int i = 1; i <= colCount; i++) {
                    fw.write(meta.getColumnLabel(i) + ";");
                }
                fw.write("\n");

                while (db.rs.next()) {
                    List<String> values = new ArrayList<>();
                    for (int i = 1; i <= db.rs.getMetaData().getColumnCount(); i++) {
                        values.add("\"" + db.value(db.rs.getObject(i)) + "\"");
                    }
                    String s_insert = String.join(";", values);
                    fw.write(s_insert + ";\n");
                    qtd++;
                    db.status_msg = "Exporting data.... " + qtd + " records exported.";
                }
                fw.close();
            }

            // --
            // -- EXCEL SCRIPT
            // --

            if (file_type == 2) {
                SXSSFWorkbook workbook = new SXSSFWorkbook(100);
                workbook.setCompressTempFiles(true); // comprime os arquivos temporários
                Sheet sheet = workbook.createSheet("Dados");
                int rowNum = 0;
                Row header = sheet.createRow(rowNum++);
                for (int i = 1; i <= colCount; i++) {
                    header.createCell(i - 1).setCellValue(meta.getColumnLabel(i));
                }
                qtd = 0;
                while (db.rs.next()) {
                    Row row = sheet.createRow(rowNum++);
                    for (int i = 1; i <= colCount; i++) {
                        String value = db.rs.getString(i);
                        row.createCell(i - 1).setCellValue(value == null ? "" : value);
                    }
                    qtd++;
                    db.status_msg = "Exporting data.... " + qtd + " records exported.";
                    // Opcional: força descarte das linhas antigas
                    if (qtd % 1000 == 0) {
                        ((org.apache.poi.xssf.streaming.SXSSFSheet) sheet).flushRows(100);
                    }
                }
                try (FileOutputStream fos = new FileOutputStream(file_path)) {
                    workbook.write(fos);
                }
                // Remove os arquivos temporários
                workbook.dispose();
                workbook.close();
            }

            // --
            // -- SQLITE SCRIPT
            // --

            if (file_type == 3) {
                Class.forName("org.sqlite.JDBC");
                file_path = Utils.generateFileName( db.username.toLowerCase() + "_" + l_filenames[file_type], true);

                Connection sqlite = DriverManager.getConnection("jdbc:sqlite:" + file_path);
                Statement st = sqlite.createStatement();
                st.executeUpdate("DROP TABLE IF EXISTS dados");

                // Cria tabela
                StringBuilder create = new StringBuilder();
                create.append("CREATE TABLE dados(");

                for (int i = 1; i <= colCount; i++) {
                    if (i > 1)
                        create.append(",");
                    create.append("\"").append(meta.getColumnLabel(i)).append("\" ")
                            .append(toSQLiteType(meta.getColumnType(i)));
                }
                create.append(")");
                st.executeUpdate(create.toString());

                // INSERT
                StringBuilder insert = new StringBuilder();
                insert.append("INSERT INTO dados VALUES(");
                for (int i = 1; i <= colCount; i++) {
                    if (i > 1)
                        insert.append(",");
                    insert.append("?");
                }
                insert.append(")");
                PreparedStatement ps = sqlite.prepareStatement(insert.toString());
                sqlite.setAutoCommit(false);
                while (db.rs.next()) {
                    for (int i = 1; i <= colCount; i++) {
                        Object value = db.rs.getObject(i);

                        if ( value == null ) {
                            value = "";
                            
                        } else if (meta.getColumnTypeName(i).toUpperCase().contains("LOB")) {
                            if (value instanceof Clob) {
                                Clob clob = (Clob) value;
                                value = clob.getSubString(1, (int) clob.length());
                            } else if (value instanceof Blob) {
                                Blob blob = (Blob) value;
                                value = new String(blob.getBytes(1, (int) blob.length()));
                            }
                        } else if (value instanceof java.sql.Timestamp || value instanceof java.sql.Date || value instanceof java.util.Date) {
                            value = db.sdf.format(value); 
                        } else {
                            value = value.toString();
                        }
                        ps.setString(i, value.toString());
                    }
                    ps.addBatch();
                    qtd++;
                    db.status_msg = "Exporting data.... " + qtd + " records exported.";
                }
                ps.executeBatch();
                sqlite.commit();
                ps.close();
                st.close();
                sqlite.close();
            }

            if (file_type == 3) {
                db.status_msg = "Data exported successfully!";
            } else {
                String ffp = new File(file_path).getName();
                db.status_msg = "<a style=\"cursor: pointer;\" onclick=\"js_download('" + ffp  + "')\"> download file </a>";
            }
        } catch (Exception e) {
            db.status_msg = "ERROR: Exporting data...." + e.getMessage();
        }
    }


    public void inputFromDatabase() {
        try{
            String sqlInsert = this.sql;
            List<String> tags = new ArrayList<>();
            Pattern p = Pattern.compile("<([^>]+)>");
            Matcher m = p.matcher(sqlInsert);
            while (m.find()) {
                tags.add(m.group(1));
            }        
            String sqlPreparada = sqlInsert.replaceAll("<[^>]+>", "?");
            String db_file = Utils.generateFileName(db.username.toLowerCase() + "_database.db", true);
            Connection conn2 = DriverManager.getConnection("jdbc:sqlite:" + db_file);
            Statement st2 = conn2.createStatement();
            ResultSet rs2 = st2.executeQuery("SELECT * FROM dados");

            java.sql.PreparedStatement ps = db.con.prepareStatement(sqlPreparada);
            int batchSize = 1000;
            int count = 0;
            while (rs2.next()) {
                int idx = 1;
                for ( String n: tags ) {
                    ps.setObject(idx, rs2.getObject(n));
                    idx++;
                }
                ps.addBatch();
                count++;
                if (count % batchSize == 0) {
                    ps.executeBatch();
                    ps.clearBatch();
                    ps = db.con.prepareStatement(sqlPreparada);
                }
                db.status_msg = "Imported " + count + " records.";
            }
            ps.executeBatch();
            ps.close();
            
            rs2.close();
            st2.close();
            conn2.close();        
            db.status_msg = "Data imported successfully!";
        } catch (Exception e) {
            db.status_msg = "ERROR: Importing data...." + e.getMessage();
        }
    }


    @Override
    public void run() {
        if (i_block == 0) {
            exportToFile();
        } else if (i_block == 1) {
            csvCompleter();
        } else if (i_block == 4) {
            inputFromDatabase();
        }
        db.status_code_parallel = 0;
    }
}
