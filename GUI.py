import tkinter as tk
import os, random
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button

import matplotlib.patches as mpatches
import settings

from ambiente import Ambiente, biome_gen, fruit_gen, river_gen, Fruta
from meko import Meko
from settings import CARACTERISTICAS, GRID_SIZE, CMAP, cores, NORM, legendas, SIMULATION_STEPS, fruit_list, mekos_list, meat_list
from utils import sprite_por_genoma, importar_meko, exportar_meko, importar_ambiente



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

    def importarM():
        """
        Importa dados de Meko Salvos
        """

        caminho = filedialog.askopenfilename(
            title="Selecione um arquivo",
            filetypes=[("Arquivos Pickle", "*.pkl"), ("Todos os arquivos", "*.*")],
        initialdir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "assets",
            "mekos"
        ))

        if not caminho:
            raise FileNotFoundError("Nenhum arquivo selecionado.")

        dados = importar_meko(caminho)

        try:
            meko = Meko(dados["nome"], dados["genoma"])

        except Exception as e:
            messagebox.showerror("Erro ao importar", str(e))
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

    def exportarM():
        caminho = filedialog.asksaveasfilename(
            title="Salvar arquivo",
            defaultextension=".pkl",
            filetypes=[("Arquivos Pickle", "*.pkl"), ("Todos os arquivos", "*.*")],
        initialdir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "assets",
            "mekos"
        ))

        if not caminho:
            return

        dados = {
        "nome": nome_var.get(),
        "genoma": {caracteristica: var.get() for caracteristica, var in entries.items()}
        }
    
        exportar_meko(caminho, dados)

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

        tk.Button(janela_atributos, text="Exportar", command=exportarM).grid(row=row, column=0, padx=10, pady=5, sticky="w")

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
    tk.Button(root, text="Importar", command=importarM).grid(row=len(CARACTERISTICAS)+1, column=0, pady=10)
    tk.Button(root, text="Confirmar", command=confirmar).grid(row=len(CARACTERISTICAS)+1, column=1, pady=10)

def GUI_Gera_Ambiente():
    """
    A função cria uma grade que representa o ambiente onde os Mekos irão interagir.

    Funcionalidade:
        `gerar_bioma`: Gera biomas no ambiente.
        `gerar_frutas`: Gera frutas no ambiente.
        `gerar_rios`: Gera rios no ambiente.
        `imprimir_matriz`: Imprime a matriz do ambiente no console.
        `importarA`: Permite importar um ambiente previamente salvo.
        `exportarA`: Permite salvar o ambiente atual em um arquivo.
    """
    size = GRID_SIZE

    grid = np.zeros((size, size))

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

    def importarA():
        matriz = importar_ambiente()

        nonlocal grid
        grid = matriz
        im.set_data(grid)
        plt.pause(0.1)
    
    def exportarA(grid):
        caminho = filedialog.asksaveasfilename(
        title="Salvar arquivo",
        filetypes=[("Arquivos NumPy", "*.npy"), ("Todos os arquivos", "*.*")],
        defaultextension=".npy",
        initialdir=os.path.dirname(os.path.abspath(__file__))
        )

        if not caminho:
            raise FileNotFoundError("Nenhum arquivo selecionado.")
        
        np.save(caminho, grid)
        print(f"Matriz salva em: {caminho}")

    ax_bioma = plt.axes([0.7, 0.05, 0.075, 0.05])
    btn_bioma = Button(ax_bioma, 'Bioma')
    btn_bioma.on_clicked(lambda event: gerar_bioma())

    ax_frutas = plt.axes([0.8, 0.05, 0.075, 0.05])
    btn_frutas = Button(ax_frutas, 'Frutas')
    btn_frutas.on_clicked(lambda event: gerar_frutas())

    ax_rios = plt.axes([0.9, 0.05, 0.075, 0.05])
    btn_rios = Button(ax_rios, 'Rios')
    btn_rios.on_clicked(lambda event: gerar_rios())

    ax_importar = plt.axes([0.5, 0.05, 0.075, 0.05])
    btn_importar = Button(ax_importar, 'Importar')
    btn_importar.on_clicked(lambda event: importarA())

    ax_exportar = plt.axes([0.4, 0.05, 0.075, 0.05])
    btn_exportar = Button(ax_exportar, 'Exportar')
    btn_exportar.on_clicked(lambda event: exportarA(grid))

    ax_print = plt.axes([0.6, 0.05, 0.075, 0.05])
    btn_print = Button(ax_print, 'Print')
    btn_print.on_clicked(lambda event: imprimir_matriz())

    patches = [mpatches.Patch(color=cor, label=lab) for cor, lab in zip(cores, legendas)]
    ax.legend(handles=patches, bbox_to_anchor=(-0.45, 0.5), loc='center left', borderaxespad=0.)

    plt.show()

def GUI_Simulacao():
    import matplotlib.pyplot as plt
    from matplotlib import gridspec
    from matplotlib.widgets import Button
    import numpy as np
    import os
    from tkinter import filedialog, messagebox

    # Variável de estado global para controlar o pause
    global is_paused
    is_paused = False
    
    # Função de callback do botão
    def toggle_pause(event):
        global is_paused
        is_paused = not is_paused
        if is_paused:
            pause_button.label.set_text("Continuar")
        else:
            pause_button.label.set_text("Pausar")
        plt.draw()

    # --- Ambiente ---
    ambiente_base = importar_ambiente()
    ambiente = Ambiente(GRID_SIZE, ambiente_base)

#--- Frutas ---
    for i, linha in enumerate(ambiente.matriz):
        for j, valor in enumerate(linha):
            if valor == 4:
                fruta = Fruta((i, j))
                settings.fruit_list.append(fruta)

    # --- Mekos ---
    Quantidade_Mekos = 4

    for i in range(Quantidade_Mekos):
        caminho = filedialog.askopenfilename(
            title="Selecione um Meko",
            filetypes=[("Arquivos Pickle", "*.pkl"), ("Todos os arquivos", "*.*")],
            initialdir=os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "assets",
                "mekos"
            )
        )

        if not caminho:
            raise FileNotFoundError("Nenhum arquivo selecionado.")

        dados = importar_meko(caminho)
        try:
            meko_inst = Meko(
                dados["nome"],
                dados["genoma"],
                (random.randint(0, ambiente.size-1), random.randint(0, ambiente.size-1))
            )
        except Exception as e:
            messagebox.showerror("Erro ao importar", str(e))
            return

        ambiente.adicionar_meko(meko_inst)
        mekos_list.append(meko_inst)

    # --- Configuração Simulação e Monitoramento
    fig = plt.figure(figsize=(12, 6))
    gs = gridspec.GridSpec(1, 2, width_ratios=[3, 1])
    
    ax_sim = fig.add_subplot(gs[0])
    ax_sim.set_title("Simulação")

    ax_attr = fig.add_subplot(gs[1])
    ax_attr.axis("off")
    
    ax_attr.set_xlim(0, 2)
    ax_attr.set_ylim(0, 1)
    ax_attr.set_aspect('equal')
    num_mekos = len(mekos_list)
    y_step = 1 / (num_mekos + 1)
    meko_artists = []

    sprite_size = 0.3
    espaco_extra = 0.1

    num_mekos = len(mekos_list)
    total_step = sprite_size + espaco_extra
    y_start = 1 - total_step / 2
    
    meko_artists = []

    for idx, meko in enumerate(mekos_list):
        y = y_start - idx * total_step
        sprite = np.array(sprite_por_genoma(meko.genoma).resize((32, 32)))
        im_artist = ax_attr.imshow(sprite, extent=(0, 1, y - sprite_size/2, y + sprite_size/2))
        txt_artist = ax_attr.text(1.1, y,
                                f"{meko.nome}\nE: {meko.energia} S: {meko.saude}\n{meko.fsm.current_state.name}",
                                va="center", fontsize=8, color="green")
        meko_artists.append((meko, im_artist, txt_artist))
    
    # --- Adiciona o botão de pause
    ax_button = fig.add_axes([0.8, 0.05, 0.1, 0.075])
    pause_button = Button(ax_button, "Pausar")
    pause_button.on_clicked(toggle_pause)
    
    plt.ion()
    plt.show()

    # --- Loop da simulação ---
    for step in range(SIMULATION_STEPS):
        # AQUI: Loop de espera para o estado de pausa
        while is_paused:
            plt.pause(0.1)

        print("\n Passo:", step)
        ambiente.tick()
        ambiente.renderizar(ax_sim)
        
        for meko, im_artist, txt_artist in meko_artists:
            sprite = np.array(sprite_por_genoma(meko.genoma).resize((32, 32)))
            im_artist.set_data(sprite)
            txt_artist.set_text(f"{meko.nome}\nE: {meko.energia} S: {meko.saude}\n{meko.fsm.current_state.name}")
            if not meko.esta_vivo(): txt_artist.set_color("gray")

        plt.draw()
        plt.pause(0.5)

# def GUI_Simulacao():
#     """
#     Função responsável pela interface gráfica da simulação. Onde o usuário pode selecionar o ambiente em arquivo `.npy` e mekos em arquivo `.pkl` previamente salvos.
#     """

#     import matplotlib.pyplot as plt
#     from matplotlib import gridspec
#     import numpy as np

#     # --- Ambiente ---
#     ambiente_base = importar_ambiente()
#     ambiente = Ambiente(GRID_SIZE, ambiente_base)

#     # --- Frutas ---
#     for i, linha in enumerate(ambiente.matriz):
#         for j, valor in enumerate(linha):
#             if valor == 4:
#                 fruta = Fruta((i, j))
#                 settings.fruit_list.append(fruta)

#     # --- Mekos ---
#     Quantidade_Mekos = 4

#     for i in range(Quantidade_Mekos):
#         caminho = filedialog.askopenfilename(
#             title="Selecione um Meko",
#             filetypes=[("Arquivos Pickle", "*.pkl"), ("Todos os arquivos", "*.*")],
#             initialdir=os.path.join(
#                 os.path.dirname(os.path.abspath(__file__)),
#                 "assets",
#                 "mekos"
#             )
#         )

#         if not caminho:
#             raise FileNotFoundError("Nenhum arquivo selecionado.")

#         dados = importar_meko(caminho)
#         try:
#             meko_inst = Meko(
#                 dados["nome"],
#                 dados["genoma"],
#                 (random.randint(0, ambiente.size-1), random.randint(0, ambiente.size-1))
#             )
#         except Exception as e:
#             messagebox.showerror("Erro ao importar", str(e))
#             return

#         ambiente.adicionar_meko(meko_inst)
#         mekos_list.append(meko_inst)

#     # --- Configuração Simulação e Monitoramento
#     fig = plt.figure(figsize=(12, 6))
#     gs = gridspec.GridSpec(1, 2, width_ratios=[3, 1])
    
#     ax_sim = fig.add_subplot(gs[0])
#     ax_sim.set_title("Simulação")

#     ax_attr = fig.add_subplot(gs[1])
#     ax_attr.axis("off")
#     ax_attr.set_xlim(0, 2)
#     ax_attr.set_ylim(0, 1)
#     ax_attr.set_aspect('equal')

#     num_mekos = len(mekos_list)
#     y_step = 1 / (num_mekos + 1)
#     meko_artists = []

#     sprite_size = 0.3
#     espaco_extra = 0.1

#     num_mekos = len(mekos_list)
#     total_step = sprite_size + espaco_extra
#     y_start = 1 - total_step / 2

#     meko_artists = []

#     for idx, meko in enumerate(mekos_list):
#         y = y_start - idx * total_step
#         sprite = np.array(sprite_por_genoma(meko.genoma).resize((32, 32)))
#         im_artist = ax_attr.imshow(sprite, extent=(0, 1, y - sprite_size/2, y + sprite_size/2))
#         txt_artist = ax_attr.text(1.1, y,
#                                 f"{meko.nome}\nE: {meko.energia} S: {meko.saude}\n{meko.fsm.current_state.name}",
#                                 va="center", fontsize=8, color="green")
#         meko_artists.append((meko, im_artist, txt_artist))

#     plt.ion()
#     plt.show()

#     # --- Loop da simulação ---
#     for step in range(SIMULATION_STEPS):
#         print("\n Passo:", step)
#         ambiente.tick()
#         ambiente.renderizar(ax_sim)
        
#         for meko, im_artist, txt_artist in meko_artists:
#             sprite = np.array(sprite_por_genoma(meko.genoma).resize((32, 32)))
#             im_artist.set_data(sprite)
#             txt_artist.set_text(f"{meko.nome}\nE: {meko.energia} S: {meko.saude}\n{meko.fsm.current_state.name}")
#             if not meko.esta_vivo(): txt_artist.set_color("gray")

#         plt.draw()
#         plt.pause(0.5)

#     plt.ioff()
#     plt.show()

def GUI_Home():
    """
    Função responsável pela interface gráfica do menu principal.
    """
    root = tk.Tk()
    root.title("Projeto Meko")

    tk.Label(root, text="Geradores", font=("Helvetica", 16)).pack(pady=20)

    tk.Button(root, text="Gerar Meko", command=GUI_Gera_Meko, width=20, height=2).pack(pady=10)
    tk.Button(root, text="Gerar Ambiente", command=GUI_Gera_Ambiente, width=20, height=2).pack(pady=10)

    tk.Label(root, text="Simulação", font=("Helvetica", 16)).pack(pady=20)

    tk.Button(root, text="Iniciar Simulação", command=GUI_Simulacao, width=20, height=2).pack(pady=10)

    root.mainloop()