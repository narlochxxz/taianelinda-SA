## SISTEMA DA OFICINA MECÂNICA ##
import math
import os
import random
import re
import sqlite3
import string
import sys
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request

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


# ---------- 4. Lógica: clientes e datas ----------
def normalizar_nome(texto):
    """Tira espaços sobrando (ex.: '  Ana   Souza ' -> 'Ana Souza')."""
    return " ".join(texto.split())


def normalizar_telefone(telefone):
    """Deixa só os dígitos (ex.: '(47) 99999-1234' -> '47999991234')."""
    return re.sub(r"\D", "", telefone)


def validar_telefone(telefone):
    """O telefone é opcional. Se informado, precisa de DDD + 8 ou 9 dígitos."""
    return len(normalizar_telefone(telefone)) in (0, 10, 11)


def formatar_telefone(telefone):
    """Mostra o telefone formatado: (47) 99999-1234. Vazio vira '—'."""
    d = telefone or ""
    if len(d) == 11:
        return f"({d[:2]}) {d[2:7]}-{d[7:]}"
    if len(d) == 10:
        return f"({d[:2]}) {d[2:6]}-{d[6:]}"
    return d or "—"


def agora():
    """Data e hora locais para gravar no banco (ex.: 2026-11-16 22:55:00)."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def formatar_data(texto):
    """Converte a data do banco para o padrão brasileiro. Vazio vira '—'."""
    if not texto:
        return "—"
    try:
        return datetime.strptime(texto, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M")
    except ValueError:
        return texto


# ---------- 5. Banco de dados ----------
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
    nome TEXT NOT NULL,
    telefone TEXT NOT NULL DEFAULT ''
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
    mao_de_obra REAL,
    pecas REAL,
    status TEXT NOT NULL DEFAULT 'aberta',
    data_abertura TEXT,
    data_conclusao TEXT,
    FOREIGN KEY (veiculo_id) REFERENCES veiculos(id)
);
"""

COLUNAS_NOVAS = {
    "clientes": {"telefone": "TEXT NOT NULL DEFAULT ''"},
    "ordens_servico": {
        "mao_de_obra": "REAL",
        "pecas": "REAL",
        "data_abertura": "TEXT",
        "data_conclusao": "TEXT",
    },
}


def atualizar_estrutura(conexao):
    """Adiciona as colunas novas em bancos criados por versões antigas."""
    for tabela, colunas in COLUNAS_NOVAS.items():
        existentes = {l["name"] for l in conexao.execute(f"PRAGMA table_info({tabela})")}
        for nome, definicao in colunas.items():
            if nome not in existentes:  # (tabela/coluna vêm das constantes acima)
                conexao.execute(f"ALTER TABLE {tabela} ADD COLUMN {nome} {definicao}")


def criar_tabelas():
    """Cria as tabelas se ainda não existirem e atualiza bancos antigos."""
    with conectar() as conexao:
        conexao.executescript(ESTRUTURA)
        atualizar_estrutura(conexao)


def obter_ou_criar_cliente(conexao, nome, telefone):
    """Reaproveita o cliente com o mesmo nome e telefone; se não houver, cria.

    O nome é comparado sem diferenciar maiúsculas de minúsculas.
    Retorna (id_do_cliente, foi_criado).
    """
    candidatos = conexao.execute(
        "SELECT id, nome FROM clientes WHERE telefone = ?", (telefone,)
    ).fetchall()
    for cliente in candidatos:
        if cliente["nome"].casefold() == nome.casefold():
            return cliente["id"], False

    cursor = conexao.execute(
        "INSERT INTO clientes (nome, telefone) VALUES (?, ?)", (nome, telefone)
    )
    return cursor.lastrowid, True


# ---------- 6. Aplicação Flask ----------
app = Flask(
    __name__,
    template_folder=str(BASE / "interface"),
    static_folder=str(BASE / "interface"),
    static_url_path="/static",
)
# Necessária para as mensagens (flash). Em efina a variável SECRET_KEY.
app.secret_key = os.environ.get("SECRET_KEY", "chave-de-desenvolvimento")

# Filtros usados no HTML: {{ valor | data }} e {{ valor | telefone }}
app.add_template_filter(formatar_data, "data")
app.add_template_filter(formatar_telefone, "telefone")

criar_tabelas()


def montar_pagina(codigo=200, form=None):
    """Monta a tela principal. 'form' devolve ao formulário o que foi digitado."""
    with conectar() as conexao:
        veiculos = conexao.execute(
            "SELECT v.id, v.placa, v.modelo, c.nome, c.telefone "
            "FROM veiculos v JOIN clientes c ON v.cliente_id = c.id"
        ).fetchall()
        ordens = conexao.execute(
            "SELECT o.id, v.placa, c.nome AS cliente, o.descricao, o.valor, "
            "o.mao_de_obra, o.pecas, o.status, o.data_abertura, o.data_conclusao "
            "FROM ordens_servico o "
            "JOIN veiculos v ON o.veiculo_id = v.id "
            "JOIN clientes c ON v.cliente_id = c.id "
            "ORDER BY o.id DESC"
        ).fetchall()
    pagina = render_template(
        "index.html",
        veiculos=veiculos,
        ordens=ordens,
        status_validos=STATUS_VALIDOS,
        form=form or {},
    )
    return pagina, codigo


def recusar(mensagem, codigo):
    """Mostra o erro na própria tela (mantendo o que foi digitado)."""
    flash(mensagem, "erro")
    return montar_pagina(codigo, request.form)


@app.route("/")
def index():
    """Tela principal: veículos, ordens de serviço e formulários."""
    return montar_pagina()


@app.route("/cadastrar", methods=["POST"])
def cadastrar():
    """Cadastra o veículo e o cliente (reaproveita o cliente se já existir)."""
    nome = normalizar_nome(request.form.get("nome", ""))
    modelo = normalizar_nome(request.form.get("modelo", ""))
    placa = normalizar_placa(request.form.get("placa", ""))
    telefone_digitado = request.form.get("telefone", "")

    if not nome or not modelo:
        return recusar("Preencha o nome do cliente e o modelo do veículo.", 400)
    if not validar_placa(placa):
        return recusar("Placa inválida. Use ABC1234 ou ABC1D23.", 400)
    if not validar_telefone(telefone_digitado):
        return recusar("Telefone inválido. Informe o DDD e o número (ex.: 47 99999-1234).", 400)
    telefone = normalizar_telefone(telefone_digitado)

    placa_repetida = False
    cliente_criado = False
    with conectar() as conexao:
        existente = conexao.execute(
            "SELECT id FROM veiculos WHERE placa = ?", (placa,)
        ).fetchone()
        if existente:
            placa_repetida = True
        else:
            cliente_id, cliente_criado = obter_ou_criar_cliente(conexao, nome, telefone)
            conexao.execute(
                "INSERT INTO veiculos (placa, modelo, cliente_id) VALUES (?, ?, ?)",
                (placa, modelo, cliente_id),
            )

    if placa_repetida:
        return recusar("Placa já cadastrada.", 409)

    if cliente_criado:
        flash(f"Cliente {nome} e veículo {placa} cadastrados.", "sucesso")
    else:
        flash(f"Veículo {placa} cadastrado para o cliente já existente ({nome}).", "sucesso")
    return redirect("/")


@app.route("/ordens", methods=["POST"])
def abrir_ordem():
    """Abre uma ordem de serviço e calcula o orçamento (mão de obra + peças)."""
    descricao = normalizar_nome(request.form.get("descricao", ""))
    mao_de_obra = validar_valor(request.form.get("mao_de_obra", ""))
    pecas = validar_valor(request.form.get("pecas", "") or "0", permitir_zero=True)

    try:
        veiculo_id = int(request.form.get("veiculo_id", ""))
    except ValueError:
        return recusar("Selecione o veículo.", 400)

    if not descricao:
        return recusar("Descreva o serviço.", 400)
    if mao_de_obra is None:
        return recusar("Mão de obra inválida. Informe um valor maior que zero (ex.: 150,00).", 400)
    if pecas is None:
        return recusar("Valor das peças inválido (ex.: 89,90). Deixe vazio se não houver.", 400)

    total = calcular_orcamento(mao_de_obra, pecas)

    ordem_id = None
    with conectar() as conexao:
        veiculo = conexao.execute(
            "SELECT id FROM veiculos WHERE id = ?", (veiculo_id,)
        ).fetchone()
        if veiculo is not None:
            cursor = conexao.execute(
                "INSERT INTO ordens_servico "
                "(veiculo_id, descricao, valor, mao_de_obra, pecas, data_abertura) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (veiculo_id, descricao, total, mao_de_obra, pecas, agora()),
            )
            ordem_id = cursor.lastrowid

    if ordem_id is None:
        return recusar("Veículo não encontrado.", 404)

    flash(f"Ordem de serviço #{ordem_id} aberta.", "sucesso")
    return redirect("/")


@app.route("/ordens/<int:ordem_id>/status", methods=["POST"])
def atualizar_status(ordem_id):
    """Atualiza o status de uma ordem (aberta, em andamento, concluída).

    Ao concluir, grava a data de conclusão (sem mudar se já estava concluída).
    Ao reabrir, a data de conclusão é apagada.
    """
    status = request.form.get("status", "")
    if status not in STATUS_VALIDOS:
        return recusar("Status inválido.", 400)

    with conectar() as conexao:
        cursor = conexao.execute(
            "UPDATE ordens_servico SET status = ?, "
            "data_conclusao = CASE WHEN ? = 'concluída' "
            "THEN COALESCE(data_conclusao, ?) ELSE NULL END "
            "WHERE id = ?",
            (status, status, agora(), ordem_id),
        )
        encontrada = cursor.rowcount > 0

    if not encontrada:
        return recusar("Ordem não encontrada.", 404)

    flash(f"Ordem #{ordem_id} agora está \"{status}\".", "sucesso")
    return redirect("/")


# ---------- 7. Testes ----------
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

    # nomes e telefones
    assert normalizar_nome("  Ana   Souza ") == "Ana Souza"
    assert normalizar_telefone("(47) 99999-1234") == "47999991234"
    assert validar_telefone("")                      # opcional
    assert validar_telefone("(47) 99999-1234")       # celular com 9
    assert validar_telefone("47 3333-4444")          # fixo
    assert not validar_telefone("12345")
    assert formatar_telefone("47999991234") == "(47) 99999-1234"
    assert formatar_telefone("4733334444") == "(47) 3333-4444"
    assert formatar_telefone("") == "—"

    # datas
    assert formatar_data("2026-11-16 22:55:00") == "16/11/2026 22:55"
    assert formatar_data(None) == "—"
    assert len(agora()) == 19

    print("Todos os testes passaram.")


# ---------- 8. Execução ----------
if __name__ == "__main__":
    if "--testar" in sys.argv:
        testar_funcoes()
    else:
        app.run(debug=True)

##o html e css estão feitos, mas não prontos.
##então o código roda perfeitamente, mas a interface não está completa.