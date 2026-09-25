# Sorteio dos Jogos dos Servidores de Boa Vista 2026

Código aberto do **motor dos sorteios** da 10ª edição dos Jogos dos Servidores Municipais de
Boa Vista (SMAG/SASQV), feito pela [Hunt Sport TV](https://huntsport.com.br). Está aqui para que
qualquer pessoa possa conferir que os sorteios são aleatórios de verdade.

São dois sorteios, feitos ao vivo e transmitidos:

| Sorteio | O que decide | Arquivo |
|---|---|---|
| **Cores** | que cor cada secretaria usa nos Jogos | [`sorteio/cores.py`](sorteio/cores.py) |
| **Chaves** | em que grupo ou jogo cada equipe cai | [`sorteio/chaves.py`](sorteio/chaves.py) |

Este repositório tem **só o motor** — a parte que escolhe. As telas, o servidor e o restante do
sistema não estão aqui, porque não decidem nada: só mostram o que o motor sorteou.

## Como o sorteio funciona

**Nada é calculado antes.** Cada bola é sorteada no momento em que o operador pede, como num
sorteio de bolinhas.

**O acaso vem do sistema operacional** (`random.SystemRandom`, que lê `os.urandom` — o mesmo tipo
de fonte usado em criptografia). Não existe semente: nem quem opera consegue prever ou repetir um
resultado.

**Cores** — dois sacos: um de secretarias, outro de cores. A cada bola sai uma de cada saco, ao
acaso. Quem já saiu não volta até o sorteio recomeçar. Toda atribuição possível tem a mesma chance.

**Chaves** — sorteio duplo: primeiro sai QUEM (uma equipe do pote), depois sai ONDE (uma vaga).
Quando a categoria tem a regra "duas equipes da mesma secretaria não caem no mesmo grupo", antes de
cada bola de posição o motor calcula quais vagas ainda deixam o sorteio terminar e sorteia só entre
elas — para nunca chegar à última bola sem lugar válido. Os testes abaixo mostram que isso não
empurra nenhuma equipe para um grupo específico.

## Como auditar

1. **Leia o código.** São dois arquivos curtos em Python, comentados em português.
2. **Rode os testes de imparcialidade** (só precisa de Python 3, sem instalar nada):

   ```
   python3 testes/imparcialidade_cores.py
   python3 testes/imparcialidade_chaves.py
   ```

   Eles fazem dezenas de milhares de sorteios completos e mostram, com o teste do qui-quadrado, que
   cada combinação sai na mesma proporção — e, nas chaves, que a regra de secretaria nunca é violada
   e o sorteio nunca trava.
3. **Confira a versão.** Durante o sorteio, a tela mostra no rodapé o código da versão do motor
   (por exemplo `motor 3f2a1bc`). É o identificador de um commit deste repositório: basta procurá-lo
   no histórico para ver exatamente o código que estava rodando.
4. **Confira a ata.** Cada bola é gravada com a hora exata em que saiu, e com a declaração feita
   antes da primeira bola — **ENSAIO** (demonstração, não vale) ou **DEFINITIVO**. As atas são
   publicadas na pasta [`atas/`](atas/) depois de cada sorteio.

## Licença

[MIT](LICENSE) — qualquer pessoa pode ler, rodar e reutilizar.
