from utils import validar_genoma
from settings import EFEITOS

class Meko:

    """As criaturas a serem observadas, seus atributos, características e comportamentos

    Os Meko contarão com um conjunto de atributos que estarão diretamente relacionados com a sua sobrevivência dentro do ambiente, suas interações com outros seres e com seus comportamentos.

    Attributes:
        genoma (list[str]): O genoma é  o conjunto de características de cada Meko.

            [0] Tipo - "Fogo", "Agua", "Terra", "Inseto", "Sombra", "Luz"

            [1] Alimentação - "Herbivoro", "Carnivoro", "Onivoro"

            [2] Tamanho - "Pequeno", "Medio", "Grande"

            [3] Olhos - "Simples", "Avançado", "Compostos"

            [4] Presas - "Nenhuma", "Pequena", "Media", "Grande"

            [5] Patas - "Apode", "Bipede", "Quadrupede", "Multipede"

            [6] Garras - "Nenhuma", "Curta", "Longa", "Retrateis"

            [7] Cauda - "Nenhuma", "Equilibrio", "Ataque", "Aquatica"

            [8] Defesa - "Nenhuma", "Carapaça", "Escamas", "Pelagem"

            [9] Extra - "Nenhuma, Camuflagem", "Veneno", "Bioluminescencia", "Campo-eletrico"

        nome (string): O nome é a identificação de cada indivíduo.
        idade (int): A idade máxima de um indivíduo, que corresponde à quantidade de iterações que ele vai permanecer vivo antes de morrer naturalmente.
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

        self.peso = 10
        self.velocidade = 10
        self.resistencia = 10
        self.forca = 4
        self.visao = 2
        self.agressividade = 0
        self.temperatura = 30

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

        # Os modificadores são aplicados aos atributos

        for i, efeitos_dict in enumerate(EFEITOS):
            efeitos = efeitos_dict.get(genoma[i], {})
            for atributo, valor in efeitos.items():
                setattr(self, atributo, getattr(self, atributo) + valor)

    def __init__(self, nome, genoma, idade = 100):
     
        self.genoma = genoma
        self.saude = 100
        self.energia = 100
        self.fertilidade = 0
        self.nome = nome
        self.idade = idade

        if(validar_genoma(genoma)): self.gerar_atributos(genoma)
