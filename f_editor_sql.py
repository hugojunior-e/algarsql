import dm
import re
from PyQt5.QtWidgets import QPlainTextEdit, QWidget, QTextEdit
from PyQt5.QtGui import QPainter, QTextFormat, QTextCharFormat, QColor, QFont, QSyntaxHighlighter, QTextCursor, QTextOption
from PyQt5.QtCore import QRegExp, Qt, QRect, QSize

C_types = [
    "localtimestamp","nchar","nclob","numeric","smallint","type","xmltype",
    "rowid","real","rownum","xmltable","pls_integer","varying","binary_integer",
    "long","raw","number","varchar","varchar2","clob","integer","char","date","timestamp",
    "decimal","int","blob"
]
C_functions = [
    "current_time","current_timestamp","current_user","row_number","dbms_output",
    "listagg","distinct","chr","utl_file","utl_http","mod","replace","translate","instr",
    "reverse","regexp_instr","regexp_replace","regexp_substr","regexp_count","add_months",
    "lpad","rpad","trunc","to_date","to_char","to_number","nvl","decode","sysdate","count",
    "avg","sum","max","min","case","nvl2","trim","substr","upper","lower","initcap"
]
C_keywords = [
    "absolute","action","add","admin","after","aggregate","alias","all","allocate","alter",
    "and","any","are","array","as","asc","assertion","at","authorization","before","begin",
    "binary","bit","blob","boolean","both","breadth","by","call","cascade","cascaded","case",
    "cast","catalog","character","check","class","close","collate","collation",
    "column","commit","completion","connect","connection","constraint","constraints","constructor",
    "continue","corresponding","create","cross","cube","current","current_date","current_path",
    "current_role","cursor","cycle","data",
    "day","deallocate","dec","declare","default","deferrable","deferred",
    "delete","depth","deref","desc","describe","descriptor","destroy","destructor","deterministic",
    "dictionary","diagnostics","disconnect","domain","double","drop","dynamic","each",
    "else","end","end-exec","equals","escape","every","except","exception","exec","execute","external",
    "false","fetch","first","for","foreign","found","from","free","full","function",
    "general","get","global","go","goto","grant","group","grouping","having","host","hour",
    "identity","if","ignore","immediate","in","indicator","initialize","initially","inner",
    "inout","input","insert","intersect","interval","into","is","isolation",
    "iterate","join","key","language","large","last","lateral","leading","left","less","level",
    "like","limit","local","localtime","locator","map","match","minute","package","body",
    "modifies","modify","module","month","names","national","natural","new",
    "next","no","none","not","null","object","of","off","old","on","only","open",
    "operation","option","or","order","ordinality","out","outer","output","pad","parameter",
    "parameters","partial","path","postfix","precision","prefix","preorder","prepare","preserve",
    "primary","prior","privileges","procedure","public","read","reads","recursive","ref",
    "references","referencing","relative","restrict","result","return","returns","revoke","right",
    "role","rollback","rollup","routine","row","rows","savepoint","schema","scroll","scope","search",
    "second","section","select","sequence","session","session_user","set","sets","size",
    "some","space","specific","specifictype","sql","sqlexception","sqlstate","sqlwarning",
    "start","state","statement","static","structure","system_user","table","temporary","terminate",
    "than","then","time","timestamp","timezone_hour","timezone_minute","to","trailing","transaction",
    "translation","treat","trigger","true","under","union","unique","unknown","unnest","update","usage",
    "user","using","value","values","variable","view","when","whenever","where","with",
    "without","work","write","year","zone","bulk","collect","record","elsif","nested","passing","columns","loop"
] 


############################################################################################

class SQLHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.highlightingRules = []

        self.commentStartExpression = QRegExp(r"/\*")
        self.commentEndExpression = QRegExp(r"\*/")

        self.multiLineCommentFormat = QTextCharFormat()
        self.multiLineCommentFormat.setForeground(QColor("#888888"))
        self.multiLineCommentFormat.setFontItalic(True)

        typesFormat = QTextCharFormat()
        typesFormat.setForeground(QColor("#B5CEA8"))
        for word in C_types:
            pattern = QRegExp(r"\b" + word + r"\b", Qt.CaseInsensitive)
            self.highlightingRules.append((pattern, typesFormat))

        functionFormat = QTextCharFormat()
        functionFormat.setForeground(Qt.magenta)
        for word in C_functions:
            pattern = QRegExp(r"\b" + word + r"\b", Qt.CaseInsensitive)
            self.highlightingRules.append((pattern, functionFormat))


        keywordFormat = QTextCharFormat()
        keywordFormat.setForeground( QColor("#0077aa")  ) 
        for word in C_keywords:
            pattern = QRegExp(r"\b" + word + r"\b", Qt.CaseInsensitive)
            self.highlightingRules.append((pattern, keywordFormat))

        stringFormat = QTextCharFormat()
        stringFormat.setForeground( QColor("#CE9178") ) 
        self.highlightingRules.append((QRegExp(r"'[^']*'"), stringFormat))

        commentFormat = QTextCharFormat()
        commentFormat.setForeground(QColor("#888888"))
        commentFormat.setFontItalic(True)
        self.highlightingRules.append((QRegExp(r"--[^\n]*"), commentFormat))

    def highlightBlock(self, text):
        # Regras comuns (palavras-chave, strings, -- comentários)
        for pattern, fmt in self.highlightingRules:
            index = pattern.indexIn(text)
            while index >= 0:
                length = pattern.matchedLength()
                self.setFormat(index, length, fmt)
                index = pattern.indexIn(text, index + length)

        # Comentário multilinha
        self.setCurrentBlockState(0)

        startIndex = 0
        if self.previousBlockState() != 1:
            startIndex = self.commentStartExpression.indexIn(text)

        while startIndex >= 0:
            endIndex = self.commentEndExpression.indexIn(text, startIndex)
            if endIndex == -1:
                self.setCurrentBlockState(1)
                commentLength = len(text) - startIndex
            else:
                commentLength = endIndex - startIndex + self.commentEndExpression.matchedLength()
            self.setFormat(startIndex, commentLength, self.multiLineCommentFormat)
            startIndex = self.commentStartExpression.indexIn(text, startIndex + commentLength)

############################################################################################


class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self.editor.lineNumberAreaPaintEvent(event)

############################################################################################


class EDITOR_SQL(QPlainTextEdit):
    def __init__(self, text="", customContextMenu=None):
        super().__init__()
        self.lineNumberArea = LineNumberArea(self)
        self.setFont(QFont("Monospace", 10))
        self.setWordWrapMode(QTextOption.NoWrap)
        self.highlighter = SQLHighlighter(self.document())

        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        #self.cursorPositionChanged.connect(self.highlightCurrentLine)
        self.cursorPositionChanged.connect(self.highlightMatchingBrackets)

        self.updateLineNumberAreaWidth(0)
        self.setPlainText(text)
        #self.highlightCurrentLine()
        self.keyCompleterEvent = None
        if customContextMenu:
            self.setContextMenuPolicy(Qt.CustomContextMenu )
            self.customContextMenuRequested.connect(customContextMenu)             

    def lineNumberAreaWidth(self):
        digits = len(str(self.blockCount()))
        return 10 + self.fontMetrics().width('9') * digits

    def setText(self, text):
        return self.setPlainText(text)
    
    def getText(self):
        return self.toPlainText()
    
    def getSelectedText(self):
        x = self.textCursor().selectedText()
        return x.replace('\u2029', '\n')
    
    def replaceSelectedText(self, new_text):
        cursor = self.textCursor()
        cursor.insertText(new_text)
        self.setTextCursor(cursor)

    def highlightMatchingBrackets(self):
        cursor = self.textCursor()
        extraSelections = []

        pos = cursor.position()
        document = self.document()

        if pos > 0:
            char = document.characterAt(pos)
            prev_char = document.characterAt(pos - 1)
        else:
            char = document.characterAt(pos)
            prev_char = ''

        brackets = {'(': ')', ')': '(', '[': ']', ']': '[', '{': '}', '}': '{'}
        direction = {'(': 1, '[': 1, '{': 1, ')': -1, ']': -1, '}': -1}

        match_pos = -1
        open_brackets = '([{'
        close_brackets = ')]}'

        def findMatch(pos, char):
            match = brackets.get(char)
            step = direction[char]
            depth = 1
            while 0 <= pos < document.characterCount():
                c = document.characterAt(pos)
                if c == char:
                    depth += 1
                elif c == match:
                    depth -= 1
                    if depth == 0:
                        return pos
                pos += step
            return -1

        if char in brackets:
            match_pos = findMatch(pos + (1 if direction[char] > 0 else -1), char)
            base_pos = pos
        elif prev_char in brackets:
            match_pos = findMatch(pos - 1 + (1 if direction[prev_char] > 0 else -1), prev_char)
            base_pos = pos - 1
            char = prev_char
        else:
            self.setExtraSelections([])
            return

        if match_pos != -1:
            for p in (base_pos, match_pos):
                match_cursor = self.textCursor()
                match_cursor.setPosition(p)
                match_cursor.movePosition(QTextCursor.NextCharacter, QTextCursor.KeepAnchor)

                selection = QTextEdit.ExtraSelection()
                selection.format.setBackground(QColor("#cceeff"))
                selection.cursor = match_cursor
                extraSelections.append(selection)

        self.setExtraSelections(extraSelections)

    def wordOnCursor(self):
        cursor = self.textCursor()
        cursor.select(QTextCursor.WordUnderCursor)
        return cursor.selectedText()

    def currentPosition(self):
        return self.textCursor().position()

    def setPosition(self, pos):
        cursor = self.textCursor()
        cursor.setPosition(pos)
        self.setTextCursor(cursor)
        self.ensureCursorVisible()

    def setPositionSel(self, pos):
        cursor = self.textCursor()
        cursor.setPosition(pos, QTextCursor.KeepAnchor)
        self.setTextCursor(cursor)
        self.ensureCursorVisible()

    def unselect(self):
        cursor = self.textCursor()
        cursor.clearSelection()
        self.setTextCursor(cursor)

    def cursorRect(self):
        # Retorna a área da posição atual do cursor no editor
        return super().cursorRect()
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))

    def updateLineNumberAreaWidth(self, _):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.lineNumberArea)
        painter.fillRect(event.rect(), QColor(240, 240, 240))

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(blockNumber + 1)
                painter.setPen(Qt.darkGray)
                painter.drawText(0, top, self.lineNumberArea.width() - 2, self.fontMetrics().height(),
                                 Qt.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            blockNumber += 1

    def highlightCurrentLine(self):
        extraSelections = []

        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            lineColor = QColor(232, 242, 254)
            selection.format.setBackground(lineColor)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)

        self.setExtraSelections(extraSelections)

    def keyPressEvent(self, event):
        cursor = self.textCursor()

        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            cursor.select(cursor.LineUnderCursor)
            current_line = cursor.selectedText()

            indent = ""
            for ch in current_line:
                if ch in (' ', '\t'):
                    indent += ch
                else:
                    break

            super().keyPressEvent(event)
            self.insertPlainText(indent)

        elif event.key() == Qt.Key_Tab and not event.modifiers() & Qt.ShiftModifier:
            # INDENTAR seleção
            cursor.beginEditBlock()
            selection_start = cursor.selectionStart()
            selection_end = cursor.selectionEnd()

            cursor.setPosition(selection_start)
            start_block = cursor.blockNumber()

            cursor.setPosition(selection_end)
            end_block = cursor.blockNumber()

            for block_num in range(start_block, end_block + 1):
                block = self.document().findBlockByNumber(block_num)
                cursor.setPosition(block.position())
                cursor.insertText("    ")  # 4 espaços

            cursor.endEditBlock()

        elif event.key() == Qt.Key_Backtab or (event.key() == Qt.Key_Tab and event.modifiers() & Qt.ShiftModifier):
            # DESINDENTAR seleção (Shift+Tab)
            cursor.beginEditBlock()
            selection_start = cursor.selectionStart()
            selection_end = cursor.selectionEnd()

            cursor.setPosition(selection_start)
            start_block = cursor.blockNumber()

            cursor.setPosition(selection_end)
            end_block = cursor.blockNumber()

            for block_num in range(start_block, end_block + 1):
                block = self.document().findBlockByNumber(block_num)
                block_cursor = self.textCursor()
                block_cursor.setPosition(block.position())
                block_cursor.movePosition(block_cursor.Right, block_cursor.KeepAnchor, 4)
                text = block_cursor.selectedText()

                if text.startswith("    "):
                    block_cursor.removeSelectedText()
                elif text.startswith("\t"):
                    block_cursor.removeSelectedText()
                elif text.startswith(" "):
                    # remove o máximo possível de espaços à esquerda (até 4)
                    count = 0
                    while count < 4 and text.startswith(" "):
                        block_cursor.setPosition(block.position())
                        block_cursor.movePosition(block_cursor.Right, block_cursor.KeepAnchor, 1)
                        block_cursor.removeSelectedText()
                        text = text[1:]
                        count += 1

            cursor.endEditBlock()

        elif event.key() == 46:
            if self.keyCompleterEvent:
                self.keyCompleterEvent()
            super().keyPressEvent(event)
        else:
            super().keyPressEvent(event)

    #---------------------------------------------------------
    #
    #---------------------------------------------------------

    def finder_prepare(self, params=None):
        if params:
            self.finder_text         = params[0]
            self.finder_replace      = params[1]
            self.finder_flgCase      = params[2]
            self.finder_flgWholeWord = params[3]
        else:
            self.locates    = []
            self.select_idx = 0
            dm.f_principal.ui.toolBox.setCurrentIndex(2)
            dm.f_principal.ui.edt_find_text.setText( self.selectedText() )


    def finder_select(self):
        if len(self.locates) == 0 or self.select_idx == len(self.locates):
            dm.messageBox("no occurrence found")
            return False
        x = self.locates[self.select_idx].start()
        self.setPosition(x)
        self.setPositionSel(x + len(self.finder_text))

        self.select_idx = self.select_idx + 1
        return True

    def finder(self):
        flags          = re.IGNORECASE
        txt_full       = self.toPlainText()
        txt_find       = re.escape( self.finder_text )

        if self.finder_flgCase:
            flags=0

        if self.finder_flgWholeWord:
            txt_find = r"\b" + txt_find + r"\b"

        p               = re.compile( txt_find ,flags=flags)
        self.locates    = [ ii for ii in p.finditer(txt_full) ]
        self.select_idx = 0
        if len(self.locates) > 0:
            self.finder_select()

    def finder_replace(self):
        self.finder()
        self.replaceSelectedText( self.finder_replace )            

    def finder_replace_all(self):
        while True:
            self.find()
            if self.selectedText():
                self.replaceSelectedText(self.ui.edt_replace.text())
            else:
                break        