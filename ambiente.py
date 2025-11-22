import numpy as np

from utils import generate_perlin_noise_2d
from settings import CMAP, meat_list, mekos_list
from logger import *

class Ambiente:
    """
    Classe que representa o objeto ambiente.
    
    Attributes:
        size (int): O tamanho do ambiente (size x size).
        matriz (np.ndarray): A matriz que representa o ambiente.
        mekos (list): A lista de objetos Meko presentes no ambiente.
    
    Methods:
        `adicionar_meko`: Adiciona um objeto Meko à lista de mekos.
        `tick`: Atualiza o estado do ambiente e dos mekos.
        `renderizar`: Renderiza o ambiente e os mekos em um gráfico.
    """
    def __init__(self, size, matriz = None, logger = None, mekos = []):
        # Atributos do Ambiente
        self.size = size
        self.matriz = matriz
        self.mekos = mekos
        self.logger = logger
        
        #Variáveis de controle
        self.nascimentos_tick = 0
        self.total_nascimentos = 0
        self.total_mortes_combate = 0
        self.total_mortes_fome = 0
        self.total_mortes_idade = 0

    def adicionar_meko(self, meko):
        """
        Adiciona um objeto Meko à lista de mekos.
        """
        self.nascimentos_tick += 1
    
        self.mekos.append(meko)
        
    def morte_meko(self, meko, causa = "Desconhecida"):
        """
        Contabiliza a morte de um Meko.
        """
        
        if causa == 'Combate':
            self.total_mortes_combate += 1
        elif causa == 'Fome':
            self.total_mortes_fome += 1
        elif causa == 'Idade':
            self.total_mortes_idade += 1
            
        if meko in mekos_list:
            mekos_list.remove(meko)

        log = f"{meko.nome} morreu. Causa: {causa}."
        meko.log.append(log)

    def tick(self,tick):
        """
        Atualiza o estado do ambiente e dos mekos.
        
        Para cada objeto na lista de mekos no ambiente, verifica se ele está na lista global `mekos_list`.
        Se não estiver, adiciona-o à lista chamando a função `adicionar_meko`.
        
        Em seguida, para cada objeto na lista de mekos, verifica se ele está vivo.
        Se estiver vivo, chama o método `update` do objeto `Meko`. Caso contrário, remove o objeto da lista local de mekos,
        cria um objeto `Carne` na posição do meko morto, adiciona-o à lista global de carnes, remove o Meko da lista global de mekos e imprime uma mensagem indicando que o Meko morreu.
        """
        mekos_remover = []
        
        for meko in self.mekos:
            meko.idade += 1
            if not meko.esta_vivo():
                mekos_remover.append(meko)
            else:   
                meko.update()
                self.logger.log_meko_data(tick, meko)
                meko.log = []
                
        for meko in mekos_remover:
            
            meat = Carne(meko.posicao)
            meat_list.append(meat)
            
            if meko in self.mekos:
                self.mekos.remove(meko)
        
        self.total_nascimentos += self.nascimentos_tick
        # if len(self.mekos) <= 0:
        #     self.logger.log_geral_final_.append({
        #     "tick_extincao": tick,
        # })
        self.logger.log_geral_tick(tick, mekos_list, self.nascimentos_tick)
        self.nascimentos_tick = 0

    def renderizar(self, ax):
        """
        Renderiza o ambiente e os mekos em um gráfico.
        
        Args:
            ax (matplotlib.axes.Axes): O eixo do gráfico onde o ambiente será renderizado
        
        Return:  
            Limpa o eixo fornecido, exibe a matriz do ambiente como uma imagem usando um mapa de cores definido (CMAP),
            e itera sobre a lista de mekos para desenhá-los na imagem. Cada meko é representado por um ponto vermelho se estiver vivo,
            ou cinza se estiver morto, com seu nome exibido no centro do ponto.
        """
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

class Carne:
    """
    Classe que representa a carne deixada por mekos mortos. Os objetos são gerados na posição do meko assim que ele morre.
    Attributes:
        posicao (tuple[int, int]): A posição da carne no ambiente.
        nome (string): O nome da carne, gerado a partir de sua posição.
        quant (int): A quantidade atual de carne disponível.
        
    Methods:
        acabar: Remove a carne da lista global se a quantidade chegar a zero.
    """
    def __init__(self, posicao):
        x, y = posicao
        self.nome = str("meat" + str(x) + str(y))
        self.posicao = posicao
        self.quant = np.random.randint(1, 4)

    def acabar(self):
        if self.quant <= 0:
            meat_list.remove(self)

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
