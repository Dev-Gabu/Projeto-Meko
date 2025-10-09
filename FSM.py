import random
from ambiente import Fruta, Carne
from settings import fruit_list, mekos_list, meat_list
from habilidades import *

class State:
    """
    Classe base para os estados da máquina de estados finitos (FSM) dos Mekos.
    
    Attributes:
        name (str): O nome do estado.
        
    Methods:
        enter(meko): Método chamado quando o Meko entra no estado.
        execute(meko): Método chamado para executar a lógica do estado.
        exit(meko): Método chamado quando o Meko sai do estado.
    """
    def __init__(self, name):
        self.name = name

    def enter(self, meko): pass
    def execute(self, meko): pass
    def exit(self, meko): pass


class FSM:
    """
    Classe que representa a máquina de estados finitos (FSM) para os Mekos.
    
    Attributes:
        owner (Meko): O objeto Meko que possui esta FSM.
        current_state (State): O estado atual da FSM.
        
    Methods: 
        change_state(new_state): Muda o estado atual para um novo estado.
        update(): Atualiza o estado atual chamando seu método execute.
    """
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
    """
    Estado em que o Meko se defende de um ataque. Baseia a decisão de fugir ou lutar na agressividade e saúde do Meko.
    
    1. Imprime uma mensagem indicando que o Meko foi atacado e vai se defender.
    2. Calcula a probabilidade de fugir com base na agressividade e saúde do Meko.
    3. Se a probabilidade de fugir for maior que um valor aleatório, o meko entra em estado `Flee`.
    4. Caso contrário, o Meko entra em estado `Combat` e imprime uma mensagem indicando que decidiu lutar.
    """
    def __init__(self): super().__init__("Defender")
    def execute(self, meko):
        print(f"{meko.nome} foi atacado e vai se defender.")

        if random.random() < (meko.agressividade - max(1, min(10, (11 - (meko.saude / meko.saudeMAX) *10)))) / 30:
            meko.fsm.change_state(Flee())
        else:
            meko.fsm.change_state(Combat())
            print(f"{meko.nome} decide lutar.")

class Flee(State):
    
    """
    Estado em que o Meko foge para sobreviver. O Meko abandona seu alvo e se move aleatoriamente para escapar do perigo.
    
    1. Imprime uma mensagem indicando que o Meko está fugindo para sobreviver
    2. Define o alvo (target) do Meko como None, indicando que ele não está mais perseguindo ninguém.
    3. Chama o método random_step() do Meko para mover-se aleatoriamente no ambiente.
    4. Muda o estado da FSM do Meko para `Wander`, indicando que ele está agora vagando sem rumo.
    """
    
    def __init__(self): super().__init__("Fugir")
    def execute(self, meko):
        print(f"{meko.nome} foge para sobreviver!")

        meko.target = None
        meko.random_step()
        meko.fsm.change_state(Wander())

class Combat(State):
    
    """
    Estado em que o Meko está em combate com outro Meko. O Meko avalia se deve continuar lutando ou fugir com base na agressividade e saúde. Caso entre em combate, pode usar habilidades contra o alvo.
    
    1. Verifica se o Meko tem um alvo (target) e se o alvo está vivo.
    2. Se o alvo estiver vivo, calcula a probabilidade de o Meko fugir com base na agressividade e saúde do Meko.
    3. Se a probabilidade de fugir for maior que um valor aleatório, o Meko muda para o estado `Flee`.
    4. Se o Meko estiver na mesma posição que o alvo, imprime uma mensagem indicando que está em combate e escolhe aleatoriamente uma habilidade para usar contra o alvo.
    5. Se o Meko não estiver na mesma posição que o alvo, há uma chance de 50% de ele perseguir o alvo (mudando para o estado `MoveToTarget`) ou decidir não perseguir (mudando para o estado `Wander` e definindo o alvo como None).
    6. Se o alvo não estiver mais vivo, o Meko define o alvo como None e muda para o estado `Wander`.
    """
    
    def __init__(self): super().__init__("Combate")
    def execute(self, meko):
        
        if meko.target and meko.target.esta_vivo():
            if random.random() > 1 / max(1, min(10, (11 - (meko.saude / meko.saudeMAX) *10))):
                meko.fsm.change_state(Flee())
            else:
                if meko.posicao == meko.target.posicao:
                    print(f"{meko.nome} está em combate com {meko.target.nome}!")
                    escolha = random.choice(meko.habilidades)
                    escolha.execute(meko, meko.target)
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
    
    """
    Estado responsável pela movimentação em que o meko se move em direção ao seu alvo.
    
    1. Compara a posição `x` e `y` do meko e do alvo.
    2. A cada iteração, soma ou subtrai um ponto na posição do meko, até que se iguale à posição do alvo.
    3. Ao alcançar seu alvo, define a próxima ação dependendo do tipo do alvo.
    4. Se o alvo for `Carne` ou `Fruta`, entra no estado `Eat`
    5. Se o alvo for outro `Meko`, entra em estado de combate ativando o estado `Combat` e ativa o estado `Defend`do alvo.
    """
    
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
    """
    Estado responsável pela movimentação em que o meko se move em direção ao parceiro escolhido para reprodução.
    
    1. Compara a posição `x` e `y` do meko e do alvo.
    2. A cada iteração, soma ou subtrai um ponto na posição do meko, até que se iguale à posição do alvo.
    3. Ao alcançar seu alvo, entra no estado `Reproduce`
    """

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
    
    """
    Estado responsável pela busca por outro meko para ser caçado.
    
    1. Dá um passo aleatório
    2. Chama a função search do Meko e procura por algum objeto `Meko` na lista de objetos.
    3. Se encontrar, define o meko encontrado como alvo e entra em perseguição ativando o estado `MoveToTarget`.
    """
    
    def __init__(self): super().__init__("Caçar criatura")
    def execute(self, meko):
        print(f"{meko.nome} procura uma criatura para caçar.")

        meko.random_step()

        if meko.search(mekos_list, 'Meko') is not None:
            meko.target = meko.search(mekos_list, 'Meko')
            print(f"{meko.nome} encontrou {meko.target.nome} em {meko.target.posicao} e começa a caçá-lo.")
            meko.fsm.change_state(MoveToTarget())

class SearchMeat(State):
    
    """
    Estado responsável pela busca por carne para comer
    
    1. Dá um passo aleatório
    2. Chama a função search do Meko e procura por algum objeto `Carne` na lista de objetos.
    3. Se encontrar, define o objeto como alvo e se move até ele, ativando o estado `MoveToTarget`.
    4. Se não encontrar, se baseia na agressividade do Meko para saber se deve entrar no modo de caça entrando no estado `HuntCreature`.
    5. Se não encontrar e for onívoro, tem 50% de chance de entrar no modo de procurar `Frutas` ativando o estado `SearchFruits`.
    """
    
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
    """
    Estado responsável pela busca por carne para comer
    
    1. Dá um passo aleatório chamando o método `random_step` do meko.
    2. Chama a função search do Meko e procura por algum objeto `Fruta` na lista de objetos.
    3. Se encontrar, define o objeto como alvo e se move até ele, ativando o estado `MoveToTarget`.
    5. Se não encontrar e for onívoro, tem 50% de chance de entrar no modo de procurar `Frutas` ativando o estado `SearchMeat`.
    """
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
    """
    Estado responsável pelo comportamento e decisão de troca de estado quando o meko está em estado neutro.
    
    1. Dá um passo aleatório chamando o método `random_step` do meko.
    2. Se a energia for menor que 40% da energia máxima:
        2.1 Se for herbívoro, entra no estado `SearchFruits`
        2.2 Se for carnívoro, entra no estado `SearchMeat`
        2.3 Se for onívoro, escolhe aleatóriamente entre entrar no estado `SearchFruits` ou `SearchMeat`
    3. Se a energia for maior que 40% e o Meko for fértil, tem 30% de chance de procurar um parceiro para reproduzir, entrando no estado `FindPartner`
    
    """
    
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
    
    """
    Estado responsável pela reprodução entre mekos.
    
    1. Checa se o Meko está apto a reproduzir, caso contrário desiste de reproduzir e entra no estado `Wander`
    2. Se o parceiro não estiver apto a reproduzir, ele rejeitará o meko e entrará no estado `Wander`
    3. Caso ambos sejam aptos a reproduzir, ambos se tornam inférteis.
    4. O nome do filhote é composto pelas três primeiras letras do nome de um pai e as três últimas letras do nome do outro.
    5. O genoma é uma seleção aleatória entre o genoma dos dois pais.
    6. Um novo meko é gerado chamando o método `gerar_filhote` do meko.
    """
    
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
            
            nome = f"{meko.nome[0:2]}{meko.love.nome[len(meko.love.nome)-2:len(meko.love.nome)]}"
            
            genoma = [random.choice([meko.genoma[i], meko.love.genoma[i]]) for i in range(len(meko.genoma))]
            meko.gerar_filhote(nome, genoma)

class FindPartner(State):
    
    """
    Estado responsável pela busca por um parceiro para acasalar.
    
    1. Dá um passo aleatório chamando o método `random_step` do meko.
    2. Chama a função search do Meko e procura por algum objeto `Meko` na lista de objetos.
    3. Caso encontre, define o meko como parceiro em potencial e entra no estado `MoveToPartner`
    4. Caso não encontre, checa seu nível de energia, caso for menor que 50% da capacidade máxima, o meko desiste de procurar um parceiro.
    """
    
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
    
    """
    Estado responsável por gerenciar a alimentação do meko.
    
    1. Se a comida alcançada for uma `Fruta` e o meko for herbívoro ou onívoro, reduz sua quantidade em 1 e aumenta a energia em 100, até a quantidade ser 0.
    2. Se a comida alcançada for uma `Carne` e o meko for carnívoro ou onívoro, reduz sua quantidade em 1 e aumenta a energia em 50, até a quantidade ser 0.
    3. Se a comida for totalmente consumida ou a energia do meko for maior que 90% da sua capacidade máxima, ele retorna ao estado `Wander`
    
    """
    
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