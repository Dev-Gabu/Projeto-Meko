# Simulação de Meko

Este projeto é uma simulação interativa de criaturas chamadas **Mekos**, permitindo a criação, visualização e manipulação de genomas, além da geração de ambientes com diferentes biomas e recursos.

## Funcionalidades

- **Criação de Mekos:**  
  Interface gráfica para seleção de características genéticas e visualização do sprite gerado a partir do genoma.
- **Validação de Genoma:**  
  Função robusta para garantir que os genomas criados são válidos conforme as regras do sistema.
- **Geração de Ambiente:**  
  Criação de grids representando diferentes biomas, com distribuição visual de cores e recursos.
- **Sprites Dinâmicos:**  
  Montagem automática do sprite do Meko conforme as características selecionadas, incluindo variações dependentes (ex: garras diferentes para tipos de patas).
- **Interface Gráfica (GUI):**  
  Menus para criar Mekos, gerar ambientes e visualizar atributos.

## Estrutura dos Arquivos

- `settings.py` — Configurações globais, colormap, caminhos de sprites e características.
- `utils.py` — Funções utilitárias, validação de genoma e montagem de sprites.
- `GUI.py` — Interface gráfica principal (Tkinter e Matplotlib).
- `ambiente.py` — Funções para geração e manipulação do ambiente (biomas, recursos).
- `meko.py` — Classe principal dos Mekos e lógica de atributos.
- `assets/` — Pasta com sprites e imagens utilizadas.
- `main.py` — Executa o código principal.

## Como Executar

1. **Crie um ambiente virtual:**
   ```bash
   python -m venv venv
   ```

2. **Ative o ambiente virtual:**
    ```bash
    venv\Script\Activate
    ```

3. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

4. **Execute o projeto:**
    ```bash
    python main.py
    ```

5. **Navegue pelo menu:**
   - **Gerar Novo Meko:** Crie e visualize um novo Meko.
   - **Gerar Ambiente:** Visualize o grid do ambiente e distribua recursos.

## Observações

- Os sprites devem estar na pasta `assets/sprites/` conforme os nomes definidos em `settings.py`.
- O sistema utiliza Python 3.8+.
- Para personalizar as características ou sprites, edite o arquivo `settings.py`.

## Licença

Este é um projeto acadêmico desenvolvido por Gabriel Tavares dos Santos.