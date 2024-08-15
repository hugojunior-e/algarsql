import lib.d_editor_find as d_editor_find
import re
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class form(QDialog):
    def __init__(self):
        super(form, self).__init__()
        self.ui = d_editor_find.Ui_d_editor_find()
        self.setFixedSize(430,200)
        self.ui.setupUi(self)
        self.ui.bt_find.clicked.connect( self.find )
        self.ui.bt_find_next.clicked.connect( self.select )
        self.ui.bt_replace.clicked.connect( self.replace )
        self.ui.bt_replace_all.clicked.connect( self.replace_all )
        self.editor     = None
        self.locates    = []
        self.select_idx = 0        

    def showFindReplace(self, editor):
        self.editor     = editor
        self.locates    = []
        self.select_idx = 0
        self.ui.edt_text.setText( editor.textCursor().selectedText() )
        self.show()

    def select(self):
        if len(self.locates) == 0 or self.select_idx == len(self.locates):
            QMessageBox.about(None, "Message", "no occurrence found")
            return False
        cursor = self.editor.textCursor()
        cursor.setPosition( self.locates[self.select_idx].start())
        cursor.setPosition( self.locates[self.select_idx].start() + len(self.ui.edt_text.text()) , QTextCursor.KeepAnchor)
        self.editor.setTextCursor(cursor)
        self.select_idx = self.select_idx + 1
        return True

    def find(self):
        flags    = re.IGNORECASE
        txt_full = self.editor.toPlainText()
        txt_find = re.escape(self.ui.edt_text.text())

        if self.ui.chk_match_case.isChecked():
            flags=0

        if self.ui.chk_match_whole_word.isChecked():
            txt_find = r"\b" + txt_find + r"\b"

        p               = re.compile( txt_find ,flags=flags)
        self.locates    = [ ii for ii in p.finditer(txt_full) ]
        self.select_idx = 0
        if len(self.locates) > 0:
            self.select()

    def replace(self):
        self.find()
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            cursor.insertText(self.ui.edt_replace.text())
            
    def replace_all(self):
        while True:
            self.find()
            cursor = self.editor.textCursor()
            if cursor.hasSelection():
                cursor.insertText(self.ui.edt_replace.text())
            else:
                break