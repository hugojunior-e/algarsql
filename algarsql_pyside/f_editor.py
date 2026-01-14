from ui import d_editor
import dm
import dm_const

from PySide6.QtWidgets import (
    QDialog, QFileDialog, QTableWidgetItem, QTreeWidgetItem
)


class form(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = d_editor.Ui_d_editor()
        self.ui.setupUi(self)

        # Conexões de sinais
        self.ui.bt_sessions_exec.clicked.connect(self.bt_sessions_exec_click)
        self.ui.edt_objetos.textEdited.connect(self.edt_objetos_edited)
        self.ui.bt_csv_of.clicked.connect(self.bt_csv_of_clicked)
        self.ui.bt_explain.clicked.connect(self.bt_explain_clicked)
        self.ui.bt_csv_populate.clicked.connect(self.bt_csv_populate_edited)
        self.ui.bt_cfg_salvar.clicked.connect(self.bt_cfg_salvar_clicked)
        self.ui.bt_obj_viewcode.clicked.connect(self.bt_obj_viewcode_clicked)

        # Inicialização de componentes
        self.ui.tree_explain.setColumnCount(7)
        self.ui.tree_explain.setHeaderLabels(["#", "Owner", "Name", "Type", "Cost", "Cardinality", "Bytes"])
        self.ui.grid_csv.setColumnCount(1)
        self.ui.grid_csv.setColumnWidth(0, 200)
        self.ui.grid_csv.setHorizontalHeaderLabels(('Field Name/Value', '-'))
        self.ui.grid_objetos.verticalHeader().setDefaultSectionSize(20)

        self.ui.edt_recall.textEdited.connect(self.edt_recall_edited)
        self.ui.edt_recall_database.textEdited.connect(self.edt_recall_edited)

        self.lista_chk_obj = [
            self.ui.chk_obj_table, self.ui.chk_obj_view, self.ui.chk_obj_trigger,
            self.ui.chk_obj_package, self.ui.chk_obj_procedure,
            self.ui.chk_obj_funcion, self.ui.chk_obj_sequence
        ]
        for x in self.lista_chk_obj:
            x.clicked.connect(self.edt_objetos_edited)

        self.ui.grid_recall.currentItemChanged.connect(
            lambda a, b: self.ui.mem_recall.setPlainText(a.text() if a else "")
        )

        self.ui.tree_sessions.itemSelectionChanged.connect(
            lambda: self.ui.mem_sessions.setPlainText(
                self.ui.tree_sessions.currentItem().text(8)
                if self.ui.tree_sessions.currentItem() else ""
            )
        )

        for i in range(self.ui.tabWidget.count()):
            self.ui.tabWidget.setTabVisible(i, False)

    # ==============================================================================================
    # mostra o formulário
    # ==============================================================================================
    def showForm(self, formName, info):
        if formName == "Editor":
            self.ui.mem_editor.setPlainText(info)
            self.ui.tabWidget.setCurrentWidget(self.ui.tab_editor)
        elif formName == "Recall SQL":
            self.ui.tabWidget.setCurrentWidget(self.ui.tab_recall)
            self.edt_recall_edited()
        elif formName == "View Sessions":
            self.ui.tree_sessions.clear()
            self.ui.tabWidget.setCurrentWidget(self.ui.tab_session)
        elif formName == "Find Objects":
            self.ui.tabWidget.setCurrentWidget(self.ui.tab_find_objects)
        elif formName == "Explain Query":
            self.ui.tree_explain.clear()
            self.ui.tabWidget.setCurrentWidget(self.ui.tab_explain)
            self.ui.mem_explain.setPlainText(info)
        elif formName == "CSV Updater":
            self.ui.mem_csv.setPlainText(dm.configValue("csv_sql"))
            self.ui.tabWidget.setCurrentWidget(self.ui.tab_csv_updater)
        elif formName == "Config Tools":
            self.ui.tabWidget.setCurrentWidget(self.ui.tab_config)
            self.ui.mem_cfg_tns.setPlainText(dm.configValue(tag="tns"))
            self.ui.mem_cfg_tns_saved.setPlainText(dm.configValue(tag="tnsSaved"))
            self.ui.edt_cfg_oracle_dir.setText(dm.configValue(tag="OracleInstantClientDir"))
            self.ui.edt_cfg_output_dir.setText(dm.configValue(tag="output_dir"))
            self.ui.edt_cfg_template_dir.setText(dm.configValue(tag="template_dir"))
            self.ui.chk_cfg_run_user.setChecked(dm.configValue(tag="cfg_run_user_pref") == "1")
        self.show()

    # ==============================================================================================
    # tab de configurações
    # ==============================================================================================
    def bt_cfg_salvar_clicked(self):
        dm.configSave("tns", self.ui.mem_cfg_tns.toPlainText(), "CONFIG")
        dm.configSave("tnsSaved", self.ui.mem_cfg_tns_saved.toPlainText(), "CONFIG")
        dm.configSave("OracleInstantClientDir", self.ui.edt_cfg_oracle_dir.text(), "CONFIG")
        dm.configSave("template_dir", self.ui.edt_cfg_template_dir.text(), "CONFIG")
        dm.configSave("output_dir", self.ui.edt_cfg_output_dir.text(), "CONFIG")
        dm.configSave("cfg_run_user_pref", "1" if self.ui.chk_cfg_run_user.isChecked() else "0", "CONFIG")
        dm.f_logon.reload_conf = True
        dm.messageBox("Configs Saved Successfully")

    # ==============================================================================================
    # tab atualizador CSV
    # ==============================================================================================
    def bt_csv_populate_thread(self):
        new_file = self.ui.edt_csv_file.text().replace(".csv", "_newdata.csv")
        sql = self.ui.mem_csv.toPlainText()
        i_start = 1 if self.ui.chk_csv.isChecked() else 0
        linhas = dm.loadFromFile(self.ui.edt_csv_file.text())[i_start:]
        dados_insert = []
        i_tipo_sql = dm.tipoSQL(sql)

        if i_tipo_sql == 1:
            r = open(new_file, 'w')

        for i_linha, s_linha in enumerate(linhas):
            if not self.bt.isVisible():
                break

            if i_tipo_sql == 1:  # SELECT
                if i_linha % 50 == 0:
                    self.bt.setText(f"processed line {i_linha}")

                sql_temp = sql
                a_linha = s_linha.strip().split(";")
                for i, v in enumerate(a_linha):
                    sql_temp = sql_temp.replace(f"<{i + 1}>", v)

                dm.db.SELECT(p_sql=sql_temp, direct=True, fetchSize=1)
                if dm.db.status_code == 0:
                    if len(dm.db.col_data) > 0:
                        retorno = dm.db.col_data[0]
                        r.write(s_linha.strip() + ";" + ";".join([str(i) for i in retorno]) + "\n")
                    else:
                        r.write(s_linha.strip() + ";\n")
                else:
                    self.bt.setText(dm.db.status_msg)
                    return 0
            else:  # UPDATE, INSERT, DELETE
                dados_insert.append(tuple(s_linha.split(";")))

                if i_linha % 5000 == 0 or i_linha == (len(linhas) - 1):
                    self.bt.setText(f"processed line {i_linha}")
                    dm.db.EXECUTE(p_sql=sql, direct=True, p_bind_values=dados_insert, p_many=True)
                    if dm.db.status_code == 0:
                        dm.db.commit()
                    else:
                        self.bt.setText(dm.db.status_msg)
                        return 0
                    dados_insert = []

        self.bt.setText(f"Finished {i_linha} records")

        if i_tipo_sql == 1:
            r.close()

    def bt_csv_populate_edited(self):
        dm.configSave("csv_sql", self.ui.mem_csv.toPlainText(), "CONFIG")
        if len(self.ui.edt_csv_file.text().strip()) == 0:
            dm.messageBox("Filename Required")
            return

        self.bt = dm.createButtonWork()
        self.th = dm.WORKER(proc_run=self.bt_csv_populate_thread)

    def bt_csv_of_clicked(self):
        fileName, _ = QFileDialog.getOpenFileName(
            self, "Open File", "", "CSV Files (*.csv);;All Files (*)",
            options=QFileDialog.Option.DontUseNativeDialog
        )
        if fileName:
            self.ui.grid_csv.setRowCount(0)
            self.ui.edt_csv_file.setText(fileName)
            x = dm.loadFromFile(fileName)[0]
            for i, reg in enumerate(x.split(";")):
                self.ui.grid_csv.insertRow(i)
                self.ui.grid_csv.setItem(i, 0, QTableWidgetItem(reg))

    # ==============================================================================================
    # tab EXPLAIN de querys
    # ==============================================================================================
    def bt_explain_clicked(self):
        self.ui.tree_explain.clear()
        nos = [None for _ in range(5000)]
        dm.db.EXPLAIN(p_sql=self.ui.mem_explain.toPlainText())
        if dm.db.status_code == 0:
            for reg in dm.db.cur.fetchall():
                id = reg[0]
                parent_id = reg[1]
                item_data = [str(r) for r in reg[2:9]]

                if parent_id == -1:
                    l1 = QTreeWidgetItem(item_data)
                    self.ui.tree_explain.addTopLevelItem(l1)
                    nos[id] = l1
                else:
                    ll = QTreeWidgetItem(item_data)
                    nos[parent_id].addChild(ll)
                    nos[id] = ll

            self.ui.tree_explain.expandAll()
            for i in range(8):
                self.ui.tree_explain.setColumnWidth(i, 200)
        else:
            dm.messageBox(dm.db.status_msg)

    # ==============================================================================================
    # tab FIND de objetos
    # ==============================================================================================
    def bt_obj_viewcode_clicked(self):
        y = self.ui.grid_objetos.currentRow()
        self.close()
        dm.f_principal.extrai_ddl(
            self.ui.grid_objetos.item(y, 0).text(),
            self.ui.grid_objetos.item(y, 5).text(),
            self.ui.grid_objetos.item(y, 1).text()
        )

    def edt_objetos_edited(self):
        if not dm.db.prepare():
            return

        self.ui.grid_objetos.setRowCount(0)
        ot = ["'" + x.text() + "'" if x.isChecked() else "'-'" for x in self.lista_chk_obj]
        dm.db.SELECT(
            p_sql=dm_const.C_SQL_FIND_OBJECT % (self.ui.edt_objetos.text(), ",".join(ot)),
            fetchSize=0
        )
        if dm.db.status_code == 0:
            dm.populateGrid(
                grid=self.ui.grid_objetos,
                data=dm.db.col_data,
                columnNames=dm.db.col_names,
                columnTypes=dm.db.col_types
            )
        else:
            dm.messageBox(dm.db.status_msg)

    # ==============================================================================================
    # tab RECALL
    # ==============================================================================================
    def edt_recall_edited(self):
        params = [self.ui.edt_recall.text(), self.ui.edt_recall_database.text()]
        dm.populateGrid(self.ui.grid_recall, dm.configValue(tag="*recall", params=params))

    # ==============================================================================================
    # tab SESSIONS do banco
    # ==============================================================================================
    def bt_sessions_exec_click(self):
        dm.db.SELECT(p_sql=dm.db.sql_session.replace("<WHERE>", self.ui.cbo_sessions.currentText()), fetchSize=0)
        if dm.db.status_code == 0:
            self.ui.tree_sessions.clear()

            parent_id = "-"
            status = "-"

            self.ui.tree_sessions.setColumnCount(len(dm.db.col_names) - 3)
            for i in range(self.ui.tree_sessions.columnCount()):
                self.ui.tree_sessions.headerItem().setText(i, dm.db.col_names[i + 2])
                self.ui.tree_sessions.setColumnWidth(i, 150)

            for reg in dm.db.col_data:
                if parent_id != reg[0]:
                    pai = QTreeWidgetItem([reg[0]])
                    self.ui.tree_sessions.addTopLevelItem(pai)

                if parent_id + status != reg[0] + reg[1]:
                    meio = QTreeWidgetItem([reg[1]])
                    pai.addChild(meio)

                fim = QTreeWidgetItem([
                    str(reg[2]), str(reg[3]), str(reg[4]), str(reg[5]),
                    str(reg[6]), str(reg[7]), str(reg[8]), str(reg[9]),
                    "" if reg[10] is None else str(reg[10])
                ])
                meio.addChild(fim)
                parent_id = reg[0]
                status = reg[1]
        else:
            dm.messageBox(dm.db.status_msg)
