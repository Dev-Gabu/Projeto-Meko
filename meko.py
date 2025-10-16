import random
import numpy as np

from utils import gerar_nome, validar_genoma, distancia
from settings import CUSTO_TERRENO, EFEITOS, GRID_SIZE, TERRENO_FLORESTA, TERRENO_MONTANHA, TERRENO_RIO, C_ENERGIA, C_SAUDE, C_LONGEVIDADE
from FSM import *
from habilidades import *

class Meko:

    """As criaturas a serem observadas, seus atributos, características e comportamentos

    Os Meko contarão com um conjunto de atributos que estarão diretamente relacionados com a sua sobrevivência dentro do ambiente, suas interações com outros seres e com seus comportamentos.

    Attributes:
        nome (string): O nome é a identificação de cada indivíduo.
        genoma (list[str]): O genoma é  o conjunto de características de cada Meko.
        idade (int): A idade máxima de um indivíduo, que corresponde à quantidade de iterações que ele vai permanecer vivo antes de morrer naturalmente.
        posicao (tuple[int, int]): A posição atual do Meko no ambiente.
        target (obj): O objeto que o Meko está atualmente buscando ou atacando.
        saude (int): O valor que representa a sobrevivência, diminui ao ser atacado ou quando a energia está baixa (fome). Quando chegar a zero ou menos, o indivíduo morre.
        energia(int): O valor que representa a capacidade de agir, sendo gasta com o tempo, ao se mover, ao usar habilidades em combate ou reprodução.
        fertilidade(int): Representa a capacidade do indivíduo se reproduzir. Aumenta quanto mais próximo a temperatura do ambiente for do seu nível ideal e dependendo da sua idade.
        velocidade(int): Representa a distância que o indivíduo é capaz de se movimentar a cada iteração.
        peso(int): Afeta sua velocidade, força, resistência e gasto de energia.
        forca(int): Representa a quantidade de dano que o indivíduo pode causar em seus ataques.
        resistencia(int): Representa a quantidade de dano que o indivíduo pode reduzir dos ataques recebidos.
        visao(int): Representa a distância que o indivíduo pode ver outros objetos no ambiente.
        agressividade(int): Representa a pré-disposição do indivíduo a atacar outros indivíduos.
        temperatura(int): Representa a temperatura ideal para o indivíduo. Afeta a sua fertilidade e consumo de energia.

    """

    def gerar_atributos(self, genoma):
        """
        Gera os atributos iniciais de uma criatura a partir de seu genoma.

        Cada característica do genoma aplica modificadores aos atributos base,
        alterando valores como peso, velocidade, força e agressividade.

        Args:
            genoma (list[str]): Lista de 10 características na ordem:
                [0] Tipo - "Fogo", "Agua", "Terra", "Inseto", "Sombra", "Luz"
                [1] Alimentação - "Herbivoro", "Carnivoro", "Onivoro"
                [2] Tamanho - "Pequeno", "Medio", "Grande"
                [3] Olhos - "Simples", "Avancado", "Compostos"
                [4] Presas - "Nenhuma", "Pequena", "Media", "Grande"
                [5] Patas - "Apode", "Bipede", "Quadrupede", "Multipede"
                [6] Garras - "Nenhuma", "Curta", "Longa", "Retrateis"
                [7] Cauda - "Nenhuma", "Equilibrio", "Ataque", "Aquatica"
                [8] Defesa - "Nenhuma", "Carapaca", "Escamas", "Pelagem"
                [9] Extra - "Nenhuma", "Camuflagem", "Veneno", "Bioluminescencia", "Campo-eletrico"

        Modifica:
                self.atributos (dict): Dicionário com os atributos finais.
        """

        self.peso = 10
        self.velocidade = 10
        self.resistencia = 10
        self.forca = 4
        self.visao = 2
        self.agressividade = 0

        # Os modificadores são aplicados aos atributos

        for i, efeitos_dict in enumerate(EFEITOS):
            efeitos = efeitos_dict.get(genoma[i], {})
            for atributo, valor in efeitos.items():
                setattr(self, atributo, getattr(self, atributo) + valor)

    def gerar_habilidades(self, genoma):
        categorias_genoma = [
            "Tipo", "Alimentação", "Tamanho", "Olhos", "Presas",
            "Patas", "Garras", "Cauda", "Defesa", "Extra"
        ]

        habilidades_do_meko = []
        for i, categoria in enumerate(categorias_genoma):
            traco_genetico = genoma[i]
            if categoria in HABILIDADES_POR_GENOMA and \
               traco_genetico in HABILIDADES_POR_GENOMA[categoria]:
                habilidades_do_meko.extend(HABILIDADES_POR_GENOMA[categoria][traco_genetico])

        return habilidades_do_meko

    def __init__(self, nome, genoma, ambiente = None, posicao = (0,0),idade = 200):
        
        # Atributos de criação
        self.posicao = posicao
        self.genoma = genoma
        self.nome = nome
        self.idadeMAX = idade
        self.idade = 0

        # Atributos de controle
        self.saudeMAX = 70
        self.saude = 70
        self.energiaMAX = 200
        self.energia = 200
        self.fitness = 0
        self.ambiente = ambiente
        
        # Atributos de Reprodução
        self.fertilidade = "Incapaz"
        self.gestacao_contador = round(self.idadeMAX * 0.1)
        self.genoma_espera = None

        # Atributos de estado
        self.fsm = FSM(self)
        self.fsm.change_state(Wander())
        self.target = None
        self.love = None

        # Gerar Atributos
        if(validar_genoma(genoma)): self.gerar_atributos(genoma)

        #Gerar Habilidades
        self.habilidades = self.gerar_habilidades(genoma)

    def esta_vivo(self):
        """
        Verifica se o Meko está vivo com base em sua saúde.
        """
        return self.saude > 0 and self.idade < self.idadeMAX
    
    def calcular_fitness(self):
        """
        Calcula o Fitness baseado na Longevidade, Sobrevivência, Eficiência e Combate.
        Fórmula: Fitness = C_Idade * (I/IMAX) + C_Saude * (S/SMAX) + C_Energia * (E/EMAX) + C_Combate * (F + R)
        """
        
        longevidade_score = C_LONGEVIDADE * (self.idade / self.idadeMAX)
        saude_score = C_SAUDE * (self.saude / self.saudeMAX)
        energia_score = C_ENERGIA * (self.energia / self.energiaMAX)
        
        
        self.fitness = longevidade_score + saude_score + energia_score

        self.fitness = max(1.0, self.fitness)
    
    def calcular_custo_movimento(self):
        """
        Calcula o gasto extra de movimento devido ao terreno na posição atual.
        Retorna a penalidade de velocidade (int).
        """
        
        x, y = self.posicao
        tipo_terreno = self.ambiente.matriz[x, y] 
        
        penalidade = CUSTO_TERRENO.get(tipo_terreno, 0)

        if tipo_terreno == TERRENO_RIO:
            if any(habilidade.nome == "Nadar" for habilidade in self.habilidades):
                penalidade = 0 

        elif tipo_terreno == TERRENO_MONTANHA:
            if any(habilidade.nome == "Escalar" for habilidade in self.habilidades):
                penalidade = 0
                
        elif tipo_terreno == TERRENO_FLORESTA:
            if any(habilidade.nome == "Camuflagem" for habilidade in self.habilidades):
                penalidade = 0
                
        return penalidade
    
    def random_step(self):
        """
        Move o Meko aleatóriamente usando self.velocidade como distância máxima.
        """
        if self.ambiente is None:
            
            max_size = GRID_SIZE 
        else:
            max_size = self.ambiente.size
            
        i, j = self.posicao
        
        distancia_passo = random.randint(0, max(1,self.velocidade))
        di = random.choice([-1, 0, 1])
        dj = random.choice([-1, 0, 1])

        new_i = i + di * distancia_passo
        new_j = j + dj * distancia_passo
    
        new_i = np.clip(new_i, 0, max_size - 1)
        new_j = np.clip(new_j, 0, max_size - 1)

        if (new_i, new_j) != self.posicao:
            self.posicao = (new_i, new_j)
            self.energia -= distancia_passo

    def search(self, objetos, tipo, breed = False):
        """
        Busca objetos de um tipo específico no raio de visão.
        objetos: lista de instâncias (Fruta, Carne, Meko, etc.)
        tipo: tipo de objeto a ser buscado
        """
        # Filtra apenas os que estão no raio de visão
        
        print("Buscando por parceiro...")
        
        proximos = [
            obj for obj in objetos
            if distancia(self, obj) <= self.visao and obj != self and obj != self.target and obj.__class__.__name__ == tipo and breed == False or distancia(self, obj) <= self.visao and obj != self and obj != self.target and obj.__class__.__name__ == tipo and breed == True and obj.fertilidade == "Fertil" and obj.love == None
        ]

        if not proximos:
            return None

        # Ordena pelo mais próximo
        alvo = min(proximos, key=lambda o: distancia(self,o))
        
        #Retorna o alvo
        print("Retornando alvo...")
        return alvo
    
    def iniciar_gestacao(self, genoma_filhote, parceiro):
        """
        Inicia a gestação, armazenando o genoma e definindo o estado.
        O Meko que inicia a gestação fica impedido de reproduzir imediatamente.
        """
        self.gestacao_contador = 0
        self.genoma_espera = genoma_filhote
        self.fertilidade = "Gestante"
        
        if parceiro.love == self:
            parceiro.love = None
            
        self.love = None
        print(f"{self.nome} iniciou a gestação. Filhote nascerá em {int(self.idadeMAX * 0.05)} ticks.")


    def gerar_filhote(self, genoma_espera):
        """
        Cria o objeto Meko no ambiente, chamado no final da gestação.
        """
        genoma = genoma_espera[0]
        nome = genoma_espera[1]
        
        offset = random.choice([-1, 0, 1])
        posicao_nascimento = (
            np.clip(self.posicao[0] + offset, 0, self.ambiente.size - 1),
            np.clip(self.posicao[1] + offset, 0, self.ambiente.size - 1)
        )
        
        filhote = Meko(nome, genoma, ambiente=self.ambiente, posicao=posicao_nascimento, idade=1)
        self.ambiente.adicionar_meko(filhote)
        mekos_list.append(filhote) 
        print(f"Um novo Meko nasceu: {nome} na posição {filhote.posicao}")


    def update(self):
        """
        Atualiza a máquina de estados do Meko
        """
        
        self.energia -= 1
        self.idade += 1
        self.calcular_fitness()
        
        ## Dano por fome
        if self.energia <= 0:
            self.saude -= 5
            
        ## Fertilidade
        if self.idade > 30 and self.saude > self.saudeMAX * 0.5 and self.energia > self.energiaMAX * 0.5 and self.fertilidade == "Incapaz":
            self.fertilidade = "Fertil"
        else: 
            self.fertilidade = "Incapaz"
            
        ## Gestação

        if self.fertilidade == "Gestante":
            self.gestacao_contador += 1
            if self.gestacao_contador >= self.gestacao_contador:
                self.gerar_filhote(self.genoma_espera)
                self.gestacao_contador = 0
                self.genoma_espera = None
                self.fertilidade = "Incapaz"

        self.fsm.update()