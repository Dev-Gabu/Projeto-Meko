import random
from settings import fruit_list, meat_list, mekos_list
from ambiente import Fruta, Carne

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
        meko.energy -= 5

# TODO Implementar Classe Combater
class Combat(State):
    def __init__(self): super().__init__("Combate")
    def execute(self, meko, matriz):
        print(f"{meko.nome} entra em combate!")
        if random.random() > 0.5:
            meko.fsm.change_state(Flee())
        else:
            meko.fsm.change_state(MoveToTarget())


class MoveToTarget(State):
    def __init__(self): super().__init__("Seguindo")
    def execute(self, meko, matriz):
        print(f"{meko.nome} se move em direção ao alvo.")

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

# TODO Implementar Classe Caçar
class HuntCreature(State):
    def __init__(self): super().__init__("Caçar criatura")
    def execute(self, meko, matriz):
        print(f"{meko.nome} procura uma criatura para caçar.")


class SearchMeat(State):
    global meat_list
    def __init__(self): super().__init__("Buscando carne")
    def execute(self, meko, matriz):
        print(f"{meko.nome} procura carne no ambiente.")
        i, j = meko.posicao
        i = (i + random.choice([-1, 0, 1]))
        j = (j + random.choice([-1, 0, 1]))
        meko.posicao = (i, j)
        meko.energia -= 1
        meko.search(meat_list, tipo="Carne")

class SearchFruits(State):
    global fruit_list
    def __init__(self): super().__init__("Buscando frutas")
    def execute(self, meko, matriz):
        print(f"{meko.nome} procura frutas no ambiente.")
        i, j = meko.posicao
        i = (i + random.choice([-1, 0, 1]))
        j = (j + random.choice([-1, 0, 1]))
        meko.posicao = (i, j)
        meko.energia -= 1
        meko.search(fruit_list, tipo="Fruta")


class Wander(State):
    def __init__(self): super().__init__("Caminhando")
    def execute(self, meko, matriz):
        print(f"{meko.nome} vagueia sem rumo.")
        i, j = meko.posicao
        i = (i + random.choice([-1, 0, 1]))
        j = (j + random.choice([-1, 0, 1]))
        meko.posicao = (i, j)
        meko.energia -= 1

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
                print(f"{meko.target} foi consumida.")
                meko.fsm.change_state(Wander())
        elif isinstance(meko.target, Carne) and meko.genoma[1] == "Carnivoro" or meko.genoma[1] == "Onivoro":
            if meko.target.quant > 0:
                meko.target.quant -= 1
                meko.energia  = min(meko.energia + 15, meko.energiaMAX)
            else:
                print(f"{meko.target} foi consumida.")
                meko.fsm.change_state(Wander())
        else:
            print(f"{meko.nome} não sabe o que fazer com {meko.target}.") 
        meko.fsm.change_state(Wander())