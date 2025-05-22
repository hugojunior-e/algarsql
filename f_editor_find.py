import ui.d_editor_find as d_editor_find
import re
import dm
from PyQt5.QtWidgets import QDialog

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
        self.ui.edt_text.setText( editor.selectedText() )
        self.show()

    def select(self):
        if len(self.locates) == 0 or self.select_idx == len(self.locates):
            dm.messageBox("no occurrence found")
            return False
        x = self.locates[self.select_idx].start()
        self.editor.setPosition(x)
        self.editor.setPositionSel(x + len(self.ui.edt_text.text()))

        self.select_idx = self.select_idx + 1
        return True

    def find(self):
        flags    = re.IGNORECASE
        txt_full = self.editor.text()
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
        if self.editor.hasSelectedText():
            self.editor.replaceSelectedText(self.ui.edt_replace.text())
            
    def replace_all(self):
        while True:
            self.find()
            if self.editor.hasSelectedText():
                self.editor.replaceSelectedText(self.ui.edt_replace.text())
            else:
                break