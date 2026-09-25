"""Teste de imparcialidade do sorteio das CORES.

Roda o sorteio completo muitas vezes e conta quantas vezes cada secretaria ficou com cada cor.
Se o sorteio é justo, todas as combinações aparecem na mesma proporção (1 em 24), a menos da
variação natural do acaso — e o teste do qui-quadrado diz se a diferença observada é do tamanho
que o acaso produz.

    python3 testes/imparcialidade_cores.py            # 24.000 sorteios
    python3 testes/imparcialidade_cores.py 100000     # mais sorteios, conclusão mais firme
"""
import csv
import math
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from sorteio.cores import sortear_tudo  # noqa: E402


def main(n):
    linhas = list(csv.DictReader(open(RAIZ / "exemplos" / "secretarias-e-cores.csv", encoding="utf-8")))
    secretarias = [l["sigla"] for l in linhas]
    cores = [{"nome": l["nome"]} for l in linhas]
    k = len(secretarias)
    par, primeira = Counter(), Counter()
    for _ in range(n):
        bolas = sortear_tudo(secretarias, cores)
        primeira[bolas[0][0]] += 1
        for s, c in bolas:
            par[(s, c["nome"])] += 1

    esperado = n / k
    qui = sum((par[(s, c["nome"])] - esperado) ** 2 / esperado for s in secretarias for c in cores)
    gl = (k - 1) ** 2
    z = (qui - gl) / math.sqrt(2 * gl)            # aproximação normal do qui-quadrado
    menor, maior = min(par.values()), max(par.values())
    print(f"{n} sorteios completos, {k} secretarias x {k} cores")
    print(f"cada par secretaria-cor deveria aparecer ~{esperado:.0f} vezes; "
          f"apareceu entre {menor} e {maior}")
    print(f"qui-quadrado = {qui:.1f} com {gl} graus de liberdade  (z = {z:+.2f})")
    print(f"quem sai na 1a bola: entre {min(primeira.values())} e {max(primeira.values())} vezes "
          f"(esperado ~{esperado:.0f})")
    ok = abs(z) < 3.5
    print("RESULTADO:", "distribuição compatível com sorteio justo" if ok
          else "ATENÇÃO: diferença maior do que o acaso explica")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(int(sys.argv[1]) if len(sys.argv) > 1 else 24000))
