from PIL import Image

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
        if valor not in valores_validos[i]:
            raise GenomaInvalidoError(f"Posicao {i} contem valor invalido, '{valor}' (Valores validos: {valores_validos[i]}).")
        
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