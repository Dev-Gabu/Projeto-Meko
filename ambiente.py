import numpy as np

from utils import generate_perlin_noise_2d
from settings import CMAP

class Ambiente:
    def __init__(self, size, matriz = None, mekos = []):
        self.size = size
        self.matriz = matriz if matriz is not None else np.random.choice([0, 1, 2], size=(size, size), p=[0.2, 0.3, 0.5])
        self.mekos = mekos

    def adicionar_meko(self, meko):
        self.mekos.append(meko)

    def tick(self):
        for meko in self.mekos:
            if meko.esta_vivo():
                meko.update(self.matriz)
            else:
                print(f"{meko.nome} morreu.")
    
    def renderizar(self, ax):
        ax.clear()
        ax.imshow(self.matriz, cmap=CMAP, interpolation="none")

        for meko in self.mekos:
            if meko.esta_vivo():
                i, j = map(int, meko.posicao)
                ax.scatter(j, i, c="red", s=100, alpha=0.6, marker="o")
                ax.text(j, i, meko.nome, color="white", ha="center", va="center", weight="bold")
            else:
                i, j = map(int, meko.posicao)
                ax.scatter(j, i, c="gray", s=100, alpha=0.6, marker="o")
                ax.text(j, i, meko.nome, color="white", ha="center", va="center", weight="bold")

class Fruta:
    """
    Classe que representa as frutas. Os objetos são gerados nas áreas de recursos no ambiente.

    Attributes:
        posicao (tuple[int, int]): A posição da fruta no ambiente.
        nome (string): O nome da fruta, gerado a partir de sua posição.
        quantMAX (int): A quantidade máxima de frutas que podem ser geradas.
        quant (int): A quantidade atual de frutas disponíveis.
        recarga (int): Índice de contagem do tempo de recarga.

    Methods:
        recarregar: Recarrega a fruta após um tempo de espera.
    """
    def __init__(self, posicao):
        self.posicao = posicao
        x,y = posicao
        self.nome = str("fruit" + str(x) + str(y))
        self.quantMAX = 3
        self.quant = 1
        self.recarga = 0

    def recarregar(self):
        if self.recarga >= 15:
            self.quant = min(self.quant + 1, self.quantMAX)
        else: self.recarga += 1

#TODO Documentar depois que implementar
class Carne:
    def __init__(self, posicao):
        self.posicao = posicao
        self.quant = np.random.randint(1, 4)
        self.podridao = 0

    def apodrecer(self):
        if self.podridao >= 15:
            self.quant -=1
        else: self.podridao += 1

def biome_gen(grid, size, n_biomas=4, scale=10.0, seed=None, biome_weights=None):
    """
    Função para separação de terreno baseada em Perlin Noise.

    Gera um mapa de Perlin Noise e distribui os biomas de acordo com faixas do ruído,
    criando regiões naturais e homogêneas. Em seguida, aplica uma suavização local.

    Args:
        grid (matriz): Matriz de terrenos (será sobrescrita).
        size (int): Tamanho da matriz.
        n_biomas (int): Número de biomas diferentes (ex: 3).
        scale (float): Escala do Perlin Noise.
        seed (int, opcional): Semente para geração aleatória.
        biome_weights (list, opcional): Pesos para cada bioma.

    Returns:
        new_grid: Matriz resultante com biomas distribuídos.
    """

    # Definição da Seed
    if seed is None:
        seed = np.random.randint(0, 10000)

    noise_map = generate_perlin_noise_2d((size, size), scale=scale, seed=seed)
   
   # Separação de Biomas
    
    if biome_weights is None:
        biome_weights = [0.2, 0.2, 0.4, 0.2]
    thresholds = np.cumsum([0] + biome_weights)


    new_grid = np.zeros_like(grid)
    for b in range(n_biomas):
        mask = (noise_map >= thresholds[b]) & (noise_map < thresholds[b+1])
        new_grid[mask] = b

    # Suavização
    for _ in range(2):
        temp_grid = new_grid.copy()
        for i in range(size):
            for j in range(size):
                neighbors = temp_grid[max(0, i-1):min(size, i+2),
                                      max(0, j-1):min(size, j+2)].flatten()
                counts = np.bincount(neighbors.astype(int), minlength=n_biomas)
                current = temp_grid[i, j].astype(int)
                counts[current] -= 1
                max_type = np.argmax(counts)
                if max_type != current and counts[max_type] > 3:
                    if np.random.rand() < 0.7:
                        new_grid[i, j] = max_type
    return new_grid.astype(int)

def fruit_gen(grid,size):

    """
    Função para distribuição aleatória de recursos.

    Função para distribuição aleatória de recursos, com probabilidade dependente do bioma.

    Args:
        grid (matriz): Recebe a matriz de terrenos.
        size (int): Tamanho da matriz.

    Returns:
        new_grid: Retorna a matriz resultante depois de uma iteração do algoritmo de distribuição.

    """

    # Definição de Probabilidades
    bioma_probs = [0, 0.02, 0.03, 0.001]
        #[deserto, campo, floresta, montanha]

    new_grid = grid.copy()
    for i in range(size):
        for j in range(size):
            bioma = new_grid[i, j]
            if bioma < len(bioma_probs):
                prob = bioma_probs[bioma]
                if np.random.rand() < prob:
                    new_grid[i, j] = 4
    return new_grid.astype(int)

def river_gen(grid, size, i = 0, j = None, chance = 0.06):
    """
    Função para geração de rios.

    Usa o algoritmo de Random Walk (Caminhada aleatória) que vai do ponto inicial (0 por padrão) e segue em direção a um ponto aleatório na linha inferior da grade.

    Inicia com uma chance aleatória (0.06 por padrão) de convergir, criando uma bifurcação no rio. Ao convergir, a chance de convergir novamente cai pela metade para ambas as instâncias.

    Args:
        grid (matriz): Recebe a matriz de terrenos.
        size (int): Tamanho da matriz.
        i (int, optional): Posição inicial na linha vertical. Padrão é 0 (topo).
        j (int, optional): Posição inicial na linha horizontal. Padrão é None (aleatório).
        chance (float, optional): Chance inicial de bifurcação. Padrão é 0.06.

    """
    if (j == None): 
        j = np.random.randint(0, size)

    while i < size:
        grid[i, j] = 5 
        grid[i, j-1] = 5
        direcao = np.random.choice([-1, 0, 1], p=[0.35, 0.3, 0.35])
        j = np.clip(j + direcao, 0, size-1)
        i += 1

        if np.random.rand() < chance and chance > 0:
            chance = chance * 0.5
            river_gen(grid, size, i, j, chance)
            
    return grid
