import random
from settings import TABELA_EFETIVIDADE_TIPO

## CLASSE GERAL

class Habilidade():
    
    def __init__(self, custo_energia, nome):
        self.custo_energia = custo_energia
        self.nome = nome
        
    def calcular_fraqueza(self,tipo,tipo_def):
        multiplicadores = TABELA_EFETIVIDADE_TIPO.get(tipo, {})
        return multiplicadores.get(tipo_def, 1.0) 
        
    def calcular_dano_base(self, atacante, alvo, dano_base):
        """
        Calcula o dano base padrão, usando Força e Resistência.
        Assume que a checagem de energia já foi feita.
        """
    
        return max(dano_base, dano_base + atacante.forca - alvo.resistencia)


    def execute(self, user, alvo):
        if self.custo_energia > user.energia:
            log = f"{user.nome} não tem energia suficiente para usar {self.nome}."
            user.log.append(log)
            return False
        user.energia -= self.custo_energia
        return True

## CLASSES ESPECIFICAS

## POR TIPO

class HabilidadeLancarBrasas(Habilidade):
    """
    Causa dano elemental de Fogo
    """
    def __init__(self):
        super().__init__(custo_energia=5,nome="Lançar Brasas")
        self.dano = 5

    def execute(self, atacante, alvo):
        if not super().execute(atacante, alvo):
            return

        dano_total = self.calcular_dano_base(atacante,alvo,self.dano) * self.calcular_fraqueza("Fogo",alvo.genoma[0])
        alvo.saude -= dano_total
        
        log = f"{atacante.nome} usa Lançar Brasas em {alvo.nome} e causa {dano_total} de dano."
        atacante.log.append(log)

class HabilidadeJatoDagua(Habilidade):
    """
    Causa dano elemental de Agua
    """
    def __init__(self):
        super().__init__(custo_energia=5,nome="Jato D'agua")
        self.dano = 5
    def execute(self, atacante, alvo):
        if not super().execute(atacante, alvo):
            return

        dano_total = self.calcular_dano_base(atacante,alvo,self.dano) * self.calcular_fraqueza("Agua",alvo.genoma[0])
        alvo.saude -= dano_total

        # Resposta
        log = f"{atacante.nome} usa Jato d'Água em {alvo.nome} e causa {dano_total} de dano."
        atacante.log.append(log)

class HabilidadeEnterrar(Habilidade):
    """
    Causa dano elemental de Terra
    """
    def __init__(self):
        super().__init__(custo_energia=5,nome="Enterrar")
        self.dano = 5

    def execute(self, atacante, alvo):
        if not super().execute(atacante, alvo):   
            return

        dano_total = self.calcular_dano_base(atacante,alvo,self.dano) * self.calcular_fraqueza("Terra",alvo.genoma[0])
        alvo.saude -= dano_total

        # Resposta
        log = f"{atacante.nome} usa Enterrar em {alvo.nome} e causa {dano_total} de dano."
        atacante.log.append(log)

class HabilidadeSanguessuga(Habilidade):
    """
    Causa dano de inseto e se cura pela metade do dano.
    """
    def __init__(self):
        super().__init__(custo_energia=5,nome="Sanguessuga")
        self.dano = 5

    def execute(self, atacante, alvo):
        if not super().execute(atacante, alvo):
            return

        dano_total = self.calcular_dano_base(atacante,alvo,self.dano) * self.calcular_fraqueza("Inseto",alvo.genoma[0])
        cura = round(dano_total / 2)

        # Efeito
        alvo.saude -= dano_total
        atacante.saude -= cura

        # Resposta
        log = f"{atacante.nome} usa Sanguessuga em {alvo.nome}, causa {dano_total} de dano e recupera {cura} de saúde."
        atacante.log.append(log)

class HabilidadeGarraNoturna(Habilidade):
    """
    Causa dano elemental de Sombras, possui 20% de chance de acerto crítico (Dano dobrado)
    """
    def __init__(self):
        super().__init__(custo_energia=5,nome="Garra Noturna")
        self.dano = 5

    def execute(self, atacante, alvo):
        if not super().execute(atacante, alvo):
            return

        dano_total = self.calcular_dano_base(atacante,alvo,self.dano) * self.calcular_fraqueza("Sombra",alvo.genoma[0])

        # Efeito
        if random.random() > 0.2:
            dano_total *= 2
            log = f"A habilidade Garra Noturna de {atacante.nome} causou um golpe crítico!"
            atacante.log.append(log)
        alvo.saude -= dano_total

        # Resposta
        log = f"{atacante.nome} usa Garra Noturna em {alvo.nome} e causa {dano_total} de dano."
        atacante.log.append(log)

class HabilidadeCura(Habilidade):
    """
    Cura o usuário em 20 pontos de vida
    """
    def __init__(self):
        super().__init__(custo_energia=5,nome="Cura")

    def execute(self, atacante, alvo):
        if not super().execute(atacante, alvo):
            return
        
        # Efeito
        atacante.saude = max(atacante.saude + 20, atacante.saudeMAX)

        # Resposta
        log = f"{atacante.nome} usa Cura e recupera 20 de saúde."
        atacante.log.append(log)

## POR TAMANHO

class HabilidadeEsquivar(Habilidade):
    """
    O usuário se move 3 células em uma direção aleatória.
    """
    def __init__(self):
        super().__init__(custo_energia=5,nome="Esquivar")

    def execute(self, atacante, alvo):
        if not super().execute(atacante, alvo):
            return

        # Efeito
        i, j = atacante.posicao
        
        randi = random.choice([-3, 0, 3])
        randj = random.choice([-3, 0, 3])
        i = i + randi if 0 >= i + randi < atacante.ambiente.size else i + (randi * -1)
        j = j + randj if 0 >= j + randj < atacante.ambiente.size else j + (randj * -1)

        atacante.posicao = (i, j)
        
        # Resposta
        log = f"{atacante.nome} usa Esquivar e se move para {atacante.posicao}."
        atacante.log.append(log)

class HabilidadeEsmagar(Habilidade):
    """
    Causa um dano maior quanto maior o usuário for
    """
    def __init__(self):
        super().__init__(custo_energia=3,nome="Esmagar")
        self.dano = 7

    def execute(self, atacante, alvo):
        if not super().execute(atacante, alvo):
            return
        
        dano = self.dano

        if atacante.genoma[2] == "Grande": dano += 7
        elif atacante.genoma[2] == "Medio": dano += 3

        # Dano
        dano_total = self.calcular_dano_base(atacante,alvo,dano)

        # Efeito
        alvo.saude -= dano_total

        # Resposta
        log = f"{atacante.nome} usa Esmagar em {alvo.nome} e causa {dano_total} de dano."
        atacante.log.append(log)

class HabilidadeMordiscar(Habilidade):
    """
    Causa um pequeno dano neutro
    """
    def __init__(self):
        super().__init__(custo_energia=5,nome="Mordiscar")
        self.dano = 2

    def execute(self, atacante, alvo):
        if not super().execute(atacante, alvo):
            return
        
        # Dano
        
        dano_total = self.calcular_dano_base(atacante,alvo,self.dano)

        # Efeito
        alvo.saude -= dano_total

        # Resposta
        log = f"{atacante.nome} usa Mordiscar em {alvo.nome} e causa {dano_total} de dano."
        atacante.log.append(log)

class HabilidadeMordida(Habilidade):
    """
    Causa um dano médio neutro
    """
    def __init__(self):
        super().__init__(custo_energia=5,nome="Mordida")
        self.dano = 5

    def execute(self, atacante, alvo):
        if not super().execute(atacante, alvo):
            return
        
        # Dano
        
        dano_total = self.calcular_dano_base(atacante,alvo,self.dano)

        # Efeito
        alvo.saude -= dano_total

        # Resposta
        log = f"{atacante.nome} usa Mordida em {alvo.nome} e causa {dano_total} de dano."
        atacante.log.append(log)

class HabilidadeMordidaAprimorada(Habilidade):
    """
    Causa um dano alto neutro
    """
    def __init__(self):
        super().__init__(custo_energia=5,nome="Mordida Aprimorada")
        self.dano = 7

    def execute(self, atacante, alvo):
        if not super().execute(atacante, alvo):
            return
        
        # Dano
        
        dano_total = self.calcular_dano_base(atacante,alvo,self.dano)

        # Efeito
        alvo.saude -= dano_total
        # Resposta
        log = f"{atacante.nome} usa Mordida Aprimorada em {alvo.nome} e causa {dano_total} de dano."
        atacante.log.append(log)

class HabilidadePrender(Habilidade):
    def __init__(self):
        super().__init__(custo_energia=5,nome="Prender")

    def execute(self, atacante, alvo):
        if not super().execute(atacante, alvo):
            return
        # TODO Implementar Prender
        # Resposta
        log = f"{atacante.nome} usa Prender em {alvo.nome}."
        atacante.log.append(log)

class HabilidadeEscalar(Habilidade):
    def __init__(self):
        super().__init__(custo_energia=5,nome="Escalar")

    def execute(self, atacante, alvo):
        if not super().execute(atacante, alvo):
            return
        # TODO Implementar Escalar
        # Resposta
        log = f"{atacante.nome} usa Escalar."
        atacante.log.append(log)

class HabilidadeCorrer(Habilidade):
    def __init__(self):
        super().__init__(custo_energia=5,nome="Correr")

    def execute(self, atacante, alvo):
        if not super().execute(atacante, alvo):
            return
        # TODO Implementar Correr
        # Resposta
        log = f"{atacante.nome} usa Correr."
        atacante.log.append(log)

class HabilidadeArranhar(Habilidade):
    """
    Causa um dano médio neutro
    """
    def __init__(self):
        super().__init__(custo_energia=5,nome="Arranhar")
        self.dano = 5

    def execute(self, atacante, alvo):
        if not super().execute(atacante, alvo):
            return
        
        # Dano
        
        dano_total = self.calcular_dano_base(atacante,alvo,self.dano)

        # Efeito
        alvo.saude -= dano_total

        # Resposta
        log = f"{atacante.nome} usa Arranhar em {alvo.nome} e causa {dano_total} de dano."
        atacante.log.append(log)

class HabilidadeRasgar(Habilidade):
    def __init__(self):
        super().__init__(custo_energia=5,nome="Rasgar")
        self.dano = 5

    def execute(self, atacante, alvo):
        if not super().execute(atacante, alvo):
            return
        # Dano
        
        dano_total = self.calcular_dano_base(atacante,alvo,self.dano)
        if atacante.genoma[9] == "Carapaca": dano_total *= 0.5
        if atacante.genoma[9] == "Nenhuma": dano_total *= 1.5

        # Efeito
        alvo.saude -= dano_total

        # Resposta
        log = f"{atacante.nome} usa Rasgar em {alvo.nome} e causa {dano_total} de dano."
        atacante.log.append(log)

class HabilidadeMartelar(Habilidade):
    def __init__(self):
        super().__init__(custo_energia=5,nome="Martelar")
        self.dano = 5

    def execute(self, atacante, alvo):
        if not super().execute(atacante, alvo):
            return
        
        # Dano
        
        dano_total = self.calcular_dano_base(atacante,alvo,self.dano)

        # Efeito
        alvo.saude -= dano_total

        #TODO Efeito Confusão

        # Resposta
        log = f"{atacante.nome} usa Martelar em {alvo.nome} e causa {dano_total} de dano."
        atacante.log.append(log)

class HabilidadeRetaliar(Habilidade):
    def __init__(self):
        super().__init__(custo_energia=5,nome="Retaliar")

    def execute(self, atacante, alvo):
        if not super().execute(atacante, alvo):
            return        

        # Dano
        dano = int(max(1, min(10, (11 - (atacante.saude / atacante.saudeMAX) *10))))
        dano_total = self.calcular_dano_base(atacante,alvo,dano)

        # Efeito
        alvo.saude -= dano_total

        # Resposta
        log = f"{atacante.nome} usa Retaliar em {alvo.nome} e causa {dano_total} de dano."
        atacante.log.append(log)

class HabilidadeNadar(Habilidade):
    def __init__(self):
        super().__init__(custo_energia=5,nome="Nadar")

    def execute(self, atacante, alvo):
        if not super().execute(atacante, alvo):
            return
        # TODO Implementar Nadar
        # Resposta
        log = f"{atacante.nome} usa Nadar."
        atacante.log.append(log)

class HabilidadeDefender(Habilidade):
    def __init__(self):
        super().__init__(custo_energia=5,nome="Defender")

    def execute(self, atacante, alvo):
        if not super().execute(atacante, alvo):
            return
        # TODO Implementar Defender
        # Resposta
        log = f"{atacante.nome} usa Defender."
        atacante.log.append(log)

class HabilidadeCamuflagem(Habilidade):
    def __init__(self):
        super().__init__(custo_energia=5,nome="Camuflagem")

    def execute(self, atacante, alvo):
        if not super().execute(atacante, alvo):
            return
        # TODO Efeito Camuflagem
        # Resposta
        log = f"{atacante.nome} usa Camuflagem."
        atacante.log.append(log)

class HabilidadeVeneno(Habilidade):
    def __init__(self):
        super().__init__(custo_energia=5,nome="Veneno")

    def execute(self, atacante, alvo):
        if not super().execute(atacante, alvo):
            return
        # TODO Efeito Veneno
        # Resposta
        log = f"{atacante.nome} usa Veneno."
        atacante.log.append(log)

class HabilidadeIluminar(Habilidade):
    def __init__(self):
        super().__init__(custo_energia=5,nome="Iluminar")

    def execute(self, atacante, alvo):
        if not super().execute(atacante, alvo):
            return
        # TODO Efeito Cegueira
        # Resposta
        log = f"{atacante.nome} usa Iluminar."
        atacante.log.append(log)

class HabilidadeEletrocutar(Habilidade):
    def __init__(self):
        super().__init__(custo_energia=5,nome="Eletrocutar")
        self.dano = 5

    def execute(self, atacante, alvo):
        if not super().execute(atacante, alvo):
            return
        
        # Dano
        dano_total = self.calcular_dano_base(atacante,alvo,self.dano)
        
        if alvo.genoma[0] == "Agua": dano_total *= 2
        elif alvo.genoma[0] == "Terra": dano_total *= 0
        # Efeito
        
        alvo.saude -= dano_total

        # Resposta
        log = f"{atacante.nome} usa Eletrocutar em {alvo.nome} e causa {dano_total} de dano."
        atacante.log.append(log)


HABILIDADES_POR_GENOMA = {
    
    "Tipo": {
        "Fogo": [HabilidadeLancarBrasas()],
        "Agua": [HabilidadeJatoDagua()],
        "Terra": [HabilidadeEnterrar()], 
        "Inseto": [HabilidadeSanguessuga()],
        "Sombra": [HabilidadeGarraNoturna()], 
        "Luz": [HabilidadeCura()]
    },
    "Tamanho": {
        "Pequeno": [HabilidadeEsquivar()],
        "Grande": [HabilidadeEsmagar()]
    },
    "Presas": {
        "Pequena": [HabilidadeMordiscar()],
        "Media": [HabilidadeMordida()],
        "Grande": [HabilidadeMordida(), HabilidadeMordidaAprimorada(), HabilidadePrender()]
    },
    "Patas": {
        "Apode": [HabilidadeEscalar()],
        "Bipede": [HabilidadeCorrer()],
        "Quadrupede": [HabilidadeCorrer()],
        "Multipede": [HabilidadeCorrer()]
    },
    "Garras": {
        "Curta": [HabilidadeArranhar()],
        "Longa": [HabilidadeRasgar(), HabilidadePrender()],
        "Retrateis": [HabilidadeRasgar()]
    },
    "Cauda": {
        "Equilibrio": [HabilidadePrender()],
        "Ataque": [HabilidadeMartelar(), HabilidadeRetaliar()],
        "Aquatica": [HabilidadeNadar()]
    },
    "Defesa": {
        "Carapaca": [HabilidadeDefender()], 
    },
    "Extra": {
        "Camuflagem": [HabilidadeCamuflagem()], 
        "Veneno": [HabilidadeVeneno()], 
        "Bioluminescencia": [HabilidadeIluminar()], 
        "Campo-eletrico": [HabilidadeEletrocutar()]
    },
}