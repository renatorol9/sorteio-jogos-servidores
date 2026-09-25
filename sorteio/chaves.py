"""Núcleo do sorteio das CHAVES dos Jogos dos Servidores de Boa Vista (2026).

Este arquivo é exatamente o que o sistema usa no dia: o programa do sorteio importa `Mesa` daqui.

Como o sorteio funciona, bola a bola, nada calculado antes:

1. **Sorteio duplo.** Primeiro sai QUEM (uma equipe do pote), depois sai ONDE (uma vaga entre
   as possíveis). Os dois na hora.
2. **Entropia do sistema operacional** (`random.SystemRandom`, que lê `os.urandom`). Não há
   semente: ninguém — nem quem opera — consegue prever ou repetir um resultado.
3. **Regra de secretaria.** Quando a categoria pede, duas equipes da mesma secretaria não caem
   no mesmo grupo/jogo. Antes de cada bola de POSIÇÃO o motor calcula quais vagas ainda deixam
   o sorteio terminar (`cabe`) e sorteia só entre essas — sem isso, a última bola poderia não
   ter lugar válido e o sorteio teria de ser refeito na frente de todos.
4. **A prova é o registro:** cada bola é gravada com a hora em que saiu (a ata, em `atas/`).

Por que sortear a equipe primeiro é seguro: se o estado é viável, existe uma distribuição que
coloca todas as equipes que faltam; nela, CADA equipe restante ocupa alguma vaga — logo qualquer
equipe do pote tem pelo menos uma vaga possível. Quem passa pela conferência é a bola da posição.

Vocabulário: `vaga` é um lugar ("A1", ou "Preliminar 3, lado a"); `recipiente` é o que a regra
de secretaria protege (o grupo, ou o jogo).
"""
from __future__ import annotations

import random
from collections import Counter

ACASO = random.SystemRandom()


# ------------------------------------------------------------ a viabilidade

def cabe(restantes: list[str], capacidade: dict[str, int],
         secretarias: dict[str, set[str]], evitar: bool) -> bool:
    """Ainda dá para colocar TODAS as equipes que faltam?

    `restantes` é a lista de SIGLAS das equipes que ainda estão no pote — só a
    sigla importa, porque a única regra que amarra é a da secretaria.

    Backtracking simples. As categorias por grupos têm no máximo 17 equipes,
    então a busca é instantânea; um algoritmo mais esperto só acrescentaria uma
    chance de estar errado num lugar onde errar é caro.
    """
    if not restantes:
        return True

    # Peneira barata ANTES da busca, e ela sozinha decide os casos grandes.
    #
    # A busca exaustiva é exponencial. Com 17 equipes isso é instantâneo; com as
    # 52 duplas do tênis de mesa masculino o programa simplesmente não volta —
    # foi o que travou no primeiro teste.
    #
    # A peneira é a condição de Hall para este formato: uma secretaria com k
    # equipes restantes precisa de k recipientes distintos que ainda tenham
    # espaço e ainda não a contenham. Ela é necessária sempre, e para
    # recipientes pequenos (2 ou 3 lugares, que é todo o mata-mata e quase todos
    # os grupos) também é suficiente — por isso os casos grandes param aqui.
    livres = {g: n for g, n in capacidade.items() if n > 0}
    if sum(livres.values()) < len(restantes):
        return False
    if evitar:
        for sec, k in Counter(restantes).items():
            if sum(1 for g in livres if sec not in secretarias[g]) < k:
                return False
    if len(restantes) > 20:
        return True

    # a equipe mais difícil primeiro: é ela que corta a busca cedo
    def opcoes(sec):
        return [g for g, n in capacidade.items()
                if n > 0 and not (evitar and sec in secretarias[g])]

    i = min(range(len(restantes)), key=lambda k: len(opcoes(restantes[k])))
    sec = restantes[i]
    resto = restantes[:i] + restantes[i + 1:]
    for g in opcoes(sec):
        capacidade[g] -= 1
        novo = sec not in secretarias[g]
        secretarias[g].add(sec)
        ok = cabe(resto, capacidade, secretarias, evitar)
        capacidade[g] += 1
        if novo:
            secretarias[g].discard(sec)
        if ok:
            return True
    return False


def diagnostico(restantes: list[str], recipientes: list[str]) -> str:
    """Por que esta categoria não fecha — com o número na mão.

    Dizer só "impossível" faria a comissão descobrir o motivo no braço. Quase
    sempre é uma secretaria com mais equipes do que recipientes onde caber."""
    conta = Counter(restantes)
    pior, quantas = max(conta.items(), key=lambda x: x[1])
    return (f"a {pior} tem {quantas} equipes e a categoria tem {len(recipientes)} "
            f"grupos/jogos. Com uma equipe por secretaria em cada um não há como "
            f"distribuir: a comissão precisa decidir se abre exceção ou se muda o formato.")



class Impossivel(Exception):
    """A categoria não fecha com as equipes que tem. Quem decide é a comissão."""


class Mesa:
    """O sorteio de UMA categoria, em andamento.

    Guarda só o que já aconteceu (as bolas) e deriva o resto. Assim recuperar um
    sorteio interrompido é reaplicar as bolas gravadas, sem estado escondido.
    """

    def __init__(self, cat: dict):
        self.cat = cat
        self.vagas = cat["vagas"]
        self.evitar = cat.get("evitar", True)
        self.bolas: list[dict] = []        # equipe + vaga, na ordem em que saíram
        self.pendente: dict | None = None  # equipe sorteada, vaga ainda não

    # ----- leitura do estado

    @property
    def ocupadas(self) -> dict[str, dict]:
        return {b["chave"]: b for b in self.bolas}

    @property
    def livres(self) -> list[dict]:
        ocupadas = self.ocupadas
        return [v for v in self.vagas if v["chave"] not in ocupadas]

    @property
    def pote(self) -> list[dict]:
        """Quem ainda não saiu. A equipe pendente já saiu do pote — ela está na
        mão, esperando a segunda bola."""
        fora = {b["equipe"] for b in self.bolas}
        if self.pendente:
            fora.add(self.pendente["equipe"])
        return [e for e in self.cat["equipes"] if e["equipe"] not in fora]

    @property
    def concluida(self) -> bool:
        return len(self.bolas) >= len(self.vagas)

    def capacidade(self) -> dict[str, int]:
        cap = {v["recipiente"]: 0 for v in self.vagas}
        for v in self.livres:
            cap[v["recipiente"]] += 1
        return cap

    def secretarias(self) -> dict[str, set[str]]:
        secs = {v["recipiente"]: set() for v in self.vagas}
        for b in self.bolas:
            secs[b["recipiente"]].add(b["secretaria"])
        return secs

    # ----- a conferência

    def conferir(self):
        """O sorteio inteiro ainda termina? Chamado antes da primeira bola.

        Uma categoria impossível tem que ser recusada AGORA, com o número na
        mão, e não no meio da revelação."""
        n, v = len(self.cat["equipes"]), len(self.vagas)
        if n != v:
            # faltando: quase sempre é secretaria que ainda não indicou quais
            # times entram (prazo 28/09). Sobrando: aí é o formato que está
            # montado para menos gente do que se inscreveu.
            raise Impossivel(
                f"são {n} equipes para {v} vagas. " + (
                    "Falta secretaria indicar quais times entram, ou o formato está montado "
                    "para mais gente do que se inscreveu." if n < v else
                    "O formato está montado para menos gente do que se inscreveu e "
                    "precisa ser refeito."))
        restantes = [e["secretaria"] for e in self.pote]
        if not cabe(restantes, self.capacidade(), self.secretarias(), self.evitar):
            raise Impossivel(diagnostico(restantes, list(self.capacidade())))

    def vagas_possiveis(self, secretaria: str) -> list[dict]:
        """As vagas em que esta equipe pode entrar SEM fechar a porta para quem
        ainda está no pote.

        A viabilidade depende do recipiente (grupo ou jogo), não da vaga: se o
        Grupo B serve, qualquer posição livre do Grupo B serve igual. Por isso a
        conferência roda uma vez por recipiente — com 17 equipes e 6 grupos são
        6 buscas em vez de 17."""
        cap, secs = self.capacidade(), self.secretarias()
        resto = [e["secretaria"] for e in self.pote]
        bons = set()
        for rec, n in cap.items():
            if n == 0 or (self.evitar and secretaria in secs[rec]):
                continue
            cap[rec] -= 1
            novo = secretaria not in secs[rec]
            secs[rec].add(secretaria)
            if cabe(resto, cap, secs, self.evitar):
                bons.add(rec)
            cap[rec] += 1
            if novo:
                secs[rec].discard(secretaria)
        return [v for v in self.livres if v["recipiente"] in bons]

    # ----- as duas bolas

    def sortear_equipe(self, acaso=ACASO) -> dict:
        """PRIMEIRA BOLA: quem sai do pote. Aleatória entre todas as restantes —
        o estado viável garante que qualquer uma delas cabe em algum lugar."""
        if self.pendente:
            raise Impossivel("já há uma equipe sorteada esperando a posição.")
        pote = self.pote
        if not pote:
            raise Impossivel("o pote está vazio.")
        e = acaso.choice(pote)
        self.pendente = {"equipe": e["equipe"], "secretaria": e["secretaria"],
                         "ordem": len(self.bolas) + 1}
        return dict(self.pendente)

    def sortear_posicao(self, acaso=ACASO) -> dict:
        """SEGUNDA BOLA: onde ela entra. Aleatória entre as vagas possíveis.

        Sorteia a VAGA, e não o grupo: num sorteio de bolinhas é assim, cada
        lugar livre é uma bolinha. Sortear o grupo e depois preencher a próxima
        posição dele daria a um grupo de 3 a mesma chance de um de 4, e os
        grupos pequenos encheriam primeiro."""
        if not self.pendente:
            raise Impossivel("não há equipe na mão: sorteie a equipe primeiro.")
        possiveis = self.vagas_possiveis(self.pendente["secretaria"])
        if not possiveis:
            # Só acontece se o estado já estava inviável — a conferência prévia
            # existe para isso nunca chegar aqui.
            raise Impossivel(
                f"sem vaga possível para {self.pendente['equipe']} "
                f"({self.pendente['secretaria']}).")
        v = acaso.choice(possiveis)
        bola = dict(self.pendente, **{k: val for k, val in v.items()},
                    opcoes=len(possiveis))
        self.pendente = None
        self.bolas.append(bola)
        return bola

    def aplicar(self, bola: dict):
        """Recoloca no tabuleiro uma bola que já foi gravada (retomada)."""
        self.bolas.append(bola)
