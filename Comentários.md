
# Devolutiva formativa — Atividade 02 da SA

**Estudante:** Taiane Emanuely Narloch  
**Turma:** Rio Negrinho — Manhã  
**Unidade Curricular:** Programação de Aplicativos  
**Projeto:** Oficina Mecânica  
**Atividade:** Interface funcional  
**Arquivos analisados:** `codigo/app.py`, `interface/index.html`, `interface/script.js` e `interface/style.css`

## O que você já conseguiu desenvolver

Taiane, seu projeto apresenta uma interface web estruturada e integrada à aplicação Flask.

Você organizou funcionalidades de cadastro, consulta e acompanhamento das ordens de serviço.

Pontos positivos identificados:

- Separou HTML, CSS e JavaScript.
- Utilizou templates Jinja2 para apresentar dados da aplicação.
- Criou abas para navegar entre funcionalidades.
- Desenvolveu formulários para cadastro de veículos e abertura de ordens.
- Implementou recursos de busca e filtros.
- Criou indicadores para apresentar quantidades e situações das ordens.
- Utilizou JavaScript para controlar a navegação e atualizar componentes.
- Implementou máscara de telefone e normalização de placa.
- Criou prévia de valores de orçamento.
- Incluiu recursos de navegação por teclado.
- Aplicou atributos de acessibilidade em diferentes componentes.
- Utilizou funções para organizar operações da interface.
- Incluiu comentários e docstrings no código.

## Comparação com a devolutiva anterior

### 1. Integração entre código e interface — ATENDIDO

Na avaliação anterior, foi recomendado verificar a correspondência entre os campos dos formulários e as rotas Flask.

A nova interface utiliza formulários conectados às operações de cadastro, abertura de ordens e atualização de situações.

**Evolução positiva:** a estrutura demonstra ligação entre HTML e as funcionalidades do Python.

### 2. Modularização — PARCIALMENTE ATENDIDO

A interface está organizada em HTML, CSS e JavaScript, o que facilita sua manutenção.

Entretanto, o código Python ainda concentra validações, operações de banco e rotas Flask.

**Como melhorar:** separar gradualmente essas responsabilidades.

### 3. Testes — PARCIALMENTE ATENDIDO

O Python contém testes de funções auxiliares.

**Como melhorar:** ampliar a verificação para os formulários, as rotas e a persistência dos registros.

### 4. Segurança de execução — PENDENTE

A configuração de desenvolvimento ainda utiliza uma chave padrão como alternativa e permite iniciar o Flask em modo de depuração.

**Como melhorar:** utilizar configurações apropriadas antes de publicar o sistema fora do ambiente de desenvolvimento.

## O que precisa ser corrigido

### 5. Compreender os trechos utilizados

O arquivo JavaScript contém um comentário indicando que a parte inicial da navegação por abas ainda precisa ser estudada.

É positivo identificar os próprios pontos de aprendizagem.

**Como melhorar:** revisar o funcionamento de `querySelectorAll()`, `forEach()`, `addEventListener()` e da navegação por teclado. Procure explicar com suas palavras o que cada trecho faz.

### 6. Revisar as regras de alteração das ordens

**Como melhorar:** definir quais mudanças de situação são permitidas e impedir transições incompatíveis com o processo da oficina.

### 7. Melhorar a documentação de execução

**Como melhorar:** atualizar o README com dependências, comando para iniciar o Flask, acesso à página e procedimento de testes.

## Oportunidades de melhoria

### 8. Aprimorar os cálculos monetários

O sistema utiliza `float` e arredondamentos.

**Como melhorar:** estudar o uso de `Decimal` ou valores em centavos, garantindo consistência nos orçamentos.

### 9. Testar a consistência entre interface e servidor

**Como melhorar:** verificar se valores rejeitados pelo JavaScript também são rejeitados pelo Python. A validação não deve depender exclusivamente do navegador.

### 10. Melhorar a organização dos módulos

**Como melhorar:** considerar arquivos específicos para banco, validações, rotas e regras das ordens de serviço.

## Testes recomendados

1. Cadastrar um veículo com placa válida.
2. Tentar cadastrar placa inválida e duplicada.
3. Testar telefone válido, inválido e vazio.
4. Abrir uma ordem com valores de mão de obra e peças.
5. Confirmar o cálculo apresentado na prévia.
6. Filtrar ordens por situação e texto.
7. Atualizar a situação de uma ordem.
8. Reiniciar a aplicação e verificar os dados.
9. Navegar pelas abas utilizando teclado.
10. Verificar as mensagens apresentadas após entradas inválidas.

## Prioridades para a próxima versão

1. **Compreender e explicar todas as funções utilizadas.**
2. **Ampliar os testes de integração.**
3. **Definir as transições permitidas das ordens.**
4. **Revisar as configurações de segurança.**
5. **Separar gradualmente os módulos Python.**

## Mensagem final

Taiane, seu projeto apresenta uma evolução consistente na integração de Flask, HTML, CSS e JavaScript.

A organização das abas, dos formulários e dos recursos de busca demonstra atenção à experiência do usuário.

Continue aprofundando a compreensão dos recursos utilizados e desenvolvendo testes que comprovem o funcionamento do sistema.
