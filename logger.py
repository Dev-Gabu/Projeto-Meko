import os
import json
from datetime import datetime

class SimulationLogger:
    def __init__(self, filename_prefix="sim_log"):
        self.log_geral = []
        self.log_meko_individual = []
        self.start_time = datetime.now()
        self.filename_prefix = filename_prefix
        
        # Cria a pasta logs se não existir
        os.makedirs("logs", exist_ok=True)

    def log_geral_tick(self, tick, mekos_list):
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
            # Futuros: n_nascimentos, n_mortes_fome, etc.
        })

    def log_meko_data(self, tick, meko):
        """Coleta o estado atual de um Meko específico para análise individual."""
        self.log_meko_individual.append({
            "tick": tick,
            "nome": meko.nome,
            "fitness": round(meko.fitness, 2),
            "saude": meko.saude,
            "energia": meko.energia,
            "idade": meko.idade,
            "estado": meko.fsm.current_state.name,
            "tipo": meko.genoma[0], 
            "fertilidade": meko.fertilidade,
            # Útil para diagnóstico de combate
            "agressividade": meko.agressividade,
            "target_nome": meko.target.nome if meko.target else None 
        })

    def export_logs(self):
        """Salva os logs em arquivos JSON (ou CSV, mas JSON é mais fácil com Python)."""
        timestamp = self.start_time.strftime("%Y%m%d_%H%M%S")
        
        # Exportar Log Geral
        filename_geral = os.path.join("logs", f"{self.filename_prefix}_geral_{timestamp}.json")
        with open(filename_geral, 'w') as f:
            json.dump(self.log_geral, f, indent=4)
        print(f"\nLOG GERAL salvo em: {filename_geral}")

        # Exportar Log Individual Detalhado
        filename_individual = os.path.join("logs", f"{self.filename_prefix}_individual_{timestamp}.json")
        with open(filename_individual, 'w') as f:
            json.dump(self.log_meko_individual, f, indent=4)
        print(f"LOG INDIVIDUAL salvo em: {filename_individual}")