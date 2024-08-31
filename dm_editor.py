import dm
import re
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


## =============================================================================================
## classe de highligther
## =============================================================================================


class SyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super(SyntaxHighlighter, self).__init__(parent)

        self.highlightingRules = []
        self._mapping = {}
        is_dm = True

        stringF = QTextCharFormat()
        stringF.setForeground(Qt.magenta if is_dm else Qt.blue)
        stringPatterns = [ "'([^'']*)'"]

        funcF = QTextCharFormat()
        funcF.setForeground(Qt.cyan)
        funcPatterns = ['UTL_FILE', 'UTL_HTTP', 'MOD', 'REPLACE','TRANSLATE','INSTR','REVERSE','REGEXP_INSTR','REGEXP_REPLACE','REGEXP_SUBSTR','REGEXP_COUNT','ADD_MONTHS', 'LPAD','RPAD','TRUNC','TO_DATE','TO_CHAR','TO_NUMBER','NVL','DECODE','SYSDATE', 'COUNT','AVG','SUM','MAX','MIN','CASE','NVL2','TRIM','SUBSTR','UPPER','LOWER','INITCAP']

        typeF = QTextCharFormat()
        typeF.setForeground(Qt.magenta)
        typePatterns = ['TYPE','PLS_INTEGER','LONG','RAW','NUMBER','VARCHAR','VARCHAR2','CLOB','INTEGER','CHAR','DATE','TIMESTAMP','INT','BLOB']

        reservedF = QTextCharFormat()
        reservedF.setForeground(Qt.yellow if is_dm else QColor(0,128,128))
        reservedPatterns = ['INTO','EXECUTE', 'IMMEDIATE', 'ROWNUM', 'VALUES', 'GROUP','HAVING','ORDER','WITH','AS','UNION','ALL','DESC','ASC',
                            'TO','PUBLIC','GRANT','DROP','ALTER','SET','IS','NOT','DISTINCT','DEFAULT',
                            'BY','SELECT','INSERT','UPDATE','DELETE','FROM', 'WHERE', 'AND', 'TABLESPACE','THEN', 'BEFORE','AFTER','REFERENCING',
                            'LEVEL','CONNECT','COMPILE','PRIOR','SYNONYM','LIKE','SEGMENT','CREATION','EACH', 'ROW',
                            'IN', 'FOR','BREAK','LOOP','BEGIN','DECLARE','EXCEPTION','WHEN','STORAGE','OLD','NEW',
                            'PCTFREE','PCTUSED','INITRANS','MAXTRANS','NOCOMPRESS','LOGGING','ENABLE','DISABLE','OUT',
                            'END','INNER','LEFT','JOIN','ON','CURSOR','ROWTYPE','OTHERS','UNIQUE','INDEX','ROLLBACK',
                            'ELSE',' THEN','IF','ELSIF','CREATE','OR','FORCE','EDITIONABLE','BETWEEN',
                            'VIEW','TABLE','PROCEDURE','PACKAGE','BODY','TRIGGER','FUNCTION','FREELIST',
                            'MODIFY', 'RENAME', 'ADD','COLUMN','GLOBAL','TEMPORARY','COMMIT','PRESERVE','ROWS',
                            'USING','COMPUTE','STATISTICS','BUFFER_POOL','FLASH_CACHE','CELL_FLASH_CACHE','EXISTS','SQLERRM','RETURN','EXIT','NULL',
                            'INITIAL','NEXT','MINEXTENTS','MAXEXTENTS','PCTINCREASE','FREELISTS','GROUPS']


        self.commentF = QTextCharFormat()
        self.commentF.setForeground(Qt.gray)
        self.commentF.setFontItalic(True)
        commentPatterns = [ r'--.*$' ]

        for r in typePatterns:
            self._mapping["\\b" + r + "\\b"] = typeF

        for r in reservedPatterns:
            self._mapping["\\b" + r + "\\b"] = reservedF

        for r in funcPatterns:
            self._mapping["\\b" + r + "\\b"] = funcF

        for r in stringPatterns:
            self._mapping[r] = stringF

        for r in commentPatterns:
            self._mapping[r] = self.commentF

    def highlightBlock(self, text_block):
        for pattern, fmt in self._mapping.items():
            for match in re.finditer(pattern,text_block, re.I):
                start,end = match.span()
                self.setFormat(start,end-start,fmt)

        commentStartExpression = QRegExp("/\\*")
        commentEndExpression = QRegExp("\\*/")  
        self.setCurrentBlockState(0)
        startIndex = 0
        if self.previousBlockState() != 1:
            startIndex = commentStartExpression.indexIn(text_block)
        while startIndex >= 0:
            endIndex      = commentEndExpression.indexIn(text_block, startIndex)
            commentLength = 0
            if endIndex == -1:
                self.setCurrentBlockState(1)
                commentLength = len(text_block) - startIndex
            else:
                commentLength = endIndex - startIndex + commentEndExpression.matchedLength()
            self.setFormat(startIndex, commentLength, self.commentF)
            startIndex = commentStartExpression.indexIn(text_block, startIndex + commentLength);    

## =============================================================================================
## classe de configuracao do Editor
## =============================================================================================

class QEditorConfig:
    def __init__(self, editor: QPlainTextEdit, keyPressEvt=None):
        self.editor        = editor
        self.__keyPressEvt = keyPressEvt

        self.editor.lineNumberArea = QWidget(self.editor)
        self.editor.resizeEvent = self.resizeEvent
        self.editor.lineNumberArea.paintEvent = self.lineNumberAreaPaintEvent
        self.editor.keyPressEvent = self.editor_keyPressEvent

        self.editor.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.editor.updateRequest.connect(self.updateLineNumberArea)

        self.updateLineNumberAreaWidth(0)
        self.editor.setFont(dm.fontSQL)
        self._ = SyntaxHighlighter(self.editor.document())

    def lineNumberAreaWidth(self):
        digits = 1
        max_block = max(1, self.editor.blockCount())
        while max_block >= 10:
            max_block //= 10
            digits += 1
        space = 10 + self.editor.fontMetrics().horizontalAdvance('9') * digits
        return space

    def updateLineNumberAreaWidth(self, _):
        self.editor.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.editor.lineNumberArea.scroll(0, dy)
        else:
            self.editor.lineNumberArea.update(0, rect.y(), self.editor.lineNumberArea.width(), rect.height())

        if rect.contains(self.editor.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def resizeEvent(self, event):
        cr = self.editor.contentsRect()
        self.editor.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.editor.lineNumberArea)
        ###painter.fillRect(event.rect(), QColor('#C0C0C0'))
        painter.setFont(dm.fontSQL)
        block        = self.editor.firstVisibleBlock()
        block_number = block.blockNumber() + 1
        top          = self.editor.blockBoundingGeometry(block).translated(self.editor.contentOffset()).top()
        bottom       = top + self.editor.blockBoundingRect(block).height()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number)
                painter.setPen(QColor('white'))
                paint_rect = QRect(0, int(top), self.editor.lineNumberArea.width(), self.editor.fontMetrics().height())
                painter.drawText(paint_rect, Qt.AlignCenter, number)

            block = block.next()
            top = bottom
            bottom = top + self.editor.blockBoundingRect(block).height()
            block_number += 1
        painter.end()


    def editor_keyPressEvent(self, event):
        tc = self.editor.textCursor()
        
        if event.key() == Qt.Key_Return:
            y = tc.blockNumber()
            i = -1
            for i,tt in enumerate(  self.editor.document().findBlockByLineNumber(y).text() ):
                if tt != ' ':
                    break
            tc.insertText("\n" + ("" if i == -1 else (" " * i) )  )
            return

        if event.key() in [Qt.Key_Tab, Qt.Key_Backtab]:
            if tc.hasSelection():
                i_start = tc.selectionStart().real
                if event.key() == Qt.Key_Tab:
                    new_text = "\n".join(["  " + x for x in tc.selection().toPlainText().split("\n")])
                else:
                    new_text = "\n".join([x.replace("  ", "", 1) for x in tc.selection().toPlainText().split("\n")])
                tc.insertText(new_text)
                tc.setPosition(i_start)
                tc.setPosition(i_start + len(new_text), QTextCursor.KeepAnchor)
                self.editor.setTextCursor(tc)
            else:
                tc.insertText("  ")
            return
        
        if self.__keyPressEvt:
            self.__keyPressEvt(event)
        else:
            QPlainTextEdit.keyPressEvent(self.editor, event)

