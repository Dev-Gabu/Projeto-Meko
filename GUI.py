import tkinter as tk
import os, random
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from matplotlib import gridspec, animation
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
from matplotlib.widgets import Button

import settings

from ambiente import Ambiente, biome_gen, fruit_gen, river_gen, Fruta
from meko import Meko
from settings import CARACTERISTICAS, GRID_SIZE, CMAP, cores, NORM, legendas, SIMULATION_STEPS, SIMULATION_DELAY, mekos_list
from utils import sprite_por_genoma, importar_meko, exportar_meko, importar_ambiente, gerar_nome

class MekoDetailWindow(tk.Toplevel):
    def __init__(self, parent_root, meko):
        super().__init__(parent_root)
        self.title(f"Detalhes: {meko.nome}")
        self.meko = meko
        self.sprite = sprite_por_genoma(self.meko.genoma)
        
        self.create_widgets()
        
    def create_widgets(self):
        if self.sprite is None:
            tk.Label(self, text="Erro ao carregar sprite").pack(pady=10)
        else:
            self.sprite = self.sprite.resize(
                (self.sprite.width * 4, self.sprite.height * 4), 
                Image.NEAREST
            )
            self.sprite_tk = ImageTk.PhotoImage(self.sprite,master=self) 
            self.label_imagem = tk.Label(self, image=self.sprite_tk)
            self.label_imagem.pack(pady=10)

        # --- Exibição dos Atributos ---
        attr_text = f"Nome: {self.meko.nome}\n"
        attr_text += f"Saúde: {self.meko.saude}/{self.meko.saudeMAX}\n"
        attr_text += f"Estado: {self.meko.fsm.current_state.name}\n"
        attr_text += f"Genoma: {', '.join(self.meko.genoma)}\n\n"
        attr_text += f"Atributos: PESO: {self.meko.peso}, VELOCIDADE: {self.meko.velocidade}, RESISTÊNCIA: {self.meko.resistencia}\nFORÇA: {self.meko.forca}, VISÃO: {self.meko.visao}, AGRESSIVIDADE: {self.meko.agressividade}"
        
        tk.Label(self, text=attr_text, justify=tk.LEFT).pack(padx=20, pady=10)

class MekoOverviewWindow(tk.Toplevel):
    def __init__(self, parent_root, mekos_list):
        super().__init__(parent_root)
        self.title("Visão Geral da Simulação")
        self.mekos_list = mekos_list
        self.sprites = [sprite_por_genoma(meko.genoma) for meko in mekos_list] 
        
        self.create_widgets()
        
    def create_widgets(self):
        main_frame = tk.Frame(self)
        main_frame.pack(fill="both", expand=True)

        for index, meko in enumerate(self.mekos_list):
            column = index % 2
            row = index // 2
            
            meko_frame = tk.Frame(main_frame, borderwidth=1, relief="groove")
            meko_frame.grid(row=row, column=column, padx=10, pady=10, sticky="n")

            attr_text = (
            f"Nome: {meko.nome} || Idade: {meko.idade}\n"
            f"Saúde: {meko.saude}/{meko.saudeMAX} || Energia: {meko.energia}/{meko.energiaMAX}\n"
            f"Estado: {meko.fsm.current_state.name}"
            )
        
            tk.Label(meko_frame, text=attr_text, justify=tk.LEFT, anchor="w").pack(padx=5, pady=5)

class MekoMonitorWindow:
    def __init__(self, mekos_list):
        self.root = tk.Tk()
        self.root.title("Monitoramento da Simulação")
        self.mekos_list = mekos_list
        self.detail_windows = []
        
        self.create_widgets()
        self.root.protocol("WM_DELETE_WINDOW", self.hide) 
        
        self.update_list(mekos_list)

    def close_all_windows(self):
        """Fecha todas as janelas de detalhes e oculta a janela principal."""
        for window in self.detail_windows:
            if window.root.winfo_exists():
                window.root.destroy()
        self.detail_windows = []
        self.hide()

    def hide(self):
        """Oculta a janela principal."""
        self.root.withdraw()

    def show(self):
        """Mostra a janela principal."""
        self.root.deiconify()

    def update_list(self, mekos_list):
        """Atualiza a lista de Mekos exibida."""
        self.mekos_list = mekos_list
        
        # Condição 2: Ordena a lista de Mekos pelo Fitness
        # Assumindo que o atributo 'fitness' existe no objeto Meko
        # self.mekos_list.sort(key=lambda m: getattr(m, 'fitness', 0), reverse=True)
        
        # Limpa o conteúdo antigo
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        # Exibe a lista de Mekos como itens clicáveis
        for meko in self.mekos_list:
            display_text = f"[{getattr(meko, 'fitness', 0):.2f}] {meko.nome}"
            
            btn = tk.Button(self.list_frame, 
                            text=display_text, 
                            anchor="w", 
                            command=lambda m=meko: self.open_detail(m))
            btn.pack(fill='x', padx=5, pady=2)

    def open_detail(self, meko):
        """Abre uma nova janela de detalhes para o Meko selecionado."""
        detail_window = MekoDetailWindow(self.root, meko)
        self.detail_windows.append(detail_window)
        
    def open_overview(self, mekos_list):
        """Abre uma nova janela de detalhes gerais da simulação."""
        overview_window = MekoOverviewWindow(self.root, mekos_list)
        self.detail_windows.append(overview_window)

    def create_widgets(self):
        tk.Label(self.root, text="Monitor de Mekos", font=("Helvetica", 16)).pack(pady=10)
        self.list_frame = tk.Frame(self.root)
        self.list_frame.pack(padx=10, pady=5, fill='both', expand=True)
        tk.Button(self.root, text="Ocultar Monitor", command=self.hide).pack(pady=10)
        tk.Button(self.root, text="Visualização Geral", command=lambda: self.open_overview(mekos_list)).pack(pady=10)

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
        
        """
        Exporta os dados de um meko como arquivo .pkl
        """
        
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

def GUI_Gera_Ambiente(size):
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
    size = size.get()

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

def GUI_Simulacao(N_mekos):
    # Variável de estado global para controlar o pause
    global is_paused
    is_paused = False
    monitor_window = None

    def toggle_pause_monitor(event, mekos_list):
        global is_paused, monitor_window
        is_paused = not is_paused
        
        if is_paused:
            event.button.label.set_text("Continuar")
            
            if monitor_window is None:
                monitor_window = MekoMonitorWindow(mekos_list)
            else:
                monitor_window.update_list(mekos_list)
                monitor_window.show() 

        else:
            event.button.label.set_text("Pausar")
            
            if monitor_window is not None:
                monitor_window.close_all_windows()
                monitor_window = None

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
    Quantidade_Mekos = N_mekos.get()

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
                ambiente,
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
    
    # --- Adiciona o botão de pause
    ax_button = fig.add_axes([0.8, 0.05, 0.1, 0.075])
    pause_button = Button(ax_button, "Pausar")
    pause_button.on_clicked(lambda event: toggle_pause_monitor(event, mekos_list))
    
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

        plt.draw()
        plt.pause(SIMULATION_DELAY)

def GUI_Aleatoria(n_mekos,size_var,loop_var):
    global is_paused, monitor_window
    is_paused = False
    monitor_window = None
    size = size_var.get()
    loop = loop_var.get()

    def toggle_pause_monitor(event, button_object, mekos_list):
        global is_paused, monitor_window
        is_paused = not is_paused
        
        if is_paused:
            button_object.label.set_text("Continuar")
            
            if monitor_window is None:
                monitor_window = MekoMonitorWindow(mekos_list)
            else:
                monitor_window.update_list(mekos_list)
                monitor_window.show() 

        else:
            button_object.label.set_text("Pausar")
            
            if monitor_window is not None:
                monitor_window.close_all_windows()
                monitor_window = None
                
    def update_frame(i):
        """Executa um passo de simulação."""
        global is_paused
        
        if is_paused:
            return
            
        print("\n Passo:", i)
        ambiente.tick()
        ambiente.renderizar(ax_sim)
        
        return ax_sim

    # --- Ambiente ---
    
    grid = np.zeros((size, size))
    n_biomas = random.randint(2, 4)
    scale = random.uniform(5.0, 30.0)
    random_weights = [random.random() for _ in range(n_biomas)]
    soma_total = sum(random_weights)
    biome_weights = [w / soma_total for w in random_weights]
    seed = random.randint(0, 99999)
    
    ambiente_base = biome_gen(grid,size,n_biomas,scale,seed,biome_weights)
    ambiente_base = fruit_gen(ambiente_base,size)
    ambiente_base = river_gen(ambiente_base,size)
    
    ambiente = Ambiente(size, ambiente_base)

#--- Frutas ---
    for i, linha in enumerate(ambiente.matriz):
        for j, valor in enumerate(linha):
            if valor == 4:
                fruta = Fruta((i, j))
                settings.fruit_list.append(fruta)

    # --- Mekos ---
    n_iteracoes = max(n_mekos.get(),1)
    for i in range(n_iteracoes):
        
        genoma = [random.choice(valores) for _, valores in CARACTERISTICAS]
        
        try:
            meko_inst = Meko(
                gerar_nome(),
                genoma,
                ambiente,
                (random.randint(0, ambiente.size-1), random.randint(0, ambiente.size-1))
            )
            
        except Exception as e:
            messagebox.showerror("Erro ao criar meko aleatório", str(e))
            continue

        ambiente.adicionar_meko(meko_inst)
        mekos_list.append(meko_inst)

    # --- Configuração Simulação e Monitoramento
    fig = plt.figure(figsize=(12, 6))
    gs = gridspec.GridSpec(1, 2, width_ratios=[3, 1])
    
    ax_sim = fig.add_subplot(gs[0])
    ax_sim.set_title("Simulação")
    
    # --- Adiciona o botão de pause
    ax_button = fig.add_axes([0.8, 0.05, 0.1, 0.075])
    pause_button = Button(ax_button, "Pausar")
    pause_button.on_clicked(lambda event: toggle_pause_monitor(event, pause_button, mekos_list))

    # --- Loop da simulação ---
    anim = animation.FuncAnimation(
        fig, 
        update_frame, 
        frames= loop, 
        interval=500, 
        blit=False,
        repeat=False
    )
    
    plt.show()

def GUI_Home():
    """
    Função responsável pela interface gráfica do menu principal.
    """
    root = tk.Tk()
    root.title("Projeto Meko")
    
    N_Mekos = tk.IntVar(value=10)
    loop = tk.IntVar(value=GRID_SIZE)
    size = tk.IntVar(value=SIMULATION_STEPS)

    tk.Label(root, text="Geradores", font=("Helvetica", 16)).pack(pady=20)

    tk.Button(root, text="Gerar Meko", command=GUI_Gera_Meko, width=20, height=2).pack(pady=10)
    
    frame_ambiente = tk.Frame(root)
    frame_ambiente.pack(pady=10)
    
    tk.Entry(
        frame_ambiente,
        textvariable = size,
        width=5,
        font=("Helvetica", 12),
        justify='center'
    ).pack(side=tk.LEFT, padx=5)
    
    tk.Button(
        frame_ambiente, 
        text="Gerar Ambiente", 
        command=lambda:GUI_Gera_Ambiente(size), 
        width=20, 
        height=2).pack(side=tk.LEFT)

    tk.Label(root, text="Simulação", font=("Helvetica", 16)).pack(pady=20)
    
    frame_controlada = tk.Frame(root)
    frame_controlada.pack(pady=10)
    
    tk.Entry(
        frame_controlada,
        textvariable = N_Mekos,
        width=5,
        font=("Helvetica", 12),
        justify='center'
    ).pack(side=tk.LEFT, padx=5)
    
    tk.Button(
        frame_controlada, 
        text="Simulação Controlada", 
        command=lambda:GUI_Simulacao(N_Mekos), 
        width=20, 
        height=2).pack(side=tk.LEFT)
    
    frame_aleatoria = tk.Frame(root)
    frame_aleatoria.pack(pady=10)

    tk.Entry(
        frame_aleatoria,
        textvariable = N_Mekos,
        width=5,
        font=("Helvetica", 12),
        justify='center'
    ).pack(side=tk.LEFT, padx=5)
    
    tk.Entry(
        frame_aleatoria,
        textvariable = size,
        width=5,
        font=("Helvetica", 12),
        justify='center'
    ).pack(side=tk.LEFT, padx=5)
    
    tk.Entry(
        frame_aleatoria,
        textvariable = loop,
        width=5,
        font=("Helvetica", 12),
        justify='center'
    ).pack(side=tk.LEFT, padx=5)

    tk.Button(
        frame_aleatoria,
        text="Simulação Aleatória",
        command=lambda: GUI_Aleatoria(N_Mekos, size, loop),
        width=20,
        height=2
    ).pack(side=tk.LEFT)

    root.mainloop()