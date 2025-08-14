import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button

import matplotlib.patches as mpatches

from ambiente import biome_gen, fruit_gen
from meko import Meko
from settings import CARACTERISTICAS, GRID_SIZE, CMAP, cores, NORM
from utils import sprite_por_genoma


class GenomaGUI:
    
    """
    Classe responsável pela interface gráfica de criação de genomas para os Meko.

    Nessa classe, o usuário pode selecionar as características desejadas para criar um novo Meko. E com base nessas características, serão gerados os atributos do Meko e sua aparência.

    """
    def __init__(self, root):
        """
        Inicializa a interface gráfica para criação de genomas.
        """

        self.root = root
        self.root.title("Criador de Genomas - Meko")
        self.entries = {}

        # Criação dos campos
        for i, (nome, opcoes) in enumerate(CARACTERISTICAS):
            tk.Label(root, text=nome).grid(row=i, column=0, padx=5, pady=5, sticky="w")
            var = tk.StringVar(value=opcoes[0])
            combo = ttk.Combobox(root, textvariable=var, values=opcoes, state="readonly")
            combo.grid(row=i, column=1, padx=5, pady=5)
            self.entries[nome] = var

        # Botões
        tk.Button(root, text="Limpar Campos", command=self.limpar).grid(row=len(CARACTERISTICAS), column=0, pady=10)
        tk.Button(root, text="Confirmar Criação", command=self.confirmar).grid(row=len(CARACTERISTICAS), column=1, pady=10)

    def limpar(self):
        """
        Limpa os campos do formulário.
        """
        for var in self.entries.values():
            var.set(var.get())  # Pode definir o padrão aqui

    def confirmar(self):
        """
        Confirma a criação do Meko e exibe a tela da interface contendo seus atributos e sua imagem.

        A função analisa o genoma e tenta criar um objeto Meko. Com o objeto criado, uma nova tela é aberta exibindo o novo Meko criado com seus atributos distribuídos e sua aparência.
        """
        genoma = [var.get() for var in self.entries.values()]
        nome = "MekoCriado"
        try:
            meko = Meko(nome, genoma)
        except Exception as e:
            messagebox.showerror("Erro", str(e))
            return

        janela_atributos = tk.Toplevel(self.root)
        janela_atributos.title(f"Atributos de {meko.nome}")

        # Atributos à esquerda
        row = 0
        for attr in ["peso", "velocidade", "resistencia", "forca", "visao", "agressividade", "temperatura"]:
            valor = getattr(meko, attr)
            tk.Label(janela_atributos, text=f"{attr.capitalize()}: {valor}").grid(row=row, column=0, padx=10, pady=5, sticky="w")
            row += 1

        # Geração do sprite
        sprite = sprite_por_genoma(meko.genoma)
        sprite = sprite.resize((sprite.width * 4, sprite.height * 4), Image.NEAREST)

        # Converter para ImageTk
        sprite_tk = ImageTk.PhotoImage(sprite)
        
        # Label para imagem
        label_imagem = tk.Label(janela_atributos, image=sprite_tk)
        label_imagem.grid(row=0, column=1, rowspan=row, padx=10, pady=5)

        # Manter referência da imagem para evitar garbage collection
        label_imagem.image = sprite_tk

def GUI_Gera_Meko():

    root = tk.Tk()
    app = GenomaGUI(root)
    root.mainloop()

def GUI_Gera_Ambiente():
    size = GRID_SIZE

    grid = np.random.choice([0, 1, 2], size=(size, size), p=[0.2, 0.3, 0.5])

    _, ax = plt.subplots()

    im = ax.imshow(grid, cmap=CMAP, norm=NORM, interpolation='nearest')

    def gerar_bioma():
        nonlocal grid
        print("Iniciando geração de bioma")
        for _ in range(20):
            grid = biome_gen(grid, size)
            im.set_data(grid)
            plt.pause(0.1)
        print("Geração de bioma concluída")

    def gerar_frutas():
        nonlocal grid
        print("Iniciando geração de recursos")
        grid = fruit_gen(grid, size)
        im.set_data(grid)
        plt.pause(0.1)
        print("Geração de recursos concluída")

    def imprimir_matriz():
        print("\n".join(" ".join(map(str, linha)) for linha in grid))

    ax_bioma = plt.axes([0.7, 0.05, 0.1, 0.075])
    btn_bioma = Button(ax_bioma, 'Gerar Bioma')
    btn_bioma.on_clicked(lambda event: gerar_bioma())

    ax_frutas = plt.axes([0.81, 0.05, 0.1, 0.075])
    btn_frutas = Button(ax_frutas, 'Gerar Frutas')
    btn_frutas.on_clicked(lambda event: gerar_frutas())

    ax_print = plt.axes([0.59, 0.05, 0.1, 0.075])
    btn_print = Button(ax_print, 'Imprimir Matriz')
    btn_print.on_clicked(lambda event: imprimir_matriz())

    cores_legenda = cores
    labels = ["0", "1", "2", "3"]
    patches = [mpatches.Patch(color=cor, label=lab) for cor, lab in zip(cores_legenda, labels)]
    plt.legend(handles=patches, bbox_to_anchor=(1.05, 1), loc='upper left')

    plt.show()

def GUI_Home():
    root = tk.Tk()
    root.title("Simulação de Meko")

    tk.Label(root, text="Bem-vindo à Simulação de Meko!", font=("Helvetica", 16)).pack(pady=20)

    tk.Button(root, text="Gerar Novo Meko", command=GUI_Gera_Meko, width=20, height=2).pack(pady=10)
    tk.Button(root, text="Gerar Ambiente", command=GUI_Gera_Ambiente, width=20, height=2).pack(pady=10)

    root.mainloop()