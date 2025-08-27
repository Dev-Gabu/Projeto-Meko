import random
from settings import GRID_SIZE

## MACROS

fraco = 0.5
forte = 1.5

## CLASSE PRINCIPAL

class Habilidade():
    def __init__(self, custo_energia):
        self.custo_energia = custo_energia

    def execute(self, user, alvo):
        if self.custo_energia > user.energia:
            print(f"{user.nome} não tem energia suficiente para usar essa habilidade.")
            # TODO Adicionar nome nas habilidades para resposta inteligente
            return
        user.energia -= self.custo_energia

## CLASSES ESPECIFICAS

## POR TIPO

class HabilidadeLancarBrasas(Habilidade):
    def __init__(self):
        super().__init__(custo_energia=5)

    def executar(self, atacante, alvo):
        dano = 5
        fraqueza = fraco if alvo.genoma[0] == "Inseto" or alvo.genoma[0] == "Terra" else fraco if alvo.genoma[0] == "Fogo" or alvo.genoma[0] == "Agua" else 1

        dano_total = max(dano, dano + atacante.forca - alvo.resistencia) * fraqueza
        alvo.saude -= dano_total
        atacante.energia -= self.custo_energia
        print(f"{atacante.nome} usa Lançar Brasas em {alvo.nome} e causa {dano_total} de dano.")

class HabilidadeJatoDagua(Habilidade):
    def __init__(self):
        super().__init__(custo_energia=5)

    def executar(self, atacante, alvo):

        # Dano
        dano = 5
        fraqueza = fraco if alvo.genoma[0] == "Fogo" or alvo.genoma[0] == "Inseto" else fraco if alvo.genoma[0] == "Terra" or alvo.genoma[0] == "Agua" else 1
        dano_total = max(dano, dano + atacante.forca - alvo.resistencia) * fraqueza

        # Efeito
        alvo.saude -= dano_total
        atacante.energia -= self.custo_energia

        # Resposta
        print(f"{atacante.nome} usa Jato d'Água em {alvo.nome} e causa {dano_total} de dano.")

class HabilidadeEnterrar(Habilidade):
    def __init__(self):
        super().__init__(custo_energia=5)

    def executar(self, atacante, alvo):

        # Dano
        dano = 5
        fraqueza = fraco if alvo.genoma[0] == "Agua" or alvo.genoma[0] == "Inseto" else fraco if alvo.genoma[0] == "Terra" or alvo.genoma[0] == "Fogo" else 1
        dano_total = max(dano, dano + atacante.forca - alvo.resistencia) * fraqueza

        # Efeito
        alvo.saude -= dano_total
        atacante.energia -= self.custo_energia

        # Resposta
        print(f"{atacante.nome} usa Enterrar em {alvo.nome} e causa {dano_total} de dano.")

class HabilidadeSanguessuga(Habilidade):
    def __init__(self):
        super().__init__(custo_energia=5)

    def executar(self, atacante, alvo):

        # Dano
        dano = 5
        dano_total = max(dano, dano + atacante.forca - alvo.resistencia)
        cura = round(dano_total / 2)

        # Efeito
        alvo.saude -= dano_total
        atacante.saude -= cura
        atacante.energia -= self.custo_energia

        # Resposta
        print(f"{atacante.nome} usa Sanguessuga em {alvo.nome}, causa {dano_total} de dano e recupera {cura} de saúde.")

class HabilidadeGarraNoturna(Habilidade):
    def __init__(self):
        super().__init__(custo_energia=5)

    def executar(self, atacante, alvo):

        # Dano
        dano = 5
        fraqueza = fraco if alvo.genoma[0] == "Luz" else fraco if alvo.genoma[0] == "Sombra" else 1
        dano_total = max(dano, dano + atacante.forca - alvo.resistencia) * fraqueza

        # Efeito
        if random.random() > fraco:
            dano_total *= 2
            print(f"A habilidade Garra Noturna de {atacante.nome} causou um golpe crítico!")
        alvo.saude -= dano_total
        atacante.energia -= self.custo_energia

        # Resposta
        print(f"{atacante.nome} usa Garra Noturna em {alvo.nome} e causa {dano_total} de dano.")

class HabilidadeCura(Habilidade):
    def __init__(self):
        super().__init__(custo_energia=5)

    def executar(self, atacante, alvo):
        
        # Efeito
        atacante.saude += 10
        atacante.energia -= self.custo_energia

        # Resposta
        print(f"{atacante.nome} usa Cura e recupera 10 de saúde.")

## POR TAMANHO

class HabilidadeEsquivar(Habilidade):
    def __init__(self):
        super().__init__(custo_energia=5)

    def executar(self, atacante, alvo):

        # Efeito
        i, j = atacante.posicao
        
        i = (i + random.choice([-3, 0, 3]))
        if 0 <= i < GRID_SIZE: i *= -1
        j = (j + random.choice([-3, 0, 3]))
        if 0 <= j < GRID_SIZE: j *= -1

        atacante.posicao = (i, j)
        atacante.energia -= self.custo_energia

        # Resposta
        print(f"{atacante.nome} usa Esquivar e se move para {atacante.posicao}.")

class HabilidadeEsmagar(Habilidade):
    def __init__(self):
        super().__init__(custo_energia=5)

    def executar(self, atacante, alvo):

        # Dano
        dano = 10
        fraqueza = fraco if alvo.genoma[2] == "Pequeno" else fraco if alvo.genoma[2] == "Grande" or alvo.genoma[2] == "Medio" else 1
        dano_total = max(dano, dano + atacante.forca - alvo.resistencia) * fraqueza

        # Efeito
        alvo.saude -= dano_total
        atacante.energia -= self.custo_energia

        # Resposta
        print(f"{atacante.nome} usa Esmagar em {alvo.nome} e causa {dano_total} de dano.")

class HabilidadeMordiscar(Habilidade):
    def __init__(self):
        super().__init__(custo_energia=5)

    def executar(self, atacante, alvo):

        # Dano
        dano = 2
        dano_total = max(dano, dano + atacante.forca - alvo.resistencia)

        # Efeito
        alvo.saude -= dano_total
        atacante.energia -= self.custo_energia

        # Resposta
        print(f"{atacante.nome} usa Mordiscar em {alvo.nome} e causa {dano_total} de dano.")

class HabilidadeMordida(Habilidade):
    def __init__(self):
        super().__init__(custo_energia=5)

    def executar(self, atacante, alvo):

        # Dano
        dano = 5
        dano_total = max(dano, dano + atacante.forca - alvo.resistencia)

        # Efeito
        alvo.saude -= dano_total
        atacante.energia -= self.custo_energia

        # Resposta
        print(f"{atacante.nome} usa Mordida em {alvo.nome} e causa {dano_total} de dano.")

class HabilidadeMordidaAprimorada(Habilidade):
    def __init__(self):
        super().__init__(custo_energia=5)

    def executar(self, atacante, alvo):

        # Dano
        dano = 7
        dano_total = max(dano, dano + atacante.forca - alvo.resistencia)
        
        # Efeito
        alvo.saude -= dano_total
        atacante.energia -= self.custo_energia

        # Resposta
        print(f"{atacante.nome} usa Mordida em {alvo.nome} e causa {dano_total} de dano.")

class HabilidadePrender(Habilidade):
    def __init__(self):
        super().__init__(custo_energia=5)

    def executar(self, atacante, alvo):
        # TODO Implementar Prender
        # Resposta
        print(f"{atacante.nome} usa Prender em {alvo.nome}.")

class HabilidadeEscalar(Habilidade):
    def __init__(self):
        super().__init__(custo_energia=5)

    def executar(self, atacante, alvo):
        # TODO Implementar Escalar
        # Resposta
        print(f"{atacante.nome} usa Escalar.")

class HabilidadeCorrer(Habilidade):
    def __init__(self):
        super().__init__(custo_energia=5)

    def executar(self, atacante, alvo):
        # TODO Implementar Correr
        # Resposta
        print(f"{atacante.nome} usa Correr.")

class HabilidadeArranhar(Habilidade):
    def __init__(self):
        super().__init__(custo_energia=5)

    def executar(self, atacante, alvo):

        # Dano
        dano = 5
        dano_total = max(dano, dano + atacante.forca - alvo.resistencia)

        # Efeito
        alvo.saude -= dano_total
        atacante.energia -= self.custo_energia

        # Resposta
        print(f"{atacante.nome} usa Arranhar em {alvo.nome} e causa {dano_total} de dano.")
    
class HabilidadeRasgar(Habilidade):
    def __init__(self):
        super().__init__(custo_energia=5)

    def executar(self, atacante, alvo):

        # Dano
        dano = 5
        fraqueza = fraco if alvo.genoma[8] == "Nenhuma" else 1 if alvo.genoma[8] == "Escamas" or alvo.genoma[8] == "Pelagem" else fraco
        dano_total = max(dano, dano + atacante.forca - alvo.resistencia) * fraqueza

        # Efeito
        alvo.saude -= dano_total
        atacante.energia -= self.custo_energia

        # Resposta
        print(f"{atacante.nome} usa Rasgar em {alvo.nome} e causa {dano_total} de dano.")

class HabilidadeMartelar(Habilidade):
    def __init__(self):
        super().__init__(custo_energia=5)

    def executar(self, atacante, alvo):

        # Dano
        dano = 5
        dano_total = max(dano, dano + atacante.forca - alvo.resistencia)

        # Efeito
        alvo.saude -= dano_total
        atacante.energia -= self.custo_energia

        #TODO Efeito Confusão

        # Resposta
        print(f"{atacante.nome} usa Martelar em {alvo.nome} e causa {dano_total} de dano.")

class HabilidadeRetaliar(Habilidade):
    def __init__(self):
        super().__init__(custo_energia=5)

    def executar(self, atacante, alvo):

        # Dano
        dano = max(1, min(10, (11 - (atacante.saude / atacante.saudeMAX) *10)))
        dano_total = max(dano, dano + atacante.forca - alvo.resistencia)

        # Efeito
        alvo.saude -= dano_total
        atacante.energia -= self.custo_energia

        # Resposta
        print(f"{atacante.nome} usa Retaliar em {alvo.nome} e causa {dano_total} de dano.")

class HabilidadeNadar(Habilidade):
    def __init__(self):
        super().__init__(custo_energia=5)

    def executar(self, atacante, alvo):
        # TODO Implementar Nadar
        # Resposta
        print(f"{atacante.nome} usa Nadar.")

class HabilidadeDefender(Habilidade):
    def __init__(self):
        super().__init__(custo_energia=5)

    def executar(self, atacante, alvo):
        # TODO Implementar Defender
        # Resposta
        print(f"{atacante.nome} usa Defender.")

class HabilidadeCamuflagem(Habilidade):
    def __init__(self):
        super().__init__(custo_energia=5)

    def executar(self, atacante, alvo):
        # TODO Efeito Camuflagem
        # Resposta
        print(f"{atacante.nome} usa Camuflagem.")

class HabilidadeVeneno(Habilidade):
    def __init__(self):
        super().__init__(custo_energia=5)

    def executar(self, atacante, alvo):
        # TODO Efeito Veneno
        # Resposta
        print(f"{atacante.nome} usa Veneno.")

class HabilidadeIluminar(Habilidade):
    def __init__(self):
        super().__init__(custo_energia=5)

    def executar(self, atacante, alvo):
        # TODO Efeito Cegueira
        # Resposta
        print(f"{atacante.nome} usa Iluminar.")

class HabilidadeEletrocutar(Habilidade):
    def __init__(self):
        super().__init__(custo_energia=5)

    def executar(self, atacante, alvo):

        # Dano
        dano = 1
        fraqueza = 10 if alvo.genoma[0] == "Agua" else 0 if alvo.genoma[0] == "Terra" else 5
        dano_total = max(dano, dano + atacante.forca - alvo.resistencia) * fraqueza

        # Efeito
        alvo.saude -= dano_total
        atacante.energia -= self.custo_energia

        #TODO Efeito Confusão

        # Resposta
        print(f"{atacante.nome} usa Martelar em {alvo.nome} e causa {dano_total} de dano.")


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
        "Pequena": [HabilidadeMordida()],
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