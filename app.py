

# from datetime import date, datetime
# from functools import wraps
# import logging
# import sqlite3
# import webbrowser
# from threading import Timer
# from typing import Tuple
# import re

# from flask import Flask, request, jsonify, Blueprint, redirect
# from flasgger import Swagger
# from flask_cors import CORS
# from sqlite3 import IntegrityError

# # --- Configuração de Logging ---
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)
# if not logger.handlers:
#     ch = logging.StreamHandler()
#     formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
#     ch.setFormatter(formatter)
#     logger.addHandler(ch)

# DATABASE = 'locadora.db'

# def get_conexao_db():
#     conn = sqlite3.connect(DATABASE)
#     conn.row_factory = sqlite3.Row
#     return conn

# def inicializar_db():
#     """Cria as tabelas necessárias caso elas não existam no SQLite"""
#     conn = get_conexao_db()
#     cursor = conn.cursor()
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS clientes (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             nome TEXT NOT NULL,
#             cpf TEXT NOT NULL UNIQUE,
#             email TEXT,
#             telefone TEXT,
#             data_nascimento TEXT NOT NULL
#         )
#     """)
#     conn.commit()
#     conn.close()
#     logger.info("Banco de dados inicializado com sucesso.")

# def abrir_navegador():
#     webbrowser.open("http://127.0.0.1:5000/apidocs")

# # --- Decorator de Conexão ---
# def gerenciar_conexao_db(func):
#     @wraps(func)
#     def wrapper(*args, **kwargs):
#         conn = get_conexao_db()
#         try:
#             result = func(conn, *args, **kwargs)
#             status_check = result[1] if isinstance(result, tuple) else 200
#             if status_check in [200, 201, 204]:
#                 conn.commit()
#             return result
#         except IntegrityError:
#             conn.rollback()
#             return jsonify({"erro": "Recurso já existe ou viola restrições (CPF duplicado)."}), 409
#         except Exception as e:
#             conn.rollback()
#             return jsonify({"erro": f"Erro inesperado: {str(e)}"}), 500
#         finally:
#             conn.close()
#     return wrapper

# # --- Funções de Validação ---
# def validar_cpf_formato(cpf: str) -> bool:
#     """Valida se o CPF possui 11 dígitos numéricos"""
#     cpf_limpo = re.sub(r'\D', '', str(cpf))
#     if len(cpf_limpo) != 11 or len(set(cpf_limpo)) == 1:
#         return False
#     return True

# def valida_idade(data_nascimento_str: str) -> Tuple[str, int]:
#     if not data_nascimento_str:
#         raise ValueError("Data de nascimento é obrigatória.")
#     try:
#         data_nascimento = datetime.strptime(data_nascimento_str, '%Y-%m-%d').date()
#     except ValueError:
#         raise ValueError("Data inválida ou formato incorreto. Use YYYY-MM-DD.")
    
#     hoje = date.today()
#     id_calc = hoje.year - data_nascimento.year - (
#         (hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day)
#     )
#     if id_calc < 18:
#         raise ValueError("Cliente deve ser maior de 18 anos para se cadastrar.")
#     return data_nascimento_str, id_calc

# # --- Configuração do App ---
# app = Flask(__name__)
# CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# clientes_bp = Blueprint('clientes_bp', __name__, url_prefix='/clientes')
# filmes_bp = Blueprint('filmes_bp', __name__, url_prefix='/filmes')

# @app.route('/')
# def inicio():
#     return redirect('/apidocs')

# # === CÓDIGO DO MOCK DA BUSCA TMDB CORRIGIDO ===
# def busca_filme_tmdb(titulo: str):
#     """Simula uma busca externa de filmes. Retorna os dados se mapeado ou None caso não exista."""
#     filmes_mock = {
#         "matrix": {"titulo": "The Matrix", "genero": "Sci-Fi", "ano": 1999},
#         "avatar": {"titulo": "Avatar", "genero": "Adventure", "ano": 2009},
#         "o poderoso chefão": {"titulo": "The Godfather", "genero": "Crime", "ano": 1972},
#         "interestelar": {"titulo": "Interstellar", "genero": "Sci-Fi", "ano": 2014}
#     }
#     busca = titulo.lower().strip()
#     # Modificado para retornar estritamente None se não bater com a lista
#     return  filmes_mock.get(busca, None)

# # === CLIENTES ===

# @clientes_bp.route('/', methods=['POST'], strict_slashes=False)
# @gerenciar_conexao_db
# def cadastra_cliente(conn: sqlite3.Connection):
#     """
#     Cadastra um novo cliente
#     ---
#     tags:
#       - Clientes
#     requestBody:
#       required: true
#       content:
#         application/json:
#           schema:
#             type: object
#             required:
#               - nome
#               - cpf
#               - data_nascimento
#             properties:
#               nome:
#                 type: string
#               cpf:
#                 type: string
#               data_nascimento:
#                 type: string
#               email:
#                 type: string
#               telefone:
#                 type: string
#     responses:
#       201:
#         description: Cliente cadastrado com sucesso
#       400:
#         description: Erro de validação (Idade ou Campos Vazios)
#       409:
#         description: CPF já cadastrado
#     """
#     dados = request.get_json(silent=True)

#     if not dados:
#         return jsonify({"erro": "JSON não enviado ou inválido."}), 400

#     nome = dados.get('nome')
#     cpf = dados.get('cpf')
#     data_nascimento = dados.get('data_nascimento')
#     email = dados.get('email', '')
#     telefone = dados.get('telefone', '')

#     # Validações de Campos Obrigatórios
#     if not nome or not cpf or not data_nascimento:
#         return jsonify({"erro": "Os campos 'nome', 'cpf' e 'data_nascimento' são obrigatórios."}), 400

#     # Validação de Regra de Negócio: Idade
#     try:
#         valida_idade(data_nascimento)
#     except ValueError as e:
#         return jsonify({"erro": str(e)}), 400

#     # Validação de Formato de CPF
#     if not validar_cpf_formato(cpf):
#         return jsonify({"erro": "Formato de CPF inválido. Certifique-se de enviar 11 dígitos."}), 400

#     # Inserção direta no Banco de Dados
#     cursor = conn.execute("""
#         INSERT INTO clientes (nome, cpf, email, telefone, data_nascimento)
#         VALUES (?, ?, ?, ?, ?)
#     """, (nome, cpf, email, telefone, data_nascimento))
    
#     novo_id = cursor.lastrowid
#     return jsonify({"id": novo_id, "mensagem": "Cliente cadastrado com sucesso!"}), 201

# @clientes_bp.route('/', methods=['GET'], strict_slashes=False)
# @gerenciar_conexao_db
# def lista_clientes(conn: sqlite3.Connection):
#     """
#     Lista todos os clientes cadastrados
#     ---
#     tags:
#       - Clientes
#     responses:
#       200:
#         description: Lista de clientes retornada com sucesso
#     """
#     clientes = conn.execute("SELECT * FROM clientes").fetchall()
#     return jsonify([dict(c) for c in clientes]), 200

# @clientes_bp.route('/<int:id>', methods=['PUT'])
# @gerenciar_conexao_db
# def altera_cliente(conn: sqlite3.Connection, id: int):
#     """
#     Atualiza os dados de um cliente existente
#     ---
#     tags:
#       - Clientes
#     parameters:
#       - name: id
#         in: path
#         required: true
#         schema:
#           type: integer
#     requestBody:
#       required: true
#       content:
#         application/json:
#           schema:
#             type: object
#             required:
#               - nome
#               - email
#               - telefone
#               - data_nascimento
#             properties:
#               nome:
#                 type: string
#               email:
#                 type: string
#               telefone:
#                 type: string
#               data_nascimento:
#                 type: string
#     responses:
#       200:
#         description: Cliente updated com sucesso
#       400:
#         description: Erro de validação de idade ou campos vazios
#       404:
#         description: Cliente não encontrado
#     """
#     dados = request.get_json(silent=True)
#     if not dados:
#         return jsonify({"erro": "Dados não fornecidos"}), 400

#     nome = dados.get('nome')
#     email = dados.get('email', '')
#     telefone = dados.get('telefone', '')
#     data_nascimento = dados.get('data_nascimento')

#     if not nome or not data_nascimento:
#         return jsonify({"erro": "Campos 'nome' e 'data_nascimento' são obrigatórios para atualização."}), 400

#     try:
#         valida_idade(data_nascimento)
#         cursor = conn.execute("""
#             UPDATE clientes
#             SET nome=?, email=?, telefone=?, data_nascimento=?
#             WHERE id=?
#         """, (nome, email, telefone, data_nascimento, id))

#         if cursor.rowcount == 0:
#             return jsonify({"erro": "Cliente não encontrado"}), 404

#         return jsonify({"mensagem": "Cliente atualizado com sucesso"}), 200
#     except ValueError as e:
#         return jsonify({"erro": str(e)}), 400

# @clientes_bp.route('/<int:id>', methods=['DELETE'])
# @gerenciar_conexao_db
# def deleta_cliente(conn: sqlite3.Connection, id: int):
#     """
#     Remove um cliente pelo ID
#     ---
#     tags:
#       - Clientes
#     parameters:
#       - name: id
#         in: path
#         required: true
#         schema:
#           type: integer
#     responses:
#       204:
#         description: Cliente removido com sucesso
#       404:
#         description: Cliente não encontrado
#     """
#     cursor = conn.execute("DELETE FROM clientes WHERE id = ?", (id,))
#     if cursor.rowcount == 0:
#         return jsonify({"erro": "Cliente não encontrado"}), 404
#     return '', 204

# # === FILMES ===

# @filmes_bp.route('/busca_externa', methods=['GET'])
# def busca_filme_externa():
#     """
#     Busca as informações de um filme por título
#     ---
#     tags:
#       - Filmes
#     parameters:
#       - name: titulo
#         in: query
#         required: true
#         schema:
#           type: string
#     responses:
#       200:
#         description: Filme retornado com sucesso
#       400:
#         description: Título não informado
#       404:
#         description: Filme não localizado no catálogo externo
#     """
#     titulo = request.args.get('titulo')

#     if not titulo:
#         return jsonify({"erro": "Título é obrigatório."}), 400

#     resultado = busca_filme_tmdb(titulo)
    
#     # Validação do retorno do mock: se for None, envia erro 404 explicitamente
#     if not resultado:
#         return jsonify({"erro": f"Filme '{titulo}' não foi localizado no catálogo da API externa."}), 404

#     return jsonify(resultado), 200

# # --- REGISTRO FINAL DOS COMPONENTES ---
# app.register_blueprint(clientes_bp)
# app.register_blueprint(filmes_bp)

# app.config['SWAGGER'] = {
#     'title': 'API Sistema de Gestão de Locadora',
#     'uiversion': 3,
#     'openapi': '3.0.2',
#     'host': '127.0.0.1:5000',
#     'schemes': ['http']
# }

# swagger = Swagger(app)

# if __name__ == '__main__':
#     try:
#         inicializar_db()
#     except Exception as e:
#         logger.error(f"Erro ao inicializar DB: {e}")

#     logger.info("Servidor iniciado localmente na porta 5000")
#     Timer(1.5, abrir_navegador).start()
#     app.run(debug=True, host='0.0.0.0', port=5000)

from datetime import date, datetime
from functools import wraps
import logging
import sqlite3
import webbrowser
from threading import Timer
from typing import Tuple
import re
import os

from flask import Flask, request, jsonify, Blueprint, redirect
from flasgger import Swagger
from flask_cors import CORS
from sqlite3 import IntegrityError

# --- Configuração de Logging ---
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

DATABASE = 'locadora.db'

def get_conexao_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def inicializar_db():
    """Cria as tabelas necessárias caso elas não existam no SQLite"""
    conn = get_conexao_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cpf TEXT NOT NULL UNIQUE,
            email TEXT,
            telefone TEXT,
            data_nascimento TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()
    logger.info("Banco de dados inicializado com sucesso.")

def abrir_navegador():
    webbrowser.open("http://127.0.0.1:5000/apidocs")

# --- Decorator de Conexão ---
def gerenciar_conexao_db(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        conn = get_conexao_db()
        try:
            result = func(conn, *args, **kwargs)
            status_check = result[1] if isinstance(result, tuple) else 200
            if status_check in [200, 201, 204]:
                conn.commit()
            return result
        except IntegrityError:
            conn.rollback()
            return jsonify({"erro": "Recurso já existe ou viola restrições (CPF duplicado)."}), 409
        except Exception as e:
            conn.rollback()
            return jsonify({"erro": f"Erro inesperado: {str(e)}"}), 500
        finally:
            conn.close()
    return wrapper

# --- Funções de Validação ---
def validar_cpf_formato(cpf: str) -> bool:
    """Valida se o CPF possui 11 dígitos numéricos"""
    cpf_limpo = re.sub(r'\D', '', str(cpf))
    if len(cpf_limpo) != 11 or len(set(cpf_limpo)) == 1:
        return False
    return True

def valida_idade(data_nascimento_str: str) -> Tuple[str, int]:
    if not data_nascimento_str:
        raise ValueError("Data de nascimento é obrigatória.")
    try:
        data_nascimento = datetime.strptime(data_nascimento_str, '%Y-%m-%d').date()
    except ValueError:
        raise ValueError("Data inválida ou formato incorreto. Use YYYY-MM-DD.")
    
    hoje = date.today()
    id_calc = hoje.year - data_nascimento.year - (
        (hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day)
    )
    if id_calc < 18:
        raise ValueError("Cliente deve ser maior de 18 anos para se cadastrar.")
    return data_nascimento_str, id_calc

# --- Configuração do App ---
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

clientes_bp = Blueprint('clientes_bp', __name__, url_prefix='/clientes')
filmes_bp = Blueprint('filmes_bp', __name__, url_prefix='/filmes')

@app.route('/')
def inicio():
    return redirect('/apidocs')

# === CÓDIGO DO MOCK DA BUSCA TMDB CORRIGIDO ===
def busca_filme_tmdb(titulo: str):
    """Simula uma busca externa de filmes. Retorna os dados se mapeado ou None caso não exista."""
    filmes_mock = {
        "matrix": {"titulo": "The Matrix", "genero": "Sci-Fi", "ano": 1999},
        "avatar": {"titulo": "Avatar", "genero": "Adventure", "ano": 2009},
        "o poderoso chefão": {"titulo": "The Godfather", "genero": "Crime", "ano": 1972},
        "interestelar": {"titulo": "Interstellar", "genero": "Sci-Fi", "ano": 2014}
    }
    busca = titulo.lower().strip()
    return  filmes_mock.get(busca, None)

# === CLIENTES ===

@clientes_bp.route('/', methods=['POST'], strict_slashes=False)
@gerenciar_conexao_db
def cadastra_cliente(conn: sqlite3.Connection):
    """
    Cadastra um novo cliente
    ---
    tags:
      - Clientes
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - nome
              - cpf
              - data_nascimento
            properties:
              nome:
                type: string
              cpf:
                type: string
              data_nascimento:
                type: string
              email:
                type: string
              telefone:
                type: string
    responses:
      201:
        description: Cliente cadastrado com sucesso
      400:
        description: Erro de validação (Idade ou Campos Vazios)
      409:
        description: CPF já cadastrado
    """
    dados = request.get_json(silent=True)

    if not dados:
        return jsonify({"erro": "JSON não enviado ou inválido."}), 400

    nome = dados.get('nome')
    cpf = dados.get('cpf')
    data_nascimento = dados.get('data_nascimento')
    email = dados.get('email', '')
    telefone = dados.get('telefone', '')

    if not nome or not cpf or not data_nascimento:
        return jsonify({"erro": "Os campos 'nome', 'cpf' e 'data_nascimento' são obrigatórios."}), 400

    try:
        valida_idade(data_nascimento)
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400

    if not validar_cpf_formato(cpf):
        return jsonify({"erro": "Formato de CPF inválido. Certifique-se de enviar 11 dígitos."}), 400

    cursor = conn.execute("""
        INSERT INTO clientes (nome, cpf, email, telefone, data_nascimento)
        VALUES (?, ?, ?, ?, ?)
    """, (nome, cpf, email, telefone, data_nascimento))
    
    novo_id = cursor.lastrowid
    return jsonify({"id": novo_id, "mensagem": "Cliente cadastrado com sucesso!"}), 201

@clientes_bp.route('/', methods=['GET'], strict_slashes=False)
@gerenciar_conexao_db
def lista_clientes(conn: sqlite3.Connection):
    """
    Lista todos os clientes cadastrados
    ---
    tags:
      - Clientes
    responses:
      200:
        description: Lista de clientes retornada com sucesso
    """
    clientes = conn.execute("SELECT * FROM clientes").fetchall()
    return jsonify([dict(c) for c in clientes]), 200

@clientes_bp.route('/<int:id>', methods=['PUT'])
@gerenciar_conexao_db
def altera_cliente(conn: sqlite3.Connection, id: int):
    """
    Atualiza os dados de um cliente existente
    ---
    tags:
      - Clientes
    parameters:
      - name: id
        in: path
        required: true
        schema:
          type: integer
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - nome
              - email
              - telefone
              - data_nascimento
            properties:
              nome:
                type: string
              email:
                type: string
              telefone:
                type: string
              data_nascimento:
                type: string
    responses:
      200:
        description: Cliente updated com sucesso
      400:
        description: Erro de validação de idade ou campos vazios
      404:
        description: Cliente não encontrado
    """
    dados = request.get_json(silent=True)
    if not dados:
        return jsonify({"erro": "Dados não fornecidos"}), 400

    nome = dados.get('nome')
    email = dados.get('email', '')
    telefone = dados.get('telefone', '')
    data_nascimento = dados.get('data_nascimento')

    if not nome or not data_nascimento:
        return jsonify({"erro": "Campos 'nome' e 'data_nascimento' são obrigatórios para atualização."}), 400

    try:
        valida_idade(data_nascimento)
        cursor = conn.execute("""
            UPDATE clientes
            SET nome=?, email=?, telefone=?, data_nascimento=?
            WHERE id=?
        """, (nome, email, telefone, data_nascimento, id))

        if cursor.rowcount == 0:
            return jsonify({"erro": "Cliente não encontrado"}), 404

        return jsonify({"mensagem": "Cliente atualizado com sucesso"}), 200
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400

@clientes_bp.route('/<int:id>', methods=['DELETE'])
@gerenciar_conexao_db
def deleta_cliente(conn: sqlite3.Connection, id: int):
    """
    Remove um cliente pelo ID
    ---
    tags:
      - Clientes
    parameters:
      - name: id
        in: path
        required: true
        schema:
          type: integer
    responses:
      204:
        description: Cliente removido com sucesso
      404:
        description: Cliente não encontrado
    """
    cursor = conn.execute("DELETE FROM clientes WHERE id = ?", (id,))
    if cursor.rowcount == 0:
        return jsonify({"erro": "Cliente não encontrado"}), 404
    return '', 204

# === FILMES ===

@filmes_bp.route('/busca_externa', methods=['GET'])
def busca_filme_externa():
    """
    Busca as informações de um filme por título
    ---
    tags:
      - Filmes
    parameters:
      - name: titulo
        in: query
        required: true
        schema:
          type: string
    responses:
      200:
        description: Filme retornado com sucesso
      400:
        description: Título não informado
      404:
        description: Filme não localizado no catálogo externo
    """
    titulo = request.args.get('titulo')

    if not titulo:
        return jsonify({"erro": "Título é obrigatório."}), 400

    resultado = busca_filme_tmdb(titulo)
    
    if not resultado:
        return jsonify({"erro": f"Filme '{titulo}' não foi localizado no catálogo da API externa."}), 404

    return jsonify(resultado), 200

# --- REGISTRO FINAL DOS COMPONENTES ---
app.register_blueprint(clientes_bp)
app.register_blueprint(filmes_bp)

app.config['SWAGGER'] = {
    'title': 'API Sistema de Gestão de Locadora',
    'uiversion': 3,
    'openapi': '3.0.2',
    'host': '127.0.0.1:5000',
    'schemes': ['http']
}

swagger = Swagger(app)

if __name__ == '__main__':
    try:
        inicializar_db()
    except Exception as e:
        logger.error(f"Erro ao inicializar DB: {e}")

    # Verifica se NÃO estamos no processo de reloader do Flask para abrir apenas uma vez
    if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        logger.info("Servidor iniciado localmente na porta 5000")
        Timer(1.5, abrir_navegador).start()
        
    app.run(debug=True, host='0.0.0.0', port=5000)