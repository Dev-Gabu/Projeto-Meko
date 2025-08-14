import numpy as np

class Biome:
    # TODO Implementar e desenvolver características de bioma


    def __init__(self, nome, quant_recursos,temperatura):
        # Atributos (características do objeto)

        self.nome = nome
        self.quant_recursos =  quant_recursos
        self.temperatura = temperatura

def biome_gen(grid,size):
    """
    Função para separação de terreno.

    Essa função utiliza um algoritmo que, para cada posição no grid, observe sua vizinhança e calcule qual o valor com maior presença, mudando o seu próprio valor para o predominante com 70% de chance.

    Args:
        grid (matriz): Recebe a matriz com as sementes de terreno distribuídas aleatóriamente.
        size (int): Tamanho da matriz.

    Returns:
        new_grid: Retorna a matriz resultante depois de uma iteração do algoritmo de organização.

    """
    new_grid = grid.copy()
    for i in range(size):
        for j in range(size):
            neighbors = grid[max(0, i-1):min(size, i+2),
                             max(0, j-1):min(size, j+2)].flatten()
            
            counts = np.bincount(neighbors)
            
            current = grid[i, j]
            
            counts[current] -= 1  
            max_type = np.argmax(counts)
            
            if max_type != current and counts[max_type] > 3:
                if np.random.rand() < 0.7:
                    new_grid[i, j] = max_type
                    
    return new_grid.astype(int)

def fruit_gen(grid,size):

    """
    Função para distribuição aleatória de recursos.

    Essa função utiliza um algoritmo que, para cada posição no grid, calcula o valor da soma de seus vizinhos, calculando o valor de probabilidade de geração de algum recurso nessa posição com base no "nível de fertilidade" do terreno. 

    Args:
        grid (matriz): Recebe a matriz de terrenos.
        size (int): Tamanho da matriz.

    Returns:
        new_grid: Retorna a matriz resultante depois de uma iteração do algoritmo de distribuição.

    """
    new_grid = grid.copy()
    for i in range(size):
        for j in range(size):
            neighbors = grid[max(0, i-1):min(size, i+2),
                             max(0, j-1):min(size, j+2)]
            
            count = np.sum(neighbors)
            
            if np.random.rand() < 0.005 * count:
                    new_grid[i, j] = 3
                    
    return new_grid.astype(int)

