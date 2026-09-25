"""Teste de imparcialidade e de segurança do sorteio das CHAVES.

Categoria de exemplo: 12 equipes de 6 secretarias (2 de cada), em 4 grupos de 3, com a regra
"duas equipes da mesma secretaria não caem no mesmo grupo". O teste confere, em milhares de
sorteios completos:
1. a regra de secretaria NUNCA é violada;
2. o sorteio NUNCA trava (sempre há vaga válida até a última bola);
3. cada equipe cai em cada grupo na mesma proporção (1 em 4), a menos do acaso — ou seja, a
   regra de secretaria não empurra ninguém para um grupo específico.

    python3 testes/imparcialidade_chaves.py            # 20.000 sorteios
"""
import math
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from sorteio.chaves import Mesa  # noqa: E402

GRUPOS, POR_GRUPO = "ABCD", 3
EQUIPES = [{"equipe": f"Equipe {s}{i}", "secretaria": s} for s in "PQRSTU" for i in (1, 2)]


def categoria():
    vagas = [{"chave": f"{g}{p}", "recipiente": g, "grupo": g, "posicao": p}
             for g in GRUPOS for p in range(1, POR_GRUPO + 1)]
    return {"vagas": vagas, "equipes": EQUIPES, "evitar": True}


def main(n):
    onde = Counter()
    for _ in range(n):
        m = Mesa(categoria())
        m.conferir()
        while not m.concluida:
            m.sortear_equipe()
            m.sortear_posicao()
        por_grupo = {}
        for b in m.bolas:
            por_grupo.setdefault(b["grupo"], []).append(b["secretaria"])
            onde[(b["equipe"], b["grupo"])] += 1
        for g, secs in por_grupo.items():
            assert len(secs) == len(set(secs)), f"regra violada no grupo {g}: {secs}"

    esperado = n / len(GRUPOS)
    qui = sum((onde[(e["equipe"], g)] - esperado) ** 2 / esperado for e in EQUIPES for g in GRUPOS)
    gl = len(EQUIPES) * (len(GRUPOS) - 1)
    z = (qui - gl) / math.sqrt(2 * gl)
    print(f"{n} sorteios completos: regra de secretaria respeitada em todos, nenhum travou")
    print(f"cada equipe deveria cair em cada grupo ~{esperado:.0f} vezes; "
          f"caiu entre {min(onde.values())} e {max(onde.values())}")
    print(f"qui-quadrado = {qui:.1f} com {gl} graus de liberdade  (z = {z:+.2f})")
    ok = abs(z) < 3.5
    print("RESULTADO:", "distribuição compatível com sorteio justo" if ok
          else "ATENÇÃO: diferença maior do que o acaso explica")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(int(sys.argv[1]) if len(sys.argv) > 1 else 20000))
