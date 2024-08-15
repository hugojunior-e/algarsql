import lib.d_editor_form as d_editor_form
import dm

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from datetime import datetime

class form(QDialog):
    def __init__(self):
        super(form, self).__init__()
        self.ui = d_editor_form.Ui_d_editor_form()
        self.ui.setupUi(self)
        self.ui.bt_salvar.clicked.connect(self.bt_salvar_clicked)
        self.ui.grid.doubleClicked.connect(self.grid_doubleclicked)
        self.ui.mem_grid.setFont(dm.fontSQL)
        self.ui.grid.verticalHeader().setDefaultSectionSize(20)

    def bt_salvar_clicked(self):
        if self.ui.bt_salvar.text().find("#") >= 0:
            self.ui.grid.show()
            self.ui.mem_grid.hide()
            self.ui.bt_salvar.setText(self.bt_salvar_text)
            rowIndex = self.ui.grid.currentIndex().row().real
            self.ui.grid.item(rowIndex,1).setText( self.ui.mem_grid.toPlainText() )
        
        elif self.ui.bt_salvar.text().find("View") >= 0:
            self.grid_doubleclicked()

        elif self.ui.bt_salvar.text().find("Save") >= 0:
            o_row         = self.grid_orig.currentIndex().row()
            sql_bind_vars = {}

            for x in range( self.ui.grid.rowCount() ):
                fn  = self.ui.grid.item(x,0).text()
                fv  = self.ui.grid.item(x,1).text()
                ft  = self.l_tipos[fn]

                if len(fv) == 0:
                    sql_bind_vars[fn] = None
                elif ft.find("DATE") >= 0:
                    sql_bind_vars[fn] = datetime.strptime(fv, '%d/%m/%Y %H:%M:%S')
                elif ft.find("LOB") >= 0:
                    sql_bind_vars[fn] = self.db.create_lob(fv,"BLOB" in ft)
                else:
                    sql_bind_vars[fn] = fv

            SQL_UPDATE_AUX = "UPDATE (" + self.sql + ") SET " + (",".join([ x + " = :" + x for x in sql_bind_vars.keys() ])) + " WHERE ROWID='" + self.rowid + "'" 

            self.db.executeSQL(p_sql=SQL_UPDATE_AUX, p_tipo='EXEC', p_bind_values=sql_bind_vars)
            
            if self.db.status_code == 0:
                o_col = 0
                for x in range( self.grid_orig.columnCount() ):
                    if self.grid_orig.horizontalHeaderItem(x).text() != "ROWID":
                        x_value = self.ui.grid.item(o_col,1).text()
                        self.grid_orig.item(o_row, x).setText( x_value )
                        o_col   = o_col + 1
                dm.f_principal.pc_editor_tabchange()

            QMessageBox.about(self, "Message", self.db.status_msg )   

    def grid_doubleclicked(self):
        if self.ui.grid.currentIndex().column().real == 0:
            rowIndex = self.ui.grid.currentIndex().row()
            self.ui.mem_grid.setPlainText( self.ui.grid.item(rowIndex,1).text() )
            self.ui.grid.hide()
            self.ui.mem_grid.show()
            self.ui.bt_salvar.setText("#")



    def showForm(self, grid_orig, db):
        rowIndex              = grid_orig.currentIndex().row()
        self.grid_orig        = grid_orig
        self.db               = db
        self.sql              = ""
        self.bt_salvar_text   = "View"
        self.l_tipos          = {}
        self.ui.grid.show()
        self.ui.mem_grid.hide()
        

        t = []
        for x in range( grid_orig.columnCount() ):
            self.l_tipos[ grid_orig.col_names[x] ] = grid_orig.col_types[x]

            if grid_orig.horizontalHeaderItem(x).text() == 'ROWID':
                self.bt_salvar_text   = "Save"
                self.rowid            = grid_orig.item(rowIndex,x).text()
                self.sql              = db._sql
            else:
                t.append( [ grid_orig.horizontalHeaderItem(x).text() ,  grid_orig.item(rowIndex,x).text()  ] )

        dm.populateGrid( self.ui.grid, t, editableColumns="-1-" )
        self.ui.bt_salvar.setText(self.bt_salvar_text)
        self.show()
