# Ferramentas para Linguagens Livres de Contexto

## Utilizando a biblioteca

A biblioteca não possui nenhuma dependência externa; para utilizar sua gramática livre
de contexto basta importar o módulo context_free.grammar.

As funcionalidades implementadas foram as seguintes:

1. Conversão para forma normal de chomsky
2. Detecção de epsilon produções, produções cíclicas e recursão à esquerda
3. Importação e Exportação de arquivos .cfg
4. Remoção de recursão à esquerda
5. Fatoração à esquerda
6. Geração de analisador sintático LL(1) a partir de gramática fatorada e livre de recursão à esquerda
7. Análise sintática de palavras à partir de um analisador sintático

## Arquivos .cfg

O construtor da classe ContextFreeGrammar espera o nome de um arquivo presente no diretório cfgs.
Este arquivo deve seguir o padrão .cfg, que é descrito por uma gramática livre de contexto - spec.cfg - dentro do
mesmo diretório.

## Rodando os testes

Para executar os testes de unidade, digite:

```
$ python3 test.py
```
