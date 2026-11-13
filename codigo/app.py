## SISTEMA DE OFICINA MECÂNICA ##
import random
import re
import sqlite3
import string
from pathlib import Path

from flask import Flask, redirect, render_template, request

# ---------- 1. Caminhos ----------
BASE = Path(__file__).resolve().parent.parent
CAMINHO_DB = BASE / "banco_de_dados" / "oficina.db"


# ---------- 2. Lógica: placas ----------
def gerar_placa():
    """Gera uma placa fictícia no formato Mercosul (ex.: ABC1D23)."""
    letras = string.ascii_uppercase
    digitos = string.digits

    l1 = ''.join(random.choices(letras, k=3))
    n1 = random.choice(digitos)
    l2 = random.choice(letras)
    n2 = ''.join(random.choices(digitos, k=2))
    return f'{l1}{n1}{l2}{n2}'


def validar_placa(placa):
    """Retorna True se a placa estiver no formato antigo (ABC1234) ou Mercosul (ABC1D23)."""
    placa = placa.strip().upper().replace('-', '')
    padrao = r'^[A-Z]{3}\d{4}$|^[A-Z]{3}\d[A-Z]\d{2}$'
    return re.match(padrao, placa) is not None


# ---------- 3. Banco de dados ----------
def conectar():
    conexao = sqlite3.connect(CAMINHO_DB)
    conexao.row_factory = sqlite3.Row  # permite usar linha["placa"]
    return conexao

ESTRUTURA = """
CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS veiculos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    placa TEXT NOT NULL UNIQUE,
    modelo TEXT NOT NULL,
    cliente_id INTEGER NOT NULL,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
);

CREATE TABLE IF NOT EXISTS ordens_servico (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    veiculo_id INTEGER NOT NULL,
    descricao TEXT NOT NULL,
    valor REAL NOT NULL,
    status TEXT NOT NULL DEFAULT 'aberta',
    FOREIGN KEY (veiculo_id) REFERENCES veiculos(id)
);
"""


def criar_tabelas():
    with conectar() as conexao:
        conexao.executescript(ESTRUTURA)

# ---------- 4. Aplicação Flask ----------
app = Flask(
    __name__,
    template_folder=str(BASE / "interface"),
    static_folder=str(BASE / "interface"),
    static_url_path="/static",
)
criar_tabelas()

@app.route("/")
def index():
    with conectar() as conexao:
        veiculos = conexao.execute(
            "SELECT v.placa, v.modelo, c.nome "
            "FROM veiculos v JOIN clientes c ON v.cliente_id = c.id"
        ).fetchall()
    return render_template("index.html", veiculos=veiculos)


@app.route("/cadastrar", methods=["POST"])
def cadastrar():
    nome = request.form["nome"].strip()
    placa = request.form["placa"].strip().upper()
    modelo = request.form["modelo"].strip()

    if not nome or not modelo or not validar_placa(placa):
        return "Dados inválidos.", 400

    with conectar() as conexao:
        cursor = conexao.execute("INSERT INTO clientes (nome) VALUES (?)", (nome,))
        conexao.execute(
            "INSERT INTO veiculos (placa, modelo, cliente_id) VALUES (?, ?, ?)",
            (placa, modelo, cursor.lastrowid),
        )
    return redirect("/")


# ---------- 5. Execução ----------
if __name__ == "__main__":
    app.run(debug=True)