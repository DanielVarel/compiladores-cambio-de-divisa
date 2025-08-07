import ply.lex as lex
import ply.yacc as yacc

# --- PARSE SIDE ---
# Diccionario de tipo de cambio
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

parser = yacc.yacc()
parser_errors = []

# --- LÓGICA PARA LEER EL ARCHIVO ---
def procesar_archivo(nombre_archivo):
    try:
        with open(nombre_archivo, 'r') as archivo:
            contenido = archivo.read().strip()
            
            if not contenido:
                print("El archivo está vacío.")
                return

            global lexer_errors, parser_errors
            lexer_errors = []
            parser_errors = []
            
            # Análisis Léxico de toda la cadena
            lexer.input(contenido.lower())
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
            lexer.input(contenido.lower())
            resultado = parser.parse(lexer=lexer)
            
            print(f"\n--- Analizando la cadena completa ---")
            
            if lexer_errors or parser_errors:
                print("\nErrores de análisis:")
                if lexer_errors:
                    print("  Errores Léxicos:", lexer_errors)
                if parser_errors:
                    print("  Errores Sintácticos:", parser_errors)

            print("\nDetalle del análisis léxico:")
            print("+-------+-----------------+-----------------+")
            print("| Línea | Tipo de token   | Valor o elemento|")
            print("+-------+-----------------+-----------------+")
            for token in lexico_out:
                print(f"| {token['linea']:<5} | {token['tipo']:<15} | {token['valor']:<15} |")
            print("+-------+-----------------+-----------------+")

            print("\nResultado(s) del análisis sintáctico:")
            if isinstance(resultado, list):
                for res in resultado:
                    print(res)
            else:
                print(resultado)
                
            print("----------------------------------------")
            
    except FileNotFoundError:
        print(f"Error: El archivo '{nombre_archivo}' no se encontró.")

if __name__ == '__main__':
    procesar_archivo("data.txt")