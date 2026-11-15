## SISTEMA DE OFICINA MECÂNICA ##
import math
import random
import re
import sqlite3
import string
import sys
from contextlib import contextmanager
from pathlib import Path

from flask import Flask, redirect, render_template, request

# ---------- 1. Configurações ----------
BASE = Path(__file__).resolve().parent.parent
CAMINHO_DB = BASE / "banco_de_dados" / "oficina.db"

# Formato antigo (ABC1234) ou Mercosul (ABC1D23)
PADRAO_PLACA = r'[A-Z]{3}[0-9]{4}|[A-Z]{3}[0-9][A-Z][0-9]{2}'
STATUS_VALIDOS = ("aberta", "em andamento", "concluída")


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


def normalizar_placa(placa):
    """Deixa a placa em maiúsculas e sem espaços ou hífen (ex.: abc-1234 -> ABC1234)."""
    return placa.strip().upper().replace('-', '')


def validar_placa(placa):
    """Retorna True se a placa estiver no formato antigo ou Mercosul."""
    return re.fullmatch(PADRAO_PLACA, normalizar_placa(placa)) is not None


# ---------- 3. Lógica: valores e orçamento ----------
def validar_valor(texto, permitir_zero=False):
    """Converte um texto em valor em reais. Retorna None se for inválido.

    Aceita '100', '100.50' e '1.250,50'. Rejeita texto, negativos e 'nan'.
    """
    texto = texto.strip()
    if "," in texto:  # formato brasileiro: 1.250,50
        texto = texto.replace(".", "").replace(",", ".")
    try:
        valor = float(texto)
    except ValueError:
        return None
    if not math.isfinite(valor):
        return None
    if valor < 0 or (valor == 0 and not permitir_zero):
        return None
    return round(valor, 2)


def calcular_orcamento(mao_de_obra, pecas):
    """Soma a mão de obra e o valor das peças."""
    return round(mao_de_obra + pecas, 2)


# ---------- 4. Banco de dados ----------
@contextmanager
def conectar():
    """Abre o banco, confirma (commit) no fim e sempre fecha a conexão."""
    conexao = sqlite3.connect(CAMINHO_DB)
    conexao.row_factory = sqlite3.Row  # permite usar linha["placa"]
    conexao.execute("PRAGMA foreign_keys = ON")
    try:
        yield conexao
        conexao.commit()
    except Exception:
        conexao.rollback()
        raise
    finally:
        conexao.close()


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
    """Cria as tabelas se ainda não existirem."""
    with conectar() as conexao:
        conexao.executescript(ESTRUTURA)


# ---------- 5. Aplicação Flask ----------
app = Flask(
    __name__,
    template_folder=str(BASE / "interface"),
    static_folder=str(BASE / "interface"),
    static_url_path="/static",
)

criar_tabelas()


@app.route("/")
def index():
    """Tela principal: veículos, ordens de serviço e formulários."""
    with conectar() as conexao:
        veiculos = conexao.execute(
            "SELECT v.id, v.placa, v.modelo, c.nome "
            "FROM veiculos v JOIN clientes c ON v.cliente_id = c.id"
        ).fetchall()
        ordens = conexao.execute(
            "SELECT o.id, v.placa, o.descricao, o.valor, o.status "
            "FROM ordens_servico o JOIN veiculos v ON o.veiculo_id = v.id "
            "ORDER BY o.id DESC"
        ).fetchall()
    return render_template(
        "index.html", veiculos=veiculos, ordens=ordens, status_validos=STATUS_VALIDOS
    )


@app.route("/cadastrar", methods=["POST"])
def cadastrar():
    """Cadastra cliente e veículo, validando os dados recebidos."""
    nome = request.form.get("nome", "").strip()
    placa = normalizar_placa(request.form.get("placa", ""))
    modelo = request.form.get("modelo", "").strip()

    if not nome or not modelo or not validar_placa(placa):
        return "Dados inválidos.", 400

    with conectar() as conexao:
        existente = conexao.execute(
            "SELECT id FROM veiculos WHERE placa = ?", (placa,)
        ).fetchone()
        if existente:
            return "Placa já cadastrada.", 409

        cursor = conexao.execute("INSERT INTO clientes (nome) VALUES (?)", (nome,))
        conexao.execute(
            "INSERT INTO veiculos (placa, modelo, cliente_id) VALUES (?, ?, ?)",
            (placa, modelo, cursor.lastrowid),
        )
    return redirect("/")


@app.route("/ordens", methods=["POST"])
def abrir_ordem():
    """Abre uma ordem de serviço e calcula o orçamento (mão de obra + peças)."""
    descricao = request.form.get("descricao", "").strip()
    mao_de_obra = validar_valor(request.form.get("mao_de_obra", ""))
    pecas = validar_valor(request.form.get("pecas", "") or "0", permitir_zero=True)

    try:
        veiculo_id = int(request.form.get("veiculo_id", ""))
    except ValueError:
        return "Veículo inválido.", 400

    if not descricao or mao_de_obra is None or pecas is None:
        return "Dados inválidos.", 400

    total = calcular_orcamento(mao_de_obra, pecas)

    with conectar() as conexao:
        veiculo = conexao.execute(
            "SELECT id FROM veiculos WHERE id = ?", (veiculo_id,)
        ).fetchone()
        if veiculo is None:
            return "Veículo não encontrado.", 404

        conexao.execute(
            "INSERT INTO ordens_servico (veiculo_id, descricao, valor) VALUES (?, ?, ?)",
            (veiculo_id, descricao, total),
        )
    return redirect("/")


@app.route("/ordens/<int:ordem_id>/status", methods=["POST"])
def atualizar_status(ordem_id):
    """Atualiza o status de uma ordem (aberta, em andamento, concluída)."""
    status = request.form.get("status", "")
    if status not in STATUS_VALIDOS:
        return "Status inválido.", 400

    with conectar() as conexao:
        cursor = conexao.execute(
            "UPDATE ordens_servico SET status = ? WHERE id = ?", (status, ordem_id)
        )
        if cursor.rowcount == 0:
            return "Ordem não encontrada.", 404
    return redirect("/")


# ---------- 6. Testes ----------
def testar_funcoes():
    """Testes simples da lógica. Rode com: python codigo/app.py --testar"""
    # placas
    assert validar_placa("ABC1D23")
    assert validar_placa("abc-1234")
    assert not validar_placa("12AB345")
    assert not validar_placa("")
    for _ in range(100):
        assert validar_placa(gerar_placa())

    # valores
    assert validar_valor("100") == 100.0
    assert validar_valor("1.250,50") == 1250.5
    assert validar_valor("-5") is None
    assert validar_valor("abc") is None
    assert validar_valor("nan") is None
    assert validar_valor("0") is None
    assert validar_valor("0", permitir_zero=True) == 0.0

    # orçamento
    assert calcular_orcamento(150.0, 89.9) == 239.9

    print("Todos os testes passaram.")


# ---------- 7. Execução ----------
if __name__ == "__main__":
    if "--testar" in sys.argv:
        testar_funcoes()
    else:
        app.run(debug=True)