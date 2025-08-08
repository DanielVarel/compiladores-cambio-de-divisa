from flask import Flask, jsonify, request, render_template
import ply.lex as lex
import ply.yacc as yacc
import os

# --- PARSE SIDE ---
exchange_rates = {
    'dolar': {'lempira': 24.51, 'euro': 0.92},
    'lempira': {'dolar': 0.041, 'euro': 0.038},
    'euro': {'dolar': 1.08, 'lempira': 26.68}
}

# --- TOKENS ---
tokens = (
    'NUMBER',
    'DIVISA',
    'DOLAR'
)

# --- DEFINICIÓN DE TOKENS (LEXEMAS) ---
def t_NUMBER(t):
    r'\d+(\.\d+)?'
    t.value = float(t.value)
    return t

def t_DIVISA(t):
    r'dolar|lempira|euro'
    t.type = 'DIVISA'
    return t

t_DOLAR = r'\$'

t_ignore = ' \t'

# --- MANEJO DE ERRORES LÉXICOS ---
def t_error(t):
    global lexer_errors
    lexer_errors.append({"linea": t.lineno, "tipo": "Token desconocido", "valor": t.value})
    t.lexer.skip(1)

# Inicializar el analizador léxico
lexer = lex.lex()
lexer_errors = []

# --- REGLAS GRAMATICALES (SINTÁCTICAS) ---
def p_statement_list(p):
    '''
    statement : conversion statement
              | conversion
    '''
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = [p[1]]

def p_conversion(p):
    '''
    conversion : NUMBER DIVISA DIVISA DOLAR
    '''
    try:
        cantidad = p[1]
        origen = p[2]
        destino = p[3]
        if origen == destino:
            p[0] = f"Error: Las divisas de origen y destino son las mismas."
            return
        
        if origen not in exchange_rates or destino not in exchange_rates[origen]:
            p[0] = f"Error: No hay tipo de cambio para {origen} a {destino}"
        else:
            tasa = exchange_rates[origen][destino]
            resultado = cantidad * tasa
            p[0] = f"{cantidad} {origen} es igual a {resultado:.2f} {destino}"
    except Exception as e:
        p[0] = f"Error en la conversión: {e}"

def p_error(p):
    global parser_errors
    if p:
        parser_errors.append({"tipo": "Error de sintaxis", "valor": p.value})
    else:
        parser_errors.append({"tipo": "Error de sintaxis", "valor": "Final de la entrada inesperado"})

# Inicializar el analizador sintáctico
parser = yacc.yacc()
parser_errors = []

# --- FLASK SERVER SIDE ---
app = Flask(__name__, static_folder='static', template_folder='templates')

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    historical_data = None

    if request.method == 'POST':
        cadena = request.form.get('input_text', '').lower()

        # Análisis léxico
        lexer.input(cadena)
        while lexer.token(): pass  # consumir tokens solo para mantener análisis léxico

        # Reiniciar para sintaxis
        lexer.input(cadena)
        result = parser.parse(lexer=lexer)

        # Simular datos históricos para la gráfica
        historical_data = {
            "dates": ["2025-08-01", "2025-08-02", "2025-08-03", "2025-08-04", "2025-08-05", "2025-08-06", "2025-08-07"],
            "rates": [24.63, 24.65, 24.66, 24.64, 24.62, 24.60, 24.61]
        }

    return render_template('index.html', result=result, historical_data=historical_data)


@app.route('/parse', methods=['POST'])
def parse():
    global lexer_errors, parser_errors
    lexer_errors = []
    parser_errors = []
    
    data = request.json
    cadena = data['input_cadena']

    # Análisis Léxico
    lexer.input(cadena.lower())
    lexico_out = []
    while True:
        tok = lexer.token()
        if not tok:
            break
        lexico_out.append({
            "linea": tok.lineno,
            "tipo": tok.type,
            "valor": tok.value
        })
    
    # Reiniciar el lexer para el análisis sintáctico
    lexer.input(cadena.lower())
    
    # Análisis Sintáctico
    resultado = parser.parse(lexer=lexer)
    
    # --- Aquí agregamos los datos históricos para el gráfico ---
    historical = {
        "dates": ["2025-08-01", "2025-08-02", "2025-08-03", "2025-08-04", "2025-08-05", "2025-08-06", "2025-08-07"],
        "rates": [24.63, 24.65, 24.66, 24.64, 24.62, 24.60, 24.61]
    }
    
    response = {
        "Resultado": resultado if resultado else "Error: Sintaxis inválida",
        "Errores_lexicos": lexer_errors,
        "Errores_sintacticos": parser_errors,
        "lexico": lexico_out,
        "historical": historical  # <-- datos del gráfico
    }
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)