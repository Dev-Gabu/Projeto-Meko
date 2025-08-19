from PIL import Image
import numpy as np

from settings import LOC_CARACTERISTICAS

class GenomaInvalidoError(Exception):
    """Erro lançado quando o genoma possui alguma característica/gene que é inválido."""
    pass

def validar_genoma(genoma):
    """
    Valida um genoma baseado nas características obrigatórias.
    
    Args:
        genoma (list[str]): Lista de 10 características na ordem:
            [0] Tipo - "Fogo", "Agua", "Terra", "Inseto", "Sombra", "Luz"
            [1] Alimentação - "Herbivoro", "Carnivoro", "Onivoro"
            [2] Tamanho - "Pequeno", "Medio", "Grande"
            [3] Olhos - "Simples", "Avançado", "Compostos"
            [4] Presas - "Nenhuma", "Pequena", "Media", "Grande"
            [5] Patas - "Apode", "Bipede", "Quadrupede", "Multipede"
            [6] Garras - "Nenhuma", "Curta", "Longa", "Retrateis"
            [7] Cauda - "Nenhuma", "Equilibrio", "Ataque", "Aquatica"
            [8] Defesa - "Nenhuma", "Carapaça", "Escamas", "Pelagem"
            [9] Extra - "Nenhuma", "Camuflagem", "Veneno", "Bioluminescencia", "Campo-eletrico"

    Raises:
        TypeError: O genoma deve conter uma ``list`` de ``string`` que represente as características de uma criatura.
        ValueError: O genoma recebido tem tamanho incompativel
        GenomaInvalidoError: O valor do gene fornecido nao corresponde as caracteristicas permitidas.

    Return:
        True: O genoma foi validado com sucesso.

    """

    if not isinstance(genoma, list):
        raise TypeError("Genoma deve ser uma lista de strings")
    if not all(isinstance(g, str) for g in genoma):
        raise TypeError("Todos os elementos do genoma devem ser strings")



    # Lista de valores válidos para cada índice
    valores_validos = [
        {"Fogo", "Agua", "Terra", "Inseto", "Sombra", "Luz"},
        {"Herbivoro", "Carnivoro", "Onivoro"},
        {"Pequeno", "Medio", "Grande"},
        {"Simples", "Avancado", "Compostos"},
        {"Nenhuma", "Pequena", "Media", "Grande"},
        {"Apode", "Bipede", "Quadrupede", "Multipede"},
        {"Nenhuma", "Curta", "Longa", "Retrateis"},
        {"Nenhuma", "Equilibrio", "Ataque", "Aquatica"},
        {"Nenhuma", "Carapaca", "Escamas", "Pelagem"},
        {"Nenhuma","Camuflagem", "Veneno", "Bioluminescencia", "Campo-eletrico"}
    ]

    # Checar tamanho do genoma
    if len(genoma) != len(valores_validos):
        raise ValueError("Tamanho do genoma fornecido e incompetivel")

    # Checar cada característica
    for i, valor in enumerate(genoma):
        # Característica não listada:
        if valor not in valores_validos[i]:
            raise GenomaInvalidoError(f"Posicao {i} contem valor invalido, '{valor}' (Valores validos: {valores_validos[i]}).")
        # Olhos Compostos:
        if valor == "Compostos" and genoma[0] != "Inseto":
            raise GenomaInvalidoError("Olhos Compostos só são válidos para Insetos.")
        # Garras em ápodes:
        if genoma[5] == "Apode" and genoma[6] != "Nenhuma":
            raise GenomaInvalidoError("Garras só são válidas para criaturas com patas.")

    return True

def sprite_por_genoma(genoma):
        
        """
        Gera uma imagem composta de um Meko a partir do genoma.
        """
        categorias = ["Tipo", "Alimentacao", "Tamanho", "Olhos", "Presas", "Patas", "Garras", "Cauda", "Defesa", "Extra"]
        sprite_final = None

        for i, cat in enumerate(categorias):
            caracteristica = genoma[i]
            if cat == "Garras":
                tipo_patas = genoma[5]
                chave_sprite = f"{tipo_patas}_{caracteristica}"
                caminho = LOC_CARACTERISTICAS[cat].get(chave_sprite)
                if caminho is None:
                    continue
                try:
                    camada = Image.open(caminho).convert("RGBA")
                except (FileNotFoundError, OSError):
                    camada = None
                    continue
            else:
                caminho = LOC_CARACTERISTICAS[cat].get(caracteristica)
                if caminho is None:
                    continue
                try:
                    camada = Image.open(caminho).convert("RGBA")
                except (FileNotFoundError, OSError):
                    camada = None
                    continue
                if camada is None:
                    continue
            if sprite_final is None:
                if camada is None:
                    continue
                sprite_final = camada
            else:
                sprite_final = Image.alpha_composite(sprite_final, camada)
        return sprite_final

## Perlin Noise

def fade(t):
    """
    Função de interpolação suave (fade) para o Perlin Noise.

    Essa função suaviza a transição entre pontos.

    É um polinômio de 5ª ordem que tem derivada `0` em `0` e `1`, garantindo continuidade suave.

    Serve para evitar "quebras" bruscas na interpolação, deixando o ruído mais natural.

    Exemplo: se `t` vai de `0 → 1`, a função suaviza a progressão para não ser linear.
    """
    return 6*t**5 - 15*t**4 + 10*t**3

def lerp(a, b, x):
    """
    Linear interpolation (LERP): interpola entre dois valores `a` e `b` com base em `x ∈ [0,1]`.

    Se `x=0` → retorna `a`; se `x=1` → retorna `b`; valores intermediários dão uma mistura proporcional.
    """
    return a + x * (b - a)

def grad(hash, x, y):
    """
    Calcula o vetor gradiente em cada canto da célula da grade.

    `hash & 3` limita os valores possíveis para `0–3` → escolhe uma direção de gradiente.

    Dependendo do ``hash``, decide se o gradiente aponta mais para ``x`` ou para ``y``.

    Retorna um valor proporcional ao ponto (``x``, ``y``) projetado nesse gradiente.
    """
    h = hash & 3
    u = x if h < 2 else y
    v = y if h < 2 else x
    return (u if (h & 1) == 0 else -u) + (v if (h & 2) == 0 else -v)

def perlin(x, y, perm):
    """
    ``xi``,``yi``: pega a posição da célula (inteiro).

    ``xf``, ``yf``: pega a posição dentro da célula (fração).

    ``u``, ``v``: aplica ``fade()`` para suavizar transição.

    Busca quatro valores pseudo-aleatórios da tabela ``perm`` (permutação), correspondendo aos cantos da célula.

    Calcula gradientes (``grad``) para cada canto.

    Faz duas interpolações horizontais (``x1``, ``x2``) com ``lerp``.

    Interpola entre ``x1`` e ``x2`` verticalmente.

    Normaliza o resultado para ``[0,1]``.
    """

    xi = int(x) & 255
    yi = int(y) & 255
    xf = x - int(x)
    yf = y - int(y)
    u = fade(xf)
    v = fade(yf)

    aa = perm[perm[xi] + yi]
    ab = perm[perm[xi] + yi + 1]
    ba = perm[perm[xi + 1] + yi]
    bb = perm[perm[xi + 1] + yi + 1]

    x1 = lerp(grad(aa, xf, yf), grad(ba, xf - 1, yf), u)
    x2 = lerp(grad(ab, xf, yf - 1), grad(bb, xf - 1, yf - 1), u)
    return (lerp(x1, x2, v) + 1) / 2  # Normaliza para [0,1]

def generate_perlin_noise_2d(shape, scale=10, seed=0):
    """
    Gera uma matriz ``shape=(altura, largura)`` com valores de ruído.

    Cria uma tabela de permutação (``perm``) para garantir pseudo-aleatoriedade.

    Normaliza coordenadas ``(i, j)`` pela escala → controla a "frequência" do ruído.

    Para cada ponto da matriz, chama ``perlin(x, y, perm)`` e guarda o valor.

    Retorna a matriz com valores suaves entre ``0`` e ``1``.
    """

    np.random.seed(seed)
    perm = np.arange(256, dtype=int)
    np.random.shuffle(perm)
    perm = np.stack([perm, perm]).flatten()
    noise = np.zeros(shape)
    for i in range(shape[0]):
        for j in range(shape[1]):
            x = i / scale
            y = j / scale
            noise[i][j] = perlin(x, y, perm)
    return noise

