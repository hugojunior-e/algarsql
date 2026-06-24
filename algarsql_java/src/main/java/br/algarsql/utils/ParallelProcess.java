package br.algarsql.utils;

import java.io.File;
import java.io.FileOutputStream;
import java.io.FileWriter;
import java.sql.ResultSetMetaData;
import java.util.ArrayList;
import java.util.List;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;
import org.apache.poi.ss.usermodel.Row;
import org.apache.poi.ss.usermodel.Sheet;

public class ParallelProcess extends Thread {
    private ORACLE db;
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

    public ParallelProcess(int i_block, ORACLE db, String sql, int file_type, String table_name) {
        this.i_block = i_block;
        this.db = db;
        this.sql = sql;
        this.file_type = file_type;
        this.table_name = table_name;
        db.status_code_parallel = 1;
    }

    public ParallelProcess(int i_block, ORACLE db, String sql, boolean first_line_titles,
            String csv_data, String file_name) {
        this.i_block = i_block;
        this.db = db;
        this.sql = sql;
        this.first_line_titles = first_line_titles;
        this.csv_data = csv_data;
        this.file_name = file_name;
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

                db.SELECT(sql_aux, false, false, -2);
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

    private void exportToFile() {
        String[] l_filenames =
                new String[] {"exported_to_insert.sql", "exported.csv", "exported.xlsx"};
        db.status_msg = "Exporting data....";

        try {
            db.SELECT(sql, false, false, -2);

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
                    fw.write(meta.getColumnName(i) + ";");
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
                XSSFWorkbook workbook = new XSSFWorkbook();
                Sheet sheet = workbook.createSheet("Dados");
                int rowNum = 0;

                Row header = sheet.createRow(rowNum++);
                for (int i = 1; i <= colCount; i++) {
                    header.createCell(i - 1).setCellValue(meta.getColumnName(i));
                }

                for (int i = 0; i < colCount; i++) {
                    sheet.autoSizeColumn(i);
                }

                while (db.rs.next()) {
                    Row row = sheet.createRow(rowNum++);
                    for (int i = 1; i <= colCount; i++) {
                        String value = db.rs.getString(i);
                        row.createCell(i - 1).setCellValue(value == null ? "" : value);
                    }
                }

                FileOutputStream fos = new FileOutputStream(file_path);
                workbook.write(fos);
                fos.close();
                workbook.close();
            }

            String ffp = new File(file_path).getName();
            db.status_msg = "<a style=\"cursor: pointer;\" onclick=\"js_download('" + ffp
                    + "')\"> download file </a>";

        } catch (Exception e) {
            db.status_msg = "ERROR: Exporting data...." + e.getMessage();
        }
    }

    @Override
    public void run() {
        if (i_block == 0) {
            exportToFile();
        } else if (i_block == 1) {
            csvCompleter();
        }
        db.status_code_parallel = 0;
    }
}
