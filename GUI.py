import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button

import matplotlib.patches as mpatches

from ambiente import biome_gen, fruit_gen, river_gen
from meko import Meko
from settings import CARACTERISTICAS, GRID_SIZE, CMAP, cores, NORM, legendas
from utils import sprite_por_genoma

def GUI_Gera_Meko():

    """
    Função responsável pela interface gráfica de criação de genomas para os Meko.

    Nessa função, o usuário pode selecionar as características desejadas para criar um novo Meko. E com base nessas características, serão gerados os atributos do Meko e sua aparência.

    """

    root = tk.Toplevel()
    root.title("Criador de Genomas - Meko")
    entries = {}
    default_values = {}

    tk.Label(root, text="Nome do Meko:").grid(row=len(CARACTERISTICAS), column=0, padx=5, pady=5, sticky="w")

    nome_var = tk.StringVar(master=root, value="Meko")
    nome = tk.Entry(root, textvariable=nome_var)
    nome.grid(row=len(CARACTERISTICAS), column=1, padx=5, pady=5)

    # Criação dos campos
    for i, (caracteristica, opcoes) in enumerate(CARACTERISTICAS):
        tk.Label(root, text=caracteristica).grid(row=i, column=0, padx=5, pady=5, sticky="w")
        var = tk.StringVar(value=opcoes[0])
        combo = ttk.Combobox(root, textvariable=var, values=opcoes, state="readonly")
        combo.grid(row=i, column=1, padx=5, pady=5)
        entries[caracteristica] = var
        default_values[caracteristica] = opcoes[0]

    def limpar():
        """
        Limpa os campos do formulário.
        """
        for caracteristica, var in entries.items():
            var.set(default_values[caracteristica])
        nome_var.set("")

    def confirmar():
        """
        Confirma a criação do Meko e exibe a tela da interface contendo seus atributos e sua imagem.

        A função analisa o genoma e tenta criar um objeto Meko. Com o objeto criado, uma nova tela é aberta exibindo o novo Meko criado com seus atributos distribuídos e sua aparência.
        """
        genoma = [var.get() for var in entries.values()]
        try:
            meko = Meko(nome_var.get(), genoma)
        except Exception as e:
            messagebox.showerror("Erro", str(e))
            return

        janela_atributos = tk.Toplevel(root)
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
        label_imagem.image = sprite_tk
        label_imagem.grid(row=0, column=1, rowspan=row, padx=10, pady=5)

    # Botões
    tk.Button(root, text="Limpar Campos", command=limpar).grid(row=len(CARACTERISTICAS)+1, column=0, pady=10)
    tk.Button(root, text="Confirmar Criação", command=confirmar).grid(row=len(CARACTERISTICAS)+1, column=1, pady=10)

def GUI_Gera_Ambiente():
    size = GRID_SIZE

    grid = np.random.choice([0, 1, 2], size=(size, size), p=[0.2, 0.3, 0.5])

    _, ax = plt.subplots()

    im = ax.imshow(grid, cmap=CMAP, norm=NORM, interpolation='nearest')

    def gerar_bioma():
        nonlocal grid

        config_win = tk.Toplevel()
        config_win.title("Distribuição dos Biomas")

        n_biomas = 4
        scales = []
        valores = []

        def atualizar_labels():
            total = sum(var.get() for var in valores)
            for i, lbl in enumerate(labels):
                pct = 100 * valores[i].get() / (total if total > 0 else 1)
                lbl.config(text=f"{pct:.1f}%")

        labels = []
        for i in range(n_biomas):
            tk.Label(config_win, text=legendas[i]).grid(row=i, column=0, padx=5, pady=5)
            var = tk.DoubleVar(value=25)
            scale = tk.Scale(config_win, from_=0, to=100, orient="horizontal", variable=var, command=lambda e: atualizar_labels())
            scale.grid(row=i, column=1, padx=5, pady=5)
            lbl = tk.Label(config_win, text="25.0%")
            lbl.grid(row=i, column=2, padx=5, pady=5)
            valores.append(var)
            labels.append(lbl)

        def confirmar():
            pesos = [v.get() for v in valores]
            soma = sum(pesos)
            if soma == 0:
                messagebox.showerror("Erro", "A soma das porcentagens deve ser maior que zero.")
                return
            biome_weights = [p/soma for p in pesos]
            config_win.destroy()
            nonlocal grid
            grid = biome_gen(grid, size, n_biomas=n_biomas, scale=10.0, seed=None, biome_weights=biome_weights)
            im.set_data(grid)
            plt.pause(0.1)

        tk.Button(config_win, text="Confirmar", command=confirmar).grid(row=n_biomas, column=0, columnspan=3, pady=10)
        atualizar_labels()

    def gerar_frutas():
        nonlocal grid
        grid = fruit_gen(grid, size)
        im.set_data(grid)
        plt.pause(0.1)

    def gerar_rios():
        nonlocal grid
        grid = river_gen(grid, size)
        im.set_data(grid)
        plt.pause(0.1)

    def imprimir_matriz():
        print("\n".join(" ".join(map(str, linha)) for linha in grid))

    ax_bioma = plt.axes([0.7, 0.05, 0.075, 0.05])
    btn_bioma = Button(ax_bioma, 'Bioma')
    btn_bioma.on_clicked(lambda event: gerar_bioma())

    ax_frutas = plt.axes([0.8, 0.05, 0.075, 0.05])
    btn_frutas = Button(ax_frutas, 'Frutas')
    btn_frutas.on_clicked(lambda event: gerar_frutas())

    ax_rios = plt.axes([0.9, 0.05, 0.075, 0.05])
    btn_rios = Button(ax_rios, 'Rios')
    btn_rios.on_clicked(lambda event: gerar_rios())

    ax_print = plt.axes([0.6, 0.05, 0.075, 0.05])
    btn_print = Button(ax_print, 'Print')
    btn_print.on_clicked(lambda event: imprimir_matriz())

    patches = [mpatches.Patch(color=cor, label=lab) for cor, lab in zip(cores, legendas)]
    ax.legend(handles=patches, bbox_to_anchor=(-0.45, 0.5), loc='center left', borderaxespad=0.)

    plt.show()

def GUI_Home():
    root = tk.Tk()
    root.title("Simulação de Meko")

    tk.Label(root, text="Bem-vindo à Simulação de Meko!", font=("Helvetica", 16)).pack(pady=20)

    tk.Button(root, text="Gerar Novo Meko", command=GUI_Gera_Meko, width=20, height=2).pack(pady=10)
    tk.Button(root, text="Gerar Ambiente", command=GUI_Gera_Ambiente, width=20, height=2).pack(pady=10)

    root.mainloop()