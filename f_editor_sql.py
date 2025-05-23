import dm
import re
from PyQt5.QtWidgets import QPlainTextEdit, QWidget, QTextEdit
from PyQt5.QtGui import QPainter, QTextFormat, QTextCharFormat, QColor, QFont, QSyntaxHighlighter, QTextCursor, QTextOption
from PyQt5.QtCore import QRegExp, Qt, QRect, QSize



#---------------------------------------------------------
#
#---------------------------------------------------------

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
        types = [
            "type","xmltype","rowid","rownum","xmltable","pls_integer","binary_integer","long","raw","number","varchar","varchar2","clob","integer","char","date","timestamp","int","blob"
        ]
        for word in types:
            pattern = QRegExp(r"\b" + word + r"\b", Qt.CaseInsensitive)
            self.highlightingRules.append((pattern, typesFormat))

        functionFormat = QTextCharFormat()
        functionFormat.setForeground(QColor("#B5CEA8"))
        functions = [
            "dbms_output","listagg","chr","utl_file","utl_http","mod","replace","translate","instr","reverse","regexp_instr","regexp_replace","regexp_substr","regexp_count","add_months","lpad","rpad","trunc","to_date","to_char","to_number","nvl","decode","sysdate","count","avg","sum","max","min","case","nvl2","trim","substr","upper","lower","initcap"
        ]
        for word in functions:
            pattern = QRegExp(r"\b" + word + r"\b", Qt.CaseInsensitive)
            self.highlightingRules.append((pattern, functionFormat))


        keywordFormat = QTextCharFormat()
        keywordFormat.setForeground(QColor("#0077aa"))
        keywords = [
            "ABSOLUTE","ACTION","ADD","ADMIN","AFTER","AGGREGATE","ALIAS","ALL","ALLOCATE","ALTER",
            "AND","ANY","ARE","ARRAY","AS","ASC","ASSERTION","AT","AUTHORIZATION","BEFORE","BEGIN",
            "BINARY","BIT","BLOB","BOOLEAN","BOTH","BREADTH","BY","CALL","CASCADE","CASCADED","CASE",
            "CAST","CATALOG","CHAR","CHARACTER","CHECK","CLASS","CLOB","CLOSE","COLLATE","COLLATION",
            "COLUMN","COMMIT","COMPLETION","CONNECT","CONNECTION","CONSTRAINT","CONSTRAINTS","CONSTRUCTOR",
            "CONTINUE","CORRESPONDING","CREATE","CROSS","CUBE","CURRENT","CURRENT_DATE","CURRENT_PATH",
            "CURRENT_ROLE","CURRENT_TIME","CURRENT_TIMESTAMP","CURRENT_USER","CURSOR","CYCLE","DATA",
            "DATE","DAY","DEALLOCATE","DEC","DECIMAL","DECLARE","DEFAULT","DEFERRABLE","DEFERRED",
            "DELETE","DEPTH","DEREF","DESC","DESCRIBE","DESCRIPTOR","DESTROY","DESTRUCTOR","DETERMINISTIC",
            "DICTIONARY","DIAGNOSTICS","DISCONNECT","DISTINCT","DOMAIN","DOUBLE","DROP","DYNAMIC","EACH",
            "ELSE","END","END-EXEC","EQUALS","ESCAPE","EVERY","EXCEPT","EXCEPTION","EXEC","EXECUTE","EXTERNAL",
            "FALSE","FETCH","FIRST","FLOAT","FOR","FOREIGN","FOUND","FROM","FREE","FULL","FUNCTION",
            "GENERAL","GET","GLOBAL","GO","GOTO","GRANT","GROUP","GROUPING","HAVING","HOST","HOUR",
            "IDENTITY","IF","IGNORE","IMMEDIATE","IN","INDICATOR","INITIALIZE","INITIALLY","INNER",
            "INOUT","INPUT","INSERT","INT","INTEGER","INTERSECT","INTERVAL","INTO","IS","ISOLATION",
            "ITERATE","JOIN","KEY","LANGUAGE","LARGE","LAST","LATERAL","LEADING","LEFT","LESS","LEVEL",
            "LIKE","LIMIT","LOCAL","LOCALTIME","LOCALTIMESTAMP","LOCATOR","MAP","MATCH","MINUTE",
            "MODIFIES","MODIFY","MODULE","MONTH","NAMES","NATIONAL","NATURAL","NCHAR","NCLOB","NEW",
            "NEXT","NO","NONE","NOT","NULL","NUMERIC","OBJECT","OF","OFF","OLD","ON","ONLY","OPEN",
            "OPERATION","OPTION","OR","ORDER","ORDINALITY","OUT","OUTER","OUTPUT","PAD","PARAMETER",
            "PARAMETERS","PARTIAL","PATH","POSTFIX","PRECISION","PREFIX","PREORDER","PREPARE","PRESERVE",
            "PRIMARY","PRIOR","PRIVILEGES","PROCEDURE","PUBLIC","READ","READS","REAL","RECURSIVE","REF",
            "REFERENCES","REFERENCING","RELATIVE","RESTRICT","RESULT","RETURN","RETURNS","REVOKE","RIGHT",
            "ROLE","ROLLBACK","ROLLUP","ROUTINE","ROW","ROWS","SAVEPOINT","SCHEMA","SCROLL","SCOPE","SEARCH",
            "SECOND","SECTION","SELECT","SEQUENCE","SESSION","SESSION_USER","SET","SETS","SIZE","SMALLINT",
            "SOME","SPACE","SPECIFIC","SPECIFICTYPE","SQL","SQLEXCEPTION","SQLSTATE","SQLWARNING",
            "START","STATE","STATEMENT","STATIC","STRUCTURE","SYSTEM_USER","TABLE","TEMPORARY","TERMINATE",
            "THAN","THEN","TIME","TIMESTAMP","TIMEZONE_HOUR","TIMEZONE_MINUTE","TO","TRAILING","TRANSACTION",
            "TRANSLATION","TREAT","TRIGGER","TRUE","UNDER","UNION","UNIQUE","UNKNOWN","UNNEST","UPDATE","USAGE",
            "USER","USING","VALUE","VALUES","VARCHAR","VARIABLE","VARYING","VIEW","WHEN","WHENEVER","WHERE","WITH",
            "WITHOUT","WORK","WRITE","YEAR","ZONE","BULK","COLLECT","RECORD","ELSIF","NESTED","PASSING","COLUMNS","LOOP",
            "PACKAGE","BODY"
        ]
        for word in keywords:
            pattern = QRegExp(r"\b" + word + r"\b", Qt.CaseInsensitive)
            self.highlightingRules.append((pattern, keywordFormat))

        stringFormat = QTextCharFormat()
        stringFormat.setForeground(QColor("#aa5500"))
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

#---------------------------------------------------------
#
#---------------------------------------------------------

class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self.editor.lineNumberAreaPaintEvent(event)

#---------------------------------------------------------
#
#---------------------------------------------------------

class CodeEditor(QPlainTextEdit):
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
        self.codeCompeteArea = None
        if customContextMenu:
            self.setContextMenuPolicy(Qt.CustomContextMenu )
            self.customContextMenuRequested.connect(customContextMenu)             

    def lineNumberAreaWidth(self):
        digits = len(str(self.blockCount()))
        return 10 + self.fontMetrics().width('9') * digits

    def setText(self, text):
        return self.setPlainText(text)
    
    def text(self):
        return self.toPlainText()
    
    def selectedText(self):
        return self.textCursor().selectedText()
    
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
            if self.codeCompeteArea:
                self.codeCompeteArea(event)
            super().keyPressEvent(event)
        else:
            super().keyPressEvent(event)


    def formatSql(self):
        import re

        indent = 0
        indent_size = 4
        text = self.toPlainText()

        sql_keywords = [
            "SELECT", "FROM", "WHERE", "INNER JOIN", "LEFT JOIN", "RIGHT JOIN", "FULL JOIN",
            "JOIN", "ON", "GROUP BY", "ORDER BY", "HAVING", "UNION", "INSERT INTO",
            "VALUES", "UPDATE", "SET", "DELETE FROM", "LIMIT", "OFFSET", "AND", "OR"
        ]

        # Ordena por tamanho decrescente para evitar conflitos ("OR" dentro de "ORDER")
        sql_keywords_sorted = sorted(sql_keywords, key=len, reverse=True)
        keyword_pattern = re.compile(
            r'(?<!\n)(?<!^)\b(' + '|'.join(re.escape(k) for k in sql_keywords_sorted) + r')\b', re.IGNORECASE
        )

        # Substitui cada keyword por \n + indent + palavra-chave
        def replacer(match):
            kw = match.group(1).upper()
            return '\n' + ' ' * indent + kw

        # Aplica substituições com cuidado para não quebrar início de linha
        formatted_text = keyword_pattern.sub(replacer, text)

        # Ajuste final: limpa espaços extras e padroniza indentação adicional
        lines = formatted_text.splitlines()
        increase_keywords = ("BEGIN", "LOOP", "THEN", "IF", "CASE", "IS", "AS", "ELSE", "ELSIF", "WHEN")
        decrease_keywords = ("END", "END IF", "ELSE", "ELSIF", "WHEN")

        result = []
        for line in lines:
            stripped = line.strip()

            if not stripped:
                result.append("")
                continue

            if any(stripped.upper().startswith(kw) for kw in decrease_keywords):
                indent = max(indent - indent_size, 0)

            result.append(" " * indent + stripped)

            if any(stripped.upper().startswith(kw) for kw in increase_keywords):
                indent += indent_size

        self.setPlainText("\n".join(result))



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
            dm.f_principal.ui.edt_find_text( self.selectedText() )


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