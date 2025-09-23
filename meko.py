import random

from utils import validar_genoma, distancia
from settings import EFEITOS, GRID_SIZE
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
        self.temperatura = 30

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

    def __init__(self, nome, genoma, posicao = (0,0),idade = 200):
     
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
        self.fertilidade = "Incapaz"

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
    
    def random_step(self):
        """
        Move o Meko aleatóriamente no intervalo do Grid
        """
        i, j = self.posicao
        step = 1 #min(1, random.randint(0, self.velocidade))
        i = (i + random.choice([-1, 0, 1])) * step
        j = (j + random.choice([-1, 0, 1])) * step
        if 0 <= i < GRID_SIZE and 0 <= j < GRID_SIZE:
            self.posicao = (i, j)
            self.energia -= step
        else: self.random_step()

    def search(self, objetos, tipo, breed = False):
        """
        Busca objetos de um tipo específico no raio de visão.
        objetos: lista de instâncias (Fruta, Carne, Meko, etc.)
        tipo: tipo de objeto a ser buscado
        """
        # Filtra apenas os que estão no raio de visão
        
        proximos = [
            obj for obj in objetos
            if distancia(self, obj) <= self.visao and obj != self and obj != self.target and obj.__class__.__name__ == tipo and breed == False or distancia(self, obj) <= self.visao and obj != self and obj != self.target and obj.__class__.__name__ == tipo and breed == True and obj.fertilidade == "Fertil" and obj.love == None
        ]

        if not proximos:
            return None

        # Ordena pelo mais próximo
        alvo = min(proximos, key=lambda o: distancia(self,o))
        
        #Retorna o alvo
        return alvo
    
    def gerar_filhote(self, nome, genoma):
        filhote = Meko(nome, genoma, posicao=self.posicao)
        mekos_list.append(filhote)
        print(f"Um novo Meko nasceu: {nome}")

    def update(self):
        """
        Atualiza a máquina de estados do Meko
        """
        
        self.energia -= 1
        self.idade += 1
        
        ## Dano por fome
        if self.energia <= 0:
            self.saude -= 5
            
        ## Fertilidade
        if self.idade > 30 and self.saude > self.saudeMAX * 0.5 and self.energia > self.energiaMAX * 0.5 and self.fertilidade == "Incapaz":
            self.fertilidade = "Fertil"
        else: 
            self.fertilidade = "Incapaz"

        self.fsm.update()