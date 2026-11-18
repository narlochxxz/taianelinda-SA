
# Devolutiva formativa — Atividade 01 da SA

**Estudante:** Taiane  
**Turma:** Rio Negrinho — Manhã  
**Unidade Curricular:** Programação de Aplicativos  
**Projeto:** Oficina Mecânica  
**Código analisado:** `codigo/app.py`  
**Referência:** Situação de Aprendizagem nº 1 — *Da Ideia ao Código*

## O que você já conseguiu desenvolver

Taiane, você desenvolveu uma aplicação de oficina mecânica com cadastro de clientes e veículos, abertura de ordens de serviço e acompanhamento da situação dos atendimentos. O projeto demonstra atenção à organização do código, à validação de entradas e à integração entre diferentes recursos.

Pontos positivos identificados:

- Criou **funções reutilizáveis** para validar placas, valores e telefones.
- Implementou a normalização de dados, como nomes, placas e números telefônicos.
- Utilizou expressões regulares para reconhecer placas nos formatos antigo e Mercosul.
- Organizou o cálculo dos orçamentos em uma função específica.
- Criou rotas Flask para cadastrar veículos, abrir ordens e atualizar situações.
- Utilizou **SQLite e consultas SQL parametrizadas**.
- Implementou um gerenciador de conexões com `commit()`, `rollback()` e fechamento adequado da conexão.
- Definiu funções para formatar datas e telefones.
- Incluiu verificações com `assert` na função `testar_funcoes()`.
- Desenvolveu arquivos HTML e CSS relacionados à aplicação, antecipando parte da etapa de interface.
- Adicionou docstrings que explicam diferentes funções e regras.

## O que precisa ser corrigido

### 1. Revisar as configurações utilizadas na execução

O aplicativo utiliza uma chave padrão para desenvolvimento e inicia o servidor com `debug=True`.

Essas configurações podem ser utilizadas em ambiente local de estudo, mas precisam ser modificadas antes de qualquer publicação da aplicação.

**Como melhorar:** exigir uma chave de sessão configurada pelo ambiente e manter o modo de depuração desativado fora dos testes locais.

### 2. Revisar a representação dos valores monetários

O sistema utiliza `float` para os valores de mão de obra, peças e orçamentos.

Embora o programa arredonde os resultados, operações monetárias podem apresentar diferenças de precisão quando representadas em ponto flutuante.

**Como melhorar:** considerar `Decimal` ou valores inteiros em centavos. Isso permitirá trabalhar de maneira mais consistente com orçamentos.

### 3. Melhorar a documentação de execução

O README identifica o projeto como Oficina Mecânica, mas ainda precisa informar claramente as dependências, os comandos de execução e os testes disponíveis.

**Como melhorar:** incluir instruções para instalar o Flask, executar `codigo/app.py`, acessar o sistema no navegador e utilizar o modo `--testar`.

## Oportunidades de melhoria

### 4. Separar responsabilidades entre os módulos

O arquivo principal contém validações, criação de tabelas, migrações simples, operações com o banco e rotas Flask.

**Como melhorar:** organizar gradualmente essas responsabilidades em arquivos separados, como regras de negócio, banco de dados e rotas da aplicação.

### 5. Ampliar os testes

A função `testar_funcoes()` verifica diferentes valores, placas, telefones e cálculos.

**Como melhorar:** complementar os testes com operações de cadastro, abertura de ordens e alteração de situações, verificando também respostas de erro e integridade dos registros.

### 6. Revisar as regras de alteração das ordens

A rota `atualizar_status()` permite definir uma situação válida para a ordem e registra a data de conclusão quando necessário.

**Como melhorar:** avaliar se todas as mudanças entre `aberta`, `em andamento` e `concluída` devem ser permitidas. Definir transições coerentes com o processo da oficina.

### 7. Garantir a consistência entre código e interface

O repositório possui arquivos HTML e CSS, e o código Flask faz referência ao template `index.html`.

**Como melhorar:** verificar se os campos enviados pelos formulários correspondem aos nomes esperados em `request.form` e se as mensagens de validação aparecem corretamente na interface.

## Testes recomendados

1. Executar a função `testar_funcoes()`.
2. Cadastrar veículos com placas válidas e inválidas.
3. Tentar cadastrar uma placa já existente.
4. Informar telefone válido, inválido e vazio.
5. Abrir ordens com valores de mão de obra e peças.
6. Testar valores negativos e entradas não numéricas.
7. Atualizar as situações de uma ordem.
8. Verificar as datas de abertura e conclusão.
9. Conferir a recuperação dos registros após reiniciar o sistema.
10. Testar o envio dos formulários pela interface.

## Prioridades para a próxima versão

1. **Melhorar a configuração de segurança para publicação.**
2. **Revisar a precisão dos cálculos monetários.**
3. **Definir regras claras para as transições de situação das ordens.**
4. **Ampliar os testes de integração entre rotas e banco.**
5. **Separar responsabilidades e complementar o README.**

## Mensagem final

Taiane, seu projeto demonstra uma boa compreensão de **funções, validações, organização do código, tratamento de erros e integração de componentes**. A presença de testes para as regras principais também é um ponto positivo.

Continue evoluindo a aplicação com atenção especial à confiabilidade dos dados, às transições entre situações e à documentação. Esses cuidados ajudarão você a manter o sistema organizado e facilitarão as próximas etapas do projeto.
