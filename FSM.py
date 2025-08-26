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

    def update(self, matriz):
        if self.current_state:
            self.current_state.execute(self.owner, matriz)


## Comportamentos dos Mekos

# TODO Implementar Classe Defender
class Defender(State):
    def __init__(self): super().__init__("Defender")
    def execute(self, meko, matriz):
        print(f"{meko.nome} está se defendendo.")
        if meko.hp < 30:
            meko.fsm.change_state(Flee())
        else:
            meko.fsm.change_state(Combat())

# TODO Implementar Classe Fugir
class Flee(State):
    def __init__(self): super().__init__("Fugir")
    def execute(self, meko, matriz):
        print(f"{meko.nome} foge para sobreviver!")

# TODO Implementar Classe Combater
class Combat(State):
    def __init__(self): super().__init__("Combate")
    def execute(self, meko, matriz):
        if meko.habilidades:
            escolha = random.choice(meko.habilidades)
            escolha.execute(meko, meko.target)


class MoveToTarget(State):
    def __init__(self): super().__init__("Seguindo")
    def execute(self, meko, matriz):

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
                meko.fsm.change_state(Combat())
        else:
            print(f"{meko.nome} se move em direção ao alvo.")

# TODO Implementar Classe Caçar
class HuntCreature(State):
    def __init__(self): super().__init__("Caçar criatura")
    def execute(self, meko, matriz):
        print(f"{meko.nome} procura uma criatura para caçar.")

        meko.random_step()

        if meko.search(mekos_list, 'Meko') is not None:
            alvo = meko.search(mekos_list, 'Meko')
            meko.fsm.change_state(MoveToTarget())
            meko.target = alvo

            print(f"{meko.nome} encontrou {meko.target.nome} em {alvo.posicao} e começa a caçá-lo.")
            meko.fsm.change_state(MoveToTarget())


class SearchMeat(State):
    def __init__(self): super().__init__("Buscando carne")
    def execute(self, meko, matriz):
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
    def execute(self, meko, matriz):
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
    def execute(self, meko, matriz):

        print(f"{meko.nome} vagueia sem rumo.")
        meko.random_step()

        if meko.energia <= meko.energiaMAX * 0.9:
            if meko.genoma[1] == "Herbivoro":
                meko.fsm.change_state(SearchFruits())
            elif meko.genoma[1] == "Carnivoro":
                meko.fsm.change_state(SearchMeat())
            elif meko.genoma[1] == "Onivoro":
                if random.random() > 0.5:
                    meko.fsm.change_state(SearchFruits())
                else:
                    meko.fsm.change_state(SearchMeat())

# TODO Implementar Classe Reproduzir
class Reproduce(State):
    def __init__(self): super().__init__("Reproduzir")
    def execute(self, meko, matriz):
        print(f"{meko.nome} tenta se reproduzir.")
        meko.fsm.change_state(FindPartner())

# TODO Implementar Classe Encontrar parceiro
class FindPartner(State):
    def __init__(self): super().__init__("Buscar parceiro")
    def execute(self, meko, matriz):
        print(f"{meko.nome} procura um parceiro para acasalar.")


class Eat(State):
    def __init__(self): super().__init__("Comendo")
    def execute(self, meko, matriz):
        print(f"{meko.nome} está se alimentando.")
        if isinstance(meko.target, Fruta) and meko.genoma[1] == "Herbivoro" or meko.genoma[1] == "Onivoro":
            if meko.target.quant > 0:
                meko.target.quant -= 1
                meko.energia = min(meko.energia + 15, meko.energiaMAX)
            else:
                print(f"{meko.target.nome} foi consumida.")
                meko.fsm.change_state(Wander())
        elif isinstance(meko.target, Carne) and meko.genoma[1] == "Carnivoro" or meko.genoma[1] == "Onivoro":
            if meko.target.quant > 0:
                meko.target.quant -= 1
                meko.energia  = min(meko.energia + 15, meko.energiaMAX)
            else:
                print(f"{meko.target.nome} foi consumida.")
                meko.fsm.change_state(Wander())
        else:
            print(f"{meko.nome} não sabe o que fazer com {meko.target.nome}.")
        meko.fsm.change_state(Wander())