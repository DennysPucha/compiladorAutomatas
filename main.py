import sys
import re
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QWidget, QTextEdit
from PyQt5.Qsci import QsciScintilla, QsciLexerJavaScript
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtCore import Qt

class CompiladorJS:
    def __init__(self):
        self.palabras = set(['if', 'else', 'while', 'for', 'function', 'return', 'var', 'let', 'const', 'break', 'continue', 'switch', 'case', 'default', 'try', 'catch', 'finally', 'throw', 'async', 'await'])
        self.errores = []
        self.tokens = []
        self.variables = set()

    def tokenize(self, entrada):
        self.tokens = []
        lineas = entrada.split('\n')
        for linea_num, linea in enumerate(lineas, 1):
            tokens = re.findall(r'\b\w+\b|[{}();\[\],=<>+\-*/]|"[^"]*"|\'[^\']*\'', linea)
            for token in tokens:
                self.tokens.append((token, linea_num))
        return self.tokens

    def analyze(self, entrada):
        self.errores = []
        self.variables = set()
        self.tokenize(entrada)
        self.verificar_llaves()
        self.verificar_if()
        self.verificar_for()
        self.verificar_variables()
        self.verificar_funciones()
        self.verificar_palabras_no_declaradas()
        return self.errores

    def verificar_llaves(self):
        pila = []
        for token, linea in self.tokens:
            if token in '{([':
                pila.append((token, linea))
            elif token in '})]':
                if not pila:
                    self.errores.append(f"Error en línea {linea}: Cierre inesperado '{token}'")
                    continue
                opening, _ = pila.pop()
                if (opening == '{' and token != '}') or \
                   (opening == '(' and token != ')') or \
                   (opening == '[' and token != ']'):
                    self.errores.append(f"Error en línea {linea}: Se esperaba cierre para '{opening}', se encontró '{token}'")
        for opening, linea in pila:
            self.errores.append(f"Error en línea {linea}: Falta cierre para '{opening}'")

    def verificar_if(self):
        for i, (token, linea) in enumerate(self.tokens):
            if token == 'if':
                if i + 1 < len(self.tokens) and self.tokens[i+1][0] != '(':
                    self.errores.append(f"Error en línea {linea}: 'if' debe ir seguido de paréntesis")
                else:
                    encontrar_abierta = False
                    encontrar_cerrada = False
                    for j in range(i+1, len(self.tokens)):
                        if self.tokens[j][0] == '{':
                            encontrar_abierta = True
                        elif self.tokens[j][0] == '}':
                            encontrar_cerrada = True
                            break
                    if not encontrar_abierta:
                        self.errores.append(f"Error en línea {linea}: Falta llave de apertura '{{' después del 'if'")
                    elif not encontrar_cerrada:
                        self.errores.append(f"Error en línea {linea}: Falta llave de cierre '}}' para el 'if'")

    def verificar_for(self):
        for i, (token, linea) in enumerate(self.tokens):
            if token == 'for':
                if i + 1 < len(self.tokens) and self.tokens[i + 1][0] != '(':
                    self.errors.append(f"Error en línea {linea}: 'for' debe ir seguido de paréntesis")
                else:
                    punto_y_coma = 0
                    parentesis_cerrado = False
                    llave_abierta = False
                    j = i + 1  
                    while j < len(self.tokens):
                        if self.tokens[j][0] == ';':
                            punto_y_coma += 1
                        elif self.tokens[j][0] == ')':
                            parentesis_cerrado = True
                        elif self.tokens[j][0] == '{':
                            llave_abierta = True
                            break
                        elif self.tokens[j][0] == 'for':
                            break 
                        j += 1

                    if punto_y_coma != 2:
                        self.errores.append(f"Error en línea {linea}: 'for' debe tener dos puntos y coma dentro de los paréntesis")
                    if not parentesis_cerrado:
                        self.errores.append(f"Error en línea {linea}: Falta paréntesis de cierre en la declaración 'for'")
                    if not llave_abierta:
                        self.errores.append(f"Error en línea {linea}: Falta llave de apertura '{{' después de la declaración 'for'")

                    llave_cerrada = False
                    for k in range(j + 1, len(self.tokens)):
                        if self.tokens[k][0] == '}':
                            llave_cerrada = True
                            break
                    if not llave_cerrada:
                        self.errores.append(f"Error en línea {linea}: Falta llave de cierre '}}' para el bloque 'for'")

    def verificar_variables(self):
        for i, (token, linea) in enumerate(self.tokens):
            if token in ['var', 'let', 'const']:
                if i + 1 < len(self.tokens):
                    var_name = self.tokens[i+1][0]
                    if var_name.isidentifier():
                        self.variables.add(var_name)
                    else:
                        self.errores.append(f"Error en línea {linea}: Nombre de variable inválido '{var_name}'")
                else:
                    self.errores.append(f"Error en línea {linea}: Declaración de variable incompleta")

    def verificar_funciones(self):
        i = 0
        while i < len(self.tokens):
            token, linea = self.tokens[i]
            
            if token == 'async':
                if i + 1 < len(self.tokens) and self.tokens[i+1][0] == 'function':
                    i += 1
                else:
                    self.errores.append(f"Error en línea {linea}: 'async' debe ir seguido de 'function'")
                    i += 1
                    continue
            
            if token == 'function':
                if i + 1 < len(self.tokens):
                    func_nombre, func_linea = self.tokens[i+1]
                    if not func_nombre.isidentifier():
                        self.errores.append(f"Error en línea {func_linea}: Nombre de función inválido '{func_nombre}'")
                    else:
                        self.variables.add(func_nombre)
                else:
                    self.errores.append(f"Error en línea {linea}: Falta el nombre de la función")
                    i += 1
                    continue

                if i + 2 < len(self.tokens) and self.tokens[i+2][0] != '(':
                    self.errores.append(f"Error en línea {func_linea}: Falta paréntesis de apertura después del nombre de la función")
                

                encontrar_abierta = False
                for j in range(i+2, len(self.tokens)):
                    if self.tokens[j][0] == '{':
                        encontrar_abierta = True
                        break
                    if self.tokens[j][0] == ';':
                        break
                
                if not encontrar_abierta:
                    self.errores.append(f"Error en línea {func_linea}: Falta llave de apertura '{{' para la función '{func_nombre}'")
            
            i += 1

    def verificar_palabras_no_declaradas(self):
        for token, linea in self.tokens:
            if token.isidentifier() and token not in self.palabras and token not in self.variables:
                self.errores.append(f"Error en línea {linea}: Palabra suelta o variable no declarada '{token}'")

class entradaEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Editor de Código JavaScript")
        self.setGeometry(100, 100, 800, 600)

        main_widget = QWidget()
        layout = QVBoxLayout()

        self.editor = QsciScintilla()
        self.setup_editor()

        analyze_button = QPushButton("Analizar Código")
        analyze_button.clicked.connect(self.analyze_entrada)

        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)

        layout.addWidget(self.editor)
        layout.addWidget(analyze_button)
        layout.addWidget(self.output_area)

        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

        self.analyzer = CompiladorJS()

    def setup_editor(self):
        font = QFont()
        font.setFamily('Courier')
        font.setFixedPitch(True)
        font.setPointSize(10)
        self.editor.setFont(font)
        self.editor.setMarginsFont(font)

        lexer = QsciLexerJavaScript()
        lexer.setDefaultFont(font)
        self.editor.setLexer(lexer)

        self.editor.setMarginType(0, QsciScintilla.NumberMargin)
        self.editor.setMarginWidth(0, "0000")
        self.editor.setMarginsForegroundColor(Qt.darkGray)
        self.editor.setCaretLineVisible(True)
        self.editor.setCaretLineBackgroundColor(QColor("#ffe4e4"))
        self.editor.setAutoIndent(True)
  

    def analyze_entrada(self):
        entrada = self.editor.text()
        errores = self.analyzer.analyze(entrada)
        if errores:
            self.output_area.setText("\n".join(errores))
        else:
            self.output_area.setText("Análisis completado. No se encontraron errores.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    editor = entradaEditor()
    editor.show()
    sys.exit(app.exec_())