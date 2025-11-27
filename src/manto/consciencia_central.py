# src/manto/consciencia_central.py
import logging
from typing import Dict, Any
from src.cognitive.cerebro import Cerebro
from src.shared.comunicacao import BarramentoEventos, Evento

logger = logging.getLogger(__name__)

class ConscienciaCentral:
    """
    O Manto. Planeja, delega e sintetiza. Não executa tarefas diretamente.
    """
    def __init__(self, cerebro: Cerebro, barramento: BarramentoEventos, tentaculos: Dict[str, Any]):
        self.cerebro = cerebro
        self.barramento = barramento
        self.tentaculos = tentaculos
        logger.info("🐙 Manto (Consciência Central) instanciado e pronto.")

    async def processar_missao(self, missao: str):
        """Recebe uma missão de alto nível e orquestra sua execução."""
        await self.barramento.publicar(Evento("EVENTO_RACIOCINIO", {"pensamento": f"🧠 Manto: Nova missão recebida: '{missao}'. Iniciando planejamento estratégico."}, "Manto"))
        
        # 1. Planejamento Estratégico
        plano_tatico = self._gerar_plano_tatico(missao)
        await self.barramento.publicar(Evento("EVENTO_RACIOCINIO", {"pensamento": f"📋 Manto: Plano tático gerado:\n{plano_tatico}"}, "Manto"))

        # 2. Execução do Plano
        for passo in plano_tatico.split('\n'):
            if not passo.strip(): continue
            
            # Delegação e execução de cada passo (lógica simplificada)
            await self.barramento.publicar(Evento("EVENTO_RACIOCINIO", {"pensamento": f"▶️ Manto: Executando passo: '{passo}'"}, "Manto"))
            
            # Roteamento (simulado)
            # Em um sistema completo, o TentaculoRoteador faria isso
            nome_especialista = self._rotear_tarefa(passo)
            
            if nome_especialista and nome_especialista in self.tentaculos:
                especialista = self.tentaculos[nome_especialista]
                resultado = await especialista.executar_tarefa(passo)
                await self.barramento.publicar(Evento("EVENTO_RACIOCINIO", {"pensamento": f"✅ Manto: Passo concluído por {nome_especialista}. Resultado: {str(resultado)[:150]}..."}, "Manto"))
            else:
                await self.barramento.publicar(Evento("FALHA_CRITICA", {"erro": f"Nenhum especialista encontrado para a tarefa: {passo}"}, "Manto"))
                break # Interrompe o plano em caso de falha

    def _gerar_plano_tatico(self, missao: str) -> str:
        """Usa o Cérebro para decompor a missão em um plano de passos."""
        prompt = f"Decomponha a seguinte missão em uma lista numerada de passos claros e acionáveis para um sistema de IA multi-agente. Missão: '{missao}'"
        return self.cerebro.gerar_pensamento(prompt)

    def _rotear_tarefa(self, tarefa: str) -> str:
        """Simula o roteamento de uma tarefa para o especialista correto."""
        tarefa_lower = tarefa.lower()
        for nome, especialista in self.tentaculos.items():
            # Simula a chamada `pode_executar`
            if nome.lower() in tarefa_lower:
                return nome
        if "busque" in tarefa_lower or "pesquise" in tarefa_lower: return "Busca"
        if "código" in tarefa_lower or "implemente" in tarefa_lower: return "Codigo"
        return "Estrategista" # Fallback
