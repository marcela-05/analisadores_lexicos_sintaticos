from sly import Lexer

class DeviceLexer(Lexer):
    ignore = " \t\r"
    literals = { }

    tokens = {
        'DISPOSITIVO', 'SET', 'SE', 'ENTAO', 'SENAO', 'ENVIAR', 'ALERTA',
        'PARA', 'TODOS', 'LIGAR', 'DESLIGAR',
        'OPLOGIC', 'AND',
        'DOIS_PONTOS', 'PONTO', 'VIRGULA', 'IGUAL',
        'ABRE_CHAVE', 'FECHA_CHAVE', 'ABRE_PAREN', 'FECHA_PAREN',
        'NAMEDEVICE', 'OBSERVATION', 'NUM', 'BOOL', 'MSG'
    }

    # Palavras-chave
    DISPOSITIVO = r'dispositivo\b'
    SET         = r'set\b'
    SE          = r'se\b'
    ENTAO       = r'entao\b'
    SENAO       = r'senao\b'
    ENVIAR      = r'enviar\b'
    ALERTA      = r'alerta\b'
    PARA        = r'para\b'
    TODOS       = r'todos\b'
    LIGAR       = r'ligar\b'
    DESLIGAR    = r'desligar\b'

    # Operadores
    AND     = r'&&'
    OPLOGIC = r'(==|!=|<=|>=|<|>)'

    # Símbolos
    DOIS_PONTOS  = r':'
    PONTO        = r'\.'
    VIRGULA      = r','
    IGUAL        = r'='
    ABRE_CHAVE   = r'\{'
    FECHA_CHAVE  = r'\}'
    ABRE_PAREN   = r'\('
    FECHA_PAREN  = r'\)'

    # Literais
    @_(r'\d+')
    def NUM(self, t):
        t.value = int(t.value)
        return t

    @_(r'(true|false)')
    def BOOL(self, t):
        t.value = t.value == 'true'
        return t

    @_(r'"[^"]*"')
    def MSG(self, t):
        t.value = t.value[1:-1]  # Remove aspas
        return t

    # nameDevice: só letras
    @_(r'[a-zA-Z]+')
    def NAMEDEVICE(self, t):
        keywords = {
            'dispositivo', 'set', 'se', 'entao', 'senao', 'enviar',
            'alerta', 'para', 'todos', 'ligar', 'desligar', 'true', 'false'
        }
        if t.value in keywords:
            t.type = t.value.upper()
        return t

    # observation: começa com letra, pode ter letras, números e _
    @_(r'[a-zA-Z][a-zA-Z0-9_]*')
    def OBSERVATION(self, t):
        keywords = {
            'dispositivo', 'set', 'se', 'entao', 'senao', 'enviar',
            'alerta', 'para', 'todos', 'ligar', 'desligar', 'true', 'false'
        }
        if t.value in keywords:
            t.type = t.value.upper()
        return t

    @_(r'\n+')
    def newline(self, t):
        self.lineno += len(t.value)

    def error(self, t):
        print(f"Erro léxico: caractere ilegal '{t.value[0]}' na linha {self.lineno}")
        self.index += 1


# Exemplo de uso do lexer
if __name__ == "__main__":
    lexer = DeviceLexer()

    # Exemplo de código para testar
    codigo_exemplo = '''
    dispositivo : sensorTemp
    dispositivo : ledVermelho, temperatura2

    set temperatura2 = 25.

    se temperatura2 > 30 entao ligar ledVermelho.
    se temperatura2 < 10 && temperatura2 > 0 entao enviar alerta ("Temperatura baixa") sensorTemp.
    '''

    print("Tokens encontrados:")
    print("-" * 50)

    for token in lexer.tokenize(codigo_exemplo):
        print(f"{token.type:12} | {repr(token.value):20} | Linha: {token.lineno}")

    print("-" * 50)
