"""Núcleo do sorteio das CORES das secretarias dos Jogos dos Servidores de Boa Vista (2026).

Este arquivo é exatamente o que o sistema usa no dia: o programa do sorteio importa `sortear_bola`.

Como funciona — dois sacos, como bolinhas:
- um saco com as secretarias que ainda não têm cor;
- um saco com as cores que ainda não foram dadas.
A cada bola sai UMA secretaria do primeiro saco e UMA cor do segundo, as duas ao acaso, com a
entropia do sistema operacional (`random.SystemRandom`, que lê `os.urandom`). Não há semente:
ninguém — nem quem opera — consegue prever ou repetir o resultado. Quem saiu não volta ao saco;
recomeçar o sorteio devolve todas as bolas (e o que saiu antes fica registrado na ata).
"""
from __future__ import annotations

import random

ACASO = random.SystemRandom()


def sortear_bola(secretarias_restantes: list[str], cores_restantes: list[dict], acaso=ACASO):
    """Uma bola: (secretaria, cor), cada uma sorteada no seu saco.

    As duas escolhas são independentes e uniformes: toda secretaria que está no saco tem a mesma
    chance de sair, e toda cor que está no saco também. Ao fim de um sorteio completo, portanto,
    qualquer uma das atribuições possíveis (24! delas, com 24 secretarias) é igualmente provável.
    """
    if not secretarias_restantes:
        raise ValueError("Todas as secretarias já têm cor.")
    if len(cores_restantes) < len(secretarias_restantes):
        raise ValueError("Há menos cores do que secretarias no saco.")
    return acaso.choice(secretarias_restantes), acaso.choice(cores_restantes)


def sortear_tudo(secretarias: list[str], cores: list[dict], acaso=ACASO) -> list[tuple[str, dict]]:
    """Um sorteio inteiro, bola a bola (usado pelos testes de imparcialidade)."""
    s_saco, c_saco, bolas = list(secretarias), list(cores), []
    while s_saco:
        s, c = sortear_bola(s_saco, c_saco, acaso)
        s_saco.remove(s)
        c_saco.remove(c)
        bolas.append((s, c))
    return bolas
