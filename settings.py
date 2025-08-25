from matplotlib.colors import ListedColormap, BoundaryNorm
import numpy as np

cores = ["#5C9128", "#277B12", "#0E5A28", "#6F4823", "#C47225", "#3B8B91"]
legendas = ["Deserto", "Campo", "Floresta", "Montanha", "Frutas", "Rios"]
CMAP = ListedColormap(cores)
bounds = np.arange(-0.5, len(cores)+0.5, 1)
NORM = BoundaryNorm(bounds, CMAP.N)

## AMBIENTE
GRID_SIZE = 10
SIMULATION_STEPS = 200

## MEKOS

LOC_CARACTERISTICAS = {

    # Lista com os endereços de sprites para cada característica dos Meko.

    "Tipo": {
        "Fogo": "assets/sprites/tipo_fogo.png",
        "Agua": "assets/sprites/tipo_agua.png",
        "Terra": "assets/sprites/tipo_terra.png",
        "Inseto": "assets/sprites/tipo_inseto.png",
        "Sombra": "assets/sprites/tipo_sombra.png",
        "Luz": "assets/sprites/tipo_luz.png"
    },
    "Tamanho": {
        "Pequeno": "assets/sprites/tamanho_pequeno.png",
        "Medio": "assets/sprites/tamanho_medio.png",
        "Grande": "assets/sprites/tamanho_grande.png"
    },
    "Alimentacao": {
        "Herbivoro": "assets/sprites/alimentacao_herbivoro.png",
        "Carnivoro": "assets/sprites/alimentacao_carnivoro.png",
        "Onivoro": "assets/sprites/alimentacao_onivoro.png"
    },
    "Olhos": {
        "Simples": "assets/sprites/olhos_simples.png",
        "Avancado": "assets/sprites/olhos_avancado.png",
        "Compostos": "assets/sprites/olhos_compostos.png"
    },
    "Presas": {
        "Pequena": "assets/sprites/presas_pequena.png",
        "Media": "assets/sprites/presas_media.png",
        "Grande": "assets/sprites/presas_grande.png"
    },
    "Patas": {
        "Bipede": "assets/sprites/patas_bipede.png",
        "Quadrupede": "assets/sprites/patas_quadrupede.png",
        "Multipede": "assets/sprites/patas_multipede.png"
    },
    "Garras": {
        "Bipede_Curta": "assets/sprites/bipede_curta.png",
        "Bipede_Longa": "assets/sprites/bipede_longa.png",
        "Bipede_Retrateis": "assets/sprites/bipede_retrateis.png",
        "Quadrupede_Curta": "assets/sprites/quadrupede_curta.png",
        "Quadrupede_Longa": "assets/sprites/quadrupede_longa.png",
        "Quadrupede_Retrateis": "assets/sprites/quadrupede_retrateis.png",
        "Multipede_Curta": "assets/sprites/multipede_curta.png",
        "Multipede_Longa": "assets/sprites/multipede_longa.png",
        "Multipede_Retrateis": "assets/sprites/multipede_retrateis.png"
    },
    "Cauda": {
        "Equilibrio": "assets/sprites/cauda_equilibrio.png",
        "Ataque": "assets/sprites/cauda_ataque.png",
        "Aquatica": "assets/sprites/cauda_aquatica.png"
    },
    "Defesa": {
        "Carapaca": "assets/sprites/defesa_carapaca.png",
        "Escamas": "assets/sprites/defesa_escamas.png",
        "Pelagem": "assets/sprites/defesa_pelagem.png"
    },
    "Extra": {
        "Camuflagem": "assets/sprites/extra_camuflagem.png",
        "Veneno": "assets/sprites/extra_veneno.png",
        "Bioluminescencia": "assets/sprites/extra_bioluminescencia.png",
        "Campo-eletrico": "assets/sprites/extra_campo_eletrico.png"
    }
}

CARACTERISTICAS = [
    ("Tipo", ["Fogo", "Agua", "Terra", "Inseto", "Sombra", "Luz"]),
    ("Alimentacao", ["Herbivoro", "Carnivoro", "Onivoro"]),
    ("Tamanho", ["Pequeno", "Medio", "Grande"]),
    ("Olhos", ["Simples", "Avancado", "Compostos"]),
    ("Presas", ["Nenhuma", "Pequena", "Media", "Grande"]),
    ("Patas", ["Apode", "Bipede", "Quadrupede", "Multipede"]),
    ("Garras", ["Nenhuma", "Curta", "Longa", "Retrateis"]),
    ("Cauda", ["Nenhuma", "Equilibrio", "Ataque", "Aquatica"]),
    ("Defesa", ["Nenhuma", "Carapaca", "Escamas", "Pelagem"]),
    ("Extra", ["Nenhuma", "Camuflagem", "Veneno", "Bioluminescencia", "Campo-eletrico"])
]

## LISTAS
mekos_list = []
fruit_list = []
meat_list = []

## MODIFICADORES

efeitos_tipo = {
    "Fogo":         {"temperatura": 20, "agressividade": 4, "forca": 7},
    "Agua":         {"temperatura": -10, "velocidade": 5, "peso": -5},
    "Terra":        {"peso": 10, "forca": 3, "velocidade": -5, "resistencia": 5},
    "Inseto":       {"peso": -10, "velocidade": 5, "forca": -3, "resistencia": -5},
    "Sombra":       {"agressividade": 10, "velocidade": 5, "forca": 4},
    "Luz":          {"visao": 5, "velocidade": 4, "agressividade": -10}
}

efeitos_alimentacao = {
    "Herbivoro":    {"agressividade": -10, "resistencia": 5},
    "Carnivoro":    {"agressividade": 10, "resistencia": -5},
    "Onivoro":      {"velocidade": 4}
}

efeitos_tamanho = {
    "Pequeno":      {"peso": -10, "resistencia": -10, "velocidade": 4},
    "Medio":        {"peso": 4, "resistencia": 2, "velocidade": 2},
    "Grande":       {"peso": 10, "resistencia": 10, "velocidade": -4}
}

efeitos_olhos = {
    "Simples":      {"visao": 2},
    "Avancado":     {"visao": 4},
    "Compostos":    {"visao": 5}
}

efeitos_presas = {
    "Nenhuma":      {"forca": 0, "agressividade": -3, "peso": 0},
    "Pequena":      {"forca": 3, "agressividade": 0, "peso": 1},
    "Media":        {"forca": 5, "agressividade": 3, "peso": 2},
    "Grande":       {"forca": 8, "agressividade": 6, "peso": 3}
}

efeitos_patas = {
    "Apode":        {"peso": 0, "velocidade": -10, "resistencia": 0},
    "Bipede":       {"peso": 2, "velocidade": 9, "resistencia": 2},
    "Quadrupede":   {"peso": 4, "velocidade": 6, "resistencia": 4},
    "Multipede":    {"peso": 6, "velocidade": 3, "resistencia": 6}
}

efeitos_garras = {
    "Nenhuma":      {"forca": 0, "agressividade": -3, "peso": 0, "velocidade": 0},
    "Curta":        {"forca": 3, "agressividade": 2, "peso": 1, "velocidade": -3},
    "Longa":        {"forca": 5, "agressividade": 4, "peso": 2, "velocidade": -6},
    "Retrateis":    {"forca": 4, "agressividade": 3, "peso": 3, "velocidade": 0}
}

efeitos_cauda = {
    "Nenhuma":      {"peso": 0, "velocidade": 0, "resistencia": 0},
    "Equilibrio":   {"peso": 4, "velocidade": 5, "resistencia": 3},
    "Ataque":       {"peso": 5, "velocidade": 2, "forca": 4},
    "Aquatica":     {"peso": 4, "velocidade": 2, "resistencia": 2} # Implementar aumento de velocidade na água / redução de cansaço
}

efeitos_defesa = {
    "Nenhuma":      {"peso": 0, "velocidade": 0, "resistencia": 0},
    "Carapaça":     {"peso": 10, "velocidade": -5, "resistencia": 5},
    "Escamas":      {"peso": 5, "velocidade": -2, "resistencia": 2}, # Implementar aumento de velocidade na água / redução de cansaço
    "Pelagem":      {"peso": 6, "velocidade": -3, "resistencia": 4, "temperatura": -10}
}

efeitos_extras = {
    "Nenhuma":       {"peso": 0, "velocidade": 0, "resistencia": 0},
    "Camuflagem":       {"peso": 0, "velocidade": 0, "resistencia": 0}, # Menor chance de ser avistado no campo de visão
    "Veneno":           {"peso": 4, "velocidade": 5, "resistencia": 3}, # Aplica veneno, causa danos constantes
    "Bioluminescencia": {"peso": 5, "velocidade": 2, "forca": 4}, # Atrai criaturas
    "Campo-eletrico":   {"peso": 4, "velocidade": 2, "resistencia": 2} # Causa danos ao seu redor quando atacando
}

EFEITOS = [
    efeitos_tipo,
    efeitos_alimentacao,
    efeitos_tamanho,
    efeitos_olhos,
    efeitos_presas,
    efeitos_patas,
    efeitos_garras,
    efeitos_cauda,
    efeitos_defesa,
    efeitos_extras
]