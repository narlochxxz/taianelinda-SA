CREATE TABLE IF NOT EXISTS cliente (
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    nome TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS veiculos (
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    placa TEXT NOT NULL UNIQUE, 
    modelo TEXT NOT NULL, 
    cliente_id INTEGER NOT NULL, 
    FOREIGN KEY (cliente_id) REFERENCES cliente(id)
);

CREATE TABLE IF NOT EXISTS ordens_servico (
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    veiculo_id INTEGER NOT  NULL, 
    descricao TEXT NOT NULL, 
    valor REAL NOT NULL, 
    STATUS text not null default 'aberta',
    FOREIGN KEY (veiculo_id) REFERENCES veiculos(id)
    );

