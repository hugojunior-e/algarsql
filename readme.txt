## ==============================================================================================
## SQLEditor Personalizado
## ==============================================================================================
class CustomSQLLexer(QsciLexerSQL):
    def __init__(self, parent=None):
        super(CustomSQLLexer, self).__init__(parent)

    def keywords(self, set_number):
        if set_number == 5:
            return QsciLexerSQL.keywords(self, set_number) + " listagg chr utl_file utl_http mod replace translate instr reverse regexp_instr regexp_replace regexp_substr regexp_count add_months lpad rpad trunc to_date to_char to_number nvl decode sysdate count avg sum max min case nvl2 trim substr upper lower initcap"
        elif set_number == 6:
            return 'type xmltype rowid rownum xmltable pls_integer binary_integer long raw number varchar varchar2 clob integer char date timestamp int blob'
        elif set_number == 1:
            return QsciLexerSQL.keywords(self, set_number) + " bulk collect record elsif nested passing columns loop package body"
        else:
            return QsciLexerSQL.keywords(self, set_number)


class EDITOR_SQL(QsciScintilla):
    def __init__(self, text="", customContextMenu=None):
        super().__init__()
        fontSQL       = QFont()
        fontSQL.setFamily("Monospace")
        fontSQL.setPointSize(10)

        self.setFont(fontSQL)     

        # Configurações básicas do editor
        self.setUtf8(True)
        self.setAutoIndent(True)
        self.setIndentationGuides(False)  # Mostra guias de indentação
        self.setIndentationsUseTabs(False)  # Usa espaços em vez de tabs
        self.setTabWidth(2)  # Define a largura da indentação em 4 espaços
        
        # Adicionando a numeração de linhas
        self.setMarginsFont(fontSQL)
        self.setMarginWidth(0, "00000")  # Margem 0 para números de linha
        self.setMarginLineNumbers(0, True)
        

        # Lexer SQL para realce de sintaxe
        self.sql_lexer = CustomSQLLexer()
        self.sql_lexer.setFont(fontSQL)
        self.sql_lexer.setColor(  QColor("#569CD6") , QsciLexerSQL.Keyword)
        self.sql_lexer.setColor(  QColor("#CE9178") , QsciLexerSQL.SingleQuotedString)
        self.sql_lexer.setColor(  QColor("#CE9178") , QsciLexerSQL.DoubleQuotedString)
        self.sql_lexer.setColor(  Qt.cyan , QsciLexerSQL.KeywordSet5)
        self.sql_lexer.setColor(  QColor("#B5CEA8") , QsciLexerSQL.KeywordSet6)
        self.sql_lexer.setColor(  QColor("#B5CEA8") , QsciLexerSQL.Number)
        self.setLexer(self.sql_lexer)        

        # Destacar a Linha corrente
        self.setCaretLineVisible(False)
        self.setCaretLineBackgroundColor(QColor('000000'))   
        self.setCaretForegroundColor(QColor('#FFFFFF'))

        # Ativar o pareamento de parênteses
        self.setBraceMatching(QsciScintilla.SloppyBraceMatch)  # Pode ser 'StrictBraceMatch' ou 'SloppyBraceMatch'
        self.setMatchedBraceForegroundColor(Qt.red)
        self.setMatchedBraceBackgroundColor(Qt.black)
        self.setUnmatchedBraceForegroundColor(Qt.black)

        if customContextMenu:
            self.setContextMenuPolicy(Qt.CustomContextMenu )
            self.customContextMenuRequested.connect(customContextMenu)        

        self.setText(text)
    
    def wordOnCursor(self):
        line, index = self.getCursorPosition()
        word = self.wordAtLineIndex(line, index)
        return word

    def currentPosition(self):
        return self.SendScintilla(QsciScintilla.SCI_GETCURRENTPOS)
    
    def setPosition(self, pos):
            self.SendScintilla(QsciScintilla.SCI_GOTOPOS, pos)
            self.ensureCursorVisible()    

    def setPositionSel(self, pos):
            self.SendScintilla(QsciScintilla.SCI_SETCURRENTPOS, pos)
            self.ensureCursorVisible()    
    
    def unselect(self):
        self.SendScintilla(QsciScintilla.SCI_CLEARSELECTIONS)

    def cursorRect(self):
        position = self.SendScintilla(QsciScintilla.SCI_GETCURRENTPOS)
        x = self.SendScintilla(QsciScintilla.SCI_POINTXFROMPOSITION, 0, position)
        y = self.SendScintilla(QsciScintilla.SCI_POINTYFROMPOSITION, 0, position)
        line_height = self.SendScintilla(QsciScintilla.SCI_TEXTHEIGHT, 0)
        return QRect(x, y, 1, line_height) 