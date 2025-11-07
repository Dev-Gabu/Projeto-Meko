import os
import json
from datetime import datetime

class SimulationLogger:
    def __init__(self, filename_prefix="sim_log"):
        self.log_geral = []
        self.log_geral_final_ = []
        self.log_meko_individual = {}
        self.start_time = datetime.now()
        self.filename_prefix = filename_prefix
        
        # Cria a pasta logs se não existir
        os.makedirs("logs", exist_ok=True)
        
    def log_geral_final(self, ambiente, inicio, fim, loop=None, n_mekos=None):
        """Registra os dados finais da simulação."""
        total_time = fim - inicio
        total_ticks = loop if loop is not None else len(self.log_geral)
        tamanho_grid = ambiente.size
        populacao_inicial = n_mekos
        populacao_final = self.log_geral[-1]['populacao_total']
        total_nascimentos = ambiente.total_nascimentos
        total_mortes_combate = ambiente.total_mortes_combate
        total_mortes_fome = ambiente.total_mortes_fome
        total_mortes_idade = ambiente.total_mortes_idade

        self.log_geral_final_.append({
            "tempo_simulacao": total_time,
            "tick": total_ticks,
            "populacao_final": populacao_final,
            "total_nascimentos": total_nascimentos,
            "total_mortes_combate": total_mortes_combate,
            "total_mortes_fome": total_mortes_fome,
            "total_mortes_idade": total_mortes_idade
        })

    def log_geral_tick(self, tick, mekos_list, nascimentos_tick=0):
        """Coleta e armazena dados macro da simulação."""
        if not mekos_list:
            pop_count = 0
            avg_fitness = 0
        else:
            pop_count = len(mekos_list)
            avg_fitness = sum(m.fitness for m in mekos_list) / pop_count

        self.log_geral.append({
            "tick": tick,
            "populacao_total": pop_count,
            "fitness_medio": round(avg_fitness, 2),
            'nascimentos': nascimentos_tick
        })

    def log_meko_data(self, tick, meko):
        """
        Coleta o estado atual de um Meko específico e o armazena em seu histórico individual.
        """
        nome = meko.nome
        
        if nome not in self.log_meko_individual:
            self.log_meko_individual[nome] = {
                "Genoma": meko.genoma,
                "Idade maxima": meko.idade,
                "Abates": meko.abates,
                "Atributos": {
                    "Forca": meko.forca,
                    "Resistencia": meko.resistencia,
                    "Velocidade": meko.velocidade,
                    "Visao": meko.visao,
                    "Agressividade": meko.agressividade,
                },
                "Genetica": {
                    "Nome Mae": meko.nome_mae,
                    "Genoma Mae": meko.genoma_mae,
                    "Nome Pai": meko.nome_pai,
                    "Genoma Pai": meko.genoma_pai
                },
                "Historico": []
            }
        
        estado_fsm = meko.fsm.current_state.name

        evento_log = f"HP: {meko.saude}/{meko.saudeMAX}, E: {meko.energia}/{meko.energiaMAX}, Fit: {meko.fitness:.2f}\n {estado_fsm} em ({int(meko.posicao[0])}, {int(meko.posicao[1])})\n {meko.log}"

        self.log_meko_individual[nome]["Historico"].append({
            "tick": int(tick),
            "log": evento_log
        })
   
    def gerar_relatorio_final(self, ambiente):
        """
        Gera um relatório estatístico final usando os dados acumulados.
        
        Args:
            ambiente (Ambiente): A instância do Ambiente para obter os totais finais.
        
        Returns:
            str: O relatório formatado.
        """
        
        total_ticks = len(self.log_geral)
        
        # 1. Dados Macroscópicos (do Log Geral)
        if not self.log_geral:
            return "Simulação não completou nenhuma iteração para gerar relatório."

        populacao_final = self.log_geral[-1]['populacao_total']
        
        # Calcula o Fitness Médio Total ao longo da simulação
        media_fitness_total = sum(d['fitness_medio'] for d in self.log_geral) / total_ticks
        
        # 2. Dados de Mortalidade (do Objeto Ambiente)
        mortes_combate = ambiente.total_mortes_combate
        mortes_fome = ambiente.total_mortes_fome
        mortes_idade = ambiente.total_mortes_idade
        total_nascimentos = ambiente.total_nascimentos

        # --- Geração do Relatório Textual ---
        relatorio = "\n" + "="*50 + "\n"
        relatorio += f"         RELATÓRIO FINAL DA SIMULAÇÃO         \n"
        relatorio += "="*50 + "\n"
        
        relatorio += f"DURAÇÃO DA SIMULAÇÃO: {total_ticks} Ticks\n"
        relatorio += f"POPULAÇÃO FINAL: {populacao_final} Mekos\n"
        relatorio += f"TOTAL DE NASCIMENTOS: {total_nascimentos}\n"
        relatorio += f"FITNESS MÉDIO GERAL: {media_fitness_total:.2f}\n"
        relatorio += "-"*50 + "\n"
        
        relatorio += "ESTATÍSTICAS DE MORTALIDADE:\n"
        relatorio += f"  > Morte por IDADE (Seleção Natural): {mortes_idade}\n"
        relatorio += f"  > Morte por COMBATE/DOMÍNIO: {mortes_combate}\n"
        relatorio += f"  > Morte por FOME/EFICIÊNCIA: {mortes_fome}\n"
        relatorio += "-"*50 + "\n"

        # Adiciona sugestão para análise dos logs JSON
        relatorio += f"Para análise detalhada, consulte os arquivos JSON na pasta 'logs/'.\n"
        
        return relatorio

    def export_logs(self):
        """Salva os logs em arquivos JSON (ou CSV, mas JSON é mais fácil com Python)."""
        timestamp = self.start_time.strftime("%Y%m%d_%H%M%S")
        
        # Exportar Log Geral
        filename_geral = os.path.join("logs", f"{self.filename_prefix}_geral_{timestamp}.json")
        with open(filename_geral, 'w') as f:
            self.log_geral_final_.append(self.log_geral)
            json.dump(self.log_geral_final_, f, indent=4)
        print(f"\nLOG GERAL salvo em: {filename_geral}")

        # Exportar Log Individual Detalhado
        filename_individual = os.path.join("logs", f"{self.filename_prefix}_individual_{timestamp}.json")
        with open(filename_individual, 'w') as f:
            json.dump(self.log_meko_individual, f, indent=4)
        print(f"LOG INDIVIDUAL salvo em: {filename_individual}")