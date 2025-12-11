# src/tentaculos/tentaculo_hardware.py

import logging
import asyncio
import psutil
from typing import Dict, Any, List

from .base_tentaculo import BaseTentaculo
from src.cognitive.cerebro import Cerebro
from src.shared.comunicacao import BarramentoEventos, Evento

logger = logging.getLogger(__name__)

# ... (Limiares de Alerta) ...

class TentaculoHardware(BaseTentaculo):
    """
    Especialista em monitoramento e diagnóstico de hardware, agora com
    capacidade de diagnóstico cognitivo para identificar causas de sobrecarga.
    """
    def __init__(self, cerebro: Cerebro, barramento: BarramentoEventos, mapa_processos: Dict[int, Any]):
        super().__init__("Hardware", cerebro, barramento)
        self.sinais_vitais: Dict[str, Any] = {}
        # O mapa de processos é injetado pelo Orquestrador para correlação
        self.mapa_processos = mapa_processos
        logger.info("🩺 Tentáculo de Hardware (v2 com Diagnóstico Cognitivo) instanciado.")

    # ... (pode_executar, iniciar, _loop_monitoramento_sinais_vitais, _avaliar_alertas inalterados) ...

    async def executar_tarefa(self, tarefa: str) -> str:
        """Executa tarefas de diagnóstico ou gera relatórios."""
        if "relatório" in tarefa.lower():
            return self._gerar_relatorio()
        if "diagnostique" in tarefa.lower() and "cpu" in tarefa.lower():
            return await self._diagnostico_cognitivo_cpu()
        
        return "Comando de hardware não reconhecido."

    def _gerar_relatorio(self) -> str:
        # ... (código do relatório inalterado) ...
        pass

    async def _diagnostico_cognitivo_cpu(self) -> str:
        """
        Executa o pipeline de diagnóstico cognitivo para identificar a causa
        de alto uso de CPU.
        """
        logger.info("  -> Iniciando Diagnóstico Cognitivo de CPU...")
        try:
            # 1. Coletar Evidências
            processos_problematicos = self._coletar_processos_problematicos(by='cpu_percent')
            if not processos_problematicos:
                return "Diagnóstico inconclusivo: Nenhum processo com alto consumo de CPU encontrado."

            processo_principal = processos_problematicos[0]

            # 2. Mapear Processo para Tentáculo
            info_tarefa = self.mapa_processos.get(processo_principal['pid'], "Não mapeado para um tentáculo conhecido.")

            # 3. Análise Cognitiva
            prompt = self._criar_prompt_diagnostico(processo_principal, info_tarefa)
            analise = self.cerebro.gerar_pensamento(prompt, max_tokens=250)

            return f"Diagnóstico Cognitivo Concluído:\n{analise}"

        except Exception as e:
            logger.error(f"Erro durante o diagnóstico cognitivo: {e}", exc_info=True)
            return f"Falha no diagnóstico. Erro: {e}"

    def _coletar_processos_problematicos(self, by: str = 'cpu_percent', count: int = 3) -> List[Dict]:
        """Coleta os 'count' principais processos ordenados pelo critério 'by'."""
        processos = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'cmdline']):
            try:
                processos.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        # Ordena os processos pelo critério especificado, em ordem decrescente
        processos_ordenados = sorted(processos, key=lambda p: p[by], reverse=True)
        return processos_ordenados[:count]

    def _criar_prompt_diagnostico(self, processo: Dict, info_tarefa: Any) -> str:
        """Monta o prompt detalhado para a análise do Cérebro."""
        return (
            "Você é um engenheiro de sistemas sênior especialista em depuração de performance. "
            "Analise os dados de diagnóstico a seguir e forneça a Causa Raiz mais provável e uma Ação Recomendada.\n\n"
            "**Alerta:** ALERTA_CPU_ALTA\n\n"
            "**Dados do Processo Problemático:**\n"
            f"- PID: {processo.get('pid')}\n"
            f"- Nome: {processo.get('name')}\n"
            f"- Uso de CPU: {processo.get('cpu_percent'):.1f}%\n"
            f"- Uso de Memória: {processo.get('memory_percent'):.1f}%\n"
            f"- Linha de Comando: {' '.join(processo.get('cmdline', []))}\n\n"
            f"**Mapeamento de Tarefa:**\n{info_tarefa}\n\n"
            "**Análise Diagnóstica (formato JSON com chaves 'causa_raiz' e 'acao_recomendada'):**"
        )
