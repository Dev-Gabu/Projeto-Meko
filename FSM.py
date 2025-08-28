import random
from ambiente import Fruta, Carne
from settings import fruit_list, mekos_list, meat_list
from habilidades import *

class State:
    def __init__(self, name):
        self.name = name

    def enter(self, meko): pass
    def execute(self, meko): pass
    def exit(self, meko): pass


class FSM:
    def __init__(self, owner):
        self.owner = owner
        self.current_state = None

    def change_state(self, new_state):
        if self.current_state:
            self.current_state.exit(self.owner)
        self.current_state = new_state
        self.current_state.enter(self.owner)

    def update(self):
        if self.current_state:
            self.current_state.execute(self.owner)


## Comportamentos dos Mekos

class Defend(State):
    def __init__(self): super().__init__("Defender")
    def execute(self, meko):
        print(f"{meko.nome} foi atacado e vai se defender.")

        ## Subtrai o fator de dano recebido da agressividade e decide baseado nisso:
        if random.random() < (meko.agressividade - max(1, min(10, (11 - (meko.saude / meko.saudeMAX) *10)))) / 30:
            meko.fsm.change_state(Flee())
        else:
            meko.fsm.change_state(Combat())
            print(f"{meko.nome} decide lutar.")

class Flee(State):
    def __init__(self): super().__init__("Fugir")
    def execute(self, meko):
        print(f"{meko.nome} foge para sobreviver!")

        meko.target = None
        meko.random_step()
        meko.fsm.change_state(Wander())


class Combat(State):
    def __init__(self): super().__init__("Combate")
    def execute(self, meko):
        
        if meko.target and meko.target.esta_vivo():
            if random.random() > 1 / max(1, min(10, (11 - (meko.saude / meko.saudeMAX) *10))):
                meko.fsm.change_state(Flee())
            else:
                if meko.posicao == meko.target.posicao:
                    print(f"{meko.nome} está em combate com {meko.target.nome}!")
                    escolha = random.choice(meko.habilidades)
                    escolha.executar(meko, meko.target)
                elif random.random() < 0.5: 
                    print(f"{meko.nome} persegue {meko.target.nome}!")
                    meko.fsm.change_state(MoveToTarget())
                else:
                    print(f"{meko.nome} decide não perseguir {meko.target.nome}.")
                    meko.fsm.change_state(Wander())
                    meko.target = None
        else:
            meko.target = None
            meko.fsm.change_state(Wander())
        

class MoveToTarget(State):
    def __init__(self): super().__init__("Seguindo")
    def execute(self, meko):

        x, y = meko.posicao
        tx, ty = meko.target.posicao

        if x < tx:
            x += 1
        elif x > tx:
            x -= 1
        if y < ty:
            y += 1
        elif y > ty:
            y -= 1
        meko.posicao = (x, y)

        if meko.posicao == meko.target.posicao:
            if meko.target.__class__.__name__ == "Carne" or meko.target.__class__.__name__ == "Fruta":
                print(f"{meko.nome} chegou ao alvo e agora vai comer.")
                meko.fsm.change_state(Eat())
            else:
                print(f"{meko.nome} chegou ao alvo e agora vai combater.")
                meko.target.fsm.change_state(Defend())
                meko.fsm.change_state(Combat())
                meko.target.target = meko
        else:
            print(f"{meko.nome} se move em direção ao alvo.")
            
class MoveToPartner(State):
    def __init__(self): super().__init__("Seguindo")
    def execute(self, meko):

        x, y = meko.posicao
        tx, ty = meko.love.posicao

        if x < tx:
            x += 1
        elif x > tx:
            x -= 1
        if y < ty:
            y += 1
        elif y > ty:
            y -= 1
        meko.posicao = (x, y)

        if meko.posicao == meko.love.posicao:
            print(f"{meko.nome} encontrou seu par e agora vai tentar acasalar.")
            meko.fsm.change_state(Reproduce())
        else:
            print(f"{meko.nome} se move em direção ao alvo.")


class HuntCreature(State):
    def __init__(self): super().__init__("Caçar criatura")
    def execute(self, meko):
        print(f"{meko.nome} procura uma criatura para caçar.")

        meko.random_step()

        if meko.search(mekos_list, 'Meko') is not None:
            meko.target = meko.search(mekos_list, 'Meko')
            print(f"{meko.nome} encontrou {meko.target.nome} em {meko.target.posicao} e começa a caçá-lo.")
            meko.fsm.change_state(MoveToTarget())


class SearchMeat(State):
    def __init__(self): super().__init__("Buscando carne")
    def execute(self, meko):
        print(f"{meko.nome} procura carne no ambiente.")

        meko.random_step()

        # Define estado e alvo
        if meko.search(meat_list, tipo='Carne') is not None:
            alvo = meko.search(meat_list, tipo='Carne')
            meko.fsm.change_state(MoveToTarget())
            meko.target = alvo

            print(f"{meko.nome} encontrou carne em {alvo.posicao} e vai até lá.")
        elif random.random() < meko.agressividade / 30:
            meko.fsm.change_state(HuntCreature())
        if meko.genoma[1] == "Onivoro" and random.random() > 0.5:
            meko.fsm.change_state(SearchFruits())

class SearchFruits(State):
    def __init__(self): super().__init__("Buscando frutas")
    def execute(self, meko):
        print(f"{meko.nome} procura frutas no ambiente.")

        meko.random_step()

        # Define estado e alvo
        if meko.search(fruit_list, tipo='Fruta') is not None:
            alvo = meko.search(fruit_list, tipo='Fruta')
            meko.fsm.change_state(MoveToTarget())
            meko.target = alvo

            print(f"{meko.nome} encontrou fruta em {alvo.posicao} e vai até lá.")
        if meko.genoma[1] == "Onivoro" and random.random() > 0.5:
            meko.fsm.change_state(SearchMeat())


class Wander(State):
    def __init__(self): super().__init__("Caminhando")
    def execute(self, meko):

        print(f"{meko.nome} vagueia sem rumo.")
        meko.random_step()

        if meko.energia <= meko.energiaMAX * 0.4:
            if meko.genoma[1] == "Herbivoro":
                meko.fsm.change_state(SearchFruits())
            elif meko.genoma[1] == "Carnivoro":
                meko.fsm.change_state(SearchMeat())
            elif meko.genoma[1] == "Onivoro":
                if random.random() > 0.5:
                    meko.fsm.change_state(SearchFruits())
                else:
                    meko.fsm.change_state(SearchMeat())
        elif meko.fertilidade == "Fertil" and random.random() < 0.3:
            meko.fsm.change_state(FindPartner())

class Reproduce(State):
    def __init__(self): super().__init__("Reproduzir")
    def execute(self, meko):

        if meko.fertilidade == "Incapaz":
            print(f"{meko.nome} desistiu de reproduzir.")
            meko.fsm.change_state(Wander())
        elif meko.love.fertilidade == "Incapaz" or meko.love.fertilidade == "Infertil":
            print(f"{meko.love.nome} rejeitou {meko.nome}.")
            meko.fsm.change_state(Wander())
        else:
            print(f"{meko.nome} e {meko.love.nome} começam a acasalar.")
            meko.fertilidade = "Infertil"
            meko.love.fertilidade = "Infertil"
            
            # Gerar filhote
            nome = f"{meko.nome[0:2]}{meko.love.nome[len(meko.love.nome)-2:len(meko.love.nome)]}"
            genoma = [random.choice([meko.genoma[i], meko.love.genoma[i]]) for i in range(len(meko.genoma))]
            meko.gerar_filhote(nome, genoma)

class FindPartner(State):
    def __init__(self): super().__init__("Buscar parceiro")
    def execute(self, meko):
        print(f"{meko.nome} procura um parceiro para acasalar.")
        
        meko.random_step()
        
        if meko.search(mekos_list, 'Meko') is not None:
            meko.love = meko.search(mekos_list, 'Meko')
            print(f"{meko.nome} se interessou por {meko.love.nome} e tenta acasalar.")
            meko.fsm.change_state(MoveToPartner())
        elif meko.energia <= meko.energiaMAX * 0.5:
            
            meko.fsm.change_state(Wander())
            print(f"{meko.nome} desistiu de procurar um parceiro.")

class Eat(State):
    def __init__(self): super().__init__("Comendo")
    def execute(self, meko):
        print(f"{meko.nome} está se alimentando.")
        if isinstance(meko.target, Fruta) and meko.genoma[1] == "Herbivoro" or meko.genoma[1] == "Onivoro":
            if meko.target.quant > 0:
                meko.target.quant -= 1
                meko.energia = min(meko.energia + 100, meko.energiaMAX)
            else:
                print(f"{meko.target.nome} foi consumida.")
                meko.fsm.change_state(Wander())
        elif isinstance(meko.target, Carne) and meko.genoma[1] == "Carnivoro" or meko.genoma[1] == "Onivoro":
            if meko.target.quant > 0:
                meko.target.quant -= 1
                meko.energia  = min(meko.energia + 50, meko.energiaMAX)
            else:
                print(f"{meko.target.nome} foi consumida.")
                meko.fsm.change_state(Wander())
        else:
            print(f"{meko.nome} não sabe o que fazer com {meko.target.nome}.")
        
        if meko.energia >= meko.energiaMAX * 0.9 or meko.target.quant <= 0:
            meko.fsm.change_state(Wander())