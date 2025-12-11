# src/tentaculos/tentaculo_promptsmith.py

import logging
import asyncio
from typing import Dict, Any, List

from .base_tentaculo import BaseTentaculo
from src.cognitive.cerebro import Cerebro
from src.shared.comunicacao import BarramentoEventos, Evento
from src.shared.estado_sistema import ModoOperacional # Importando o Enum

logger = logging.getLogger(__name__)

# ... (classes TipoIntencao e outras estruturas de dados) ...

class TentaculoPromptsmith(BaseTentaculo):
    """
    Especialista autodidata na arte de forjar prompts. Otimiza prompts e
    pesquisa ativamente por novas técnicas para se autoaperfeiçoar.
    """
    def __init__(self, cerebro: Cerebro, barramento: BarramentoEventos):
        super().__init__("Promptsmith", cerebro, barramento)
        self.banco_de_exemplos = { ... } # Inalterado
        # Nova base de conhecimento de técnicas
        self.tecnicas_conhecidas = {"FEW_SHOT", "PERSONA_INJECTION"}
        self.fila_resultados_pesquisa = asyncio.Queue()
        logger.info("🛠️ Tentáculo Promptsmith (Autodidata) instanciado.")

    async def iniciar(self):
        """Inicia os loops de escuta e as tarefas de fundo de autoaperfeiçoamento."""
        await self.barramento.assinar("FORJAR_PROMPT", self.fila_tarefas)
        # Assina os resultados das suas próprias missões de pesquisa
        await self.barramento.assinar("TAREFA_CONCLUIDA", self.fila_resultados_pesquisa)
        
        asyncio.create_task(self._loop_escuta_forja())
        # Inicia as tarefas de fundo que respeitarão o modo operacional
        await self.iniciar_tarefas_de_fundo()

    async def iniciar_tarefas_de_fundo(self):
        """Inicia o ciclo de pesquisa de novas técnicas com base no modo operacional."""
        intervalo_s = None
        if self.modo_operacional == ModoOperacional.MAXIMO:
            intervalo_s = 86400  # 1 dia
        elif self.modo_operacional == ModoOperacional.NORMAL:
            intervalo_s = 604800 # 1 semana
        
        if intervalo_s:
            task = asyncio.create_task(self._loop_autoaperfeicoamento(intervalo_s))
            self._tarefas_fundo.append(task)
            logger.info(f"🔬 Ciclo de autoaperfeiçoamento do Promptsmith agendado a cada {intervalo_s / 3600:.0f} horas.")

    async def _loop_autoaperfeicoamento(self, intervalo_s: int):
        """Loop que periodicamente dispara a pesquisa por novas técnicas."""
        while True:
            await asyncio.sleep(intervalo_s)
            logger.info("🔬 Promptsmith iniciando ciclo de pesquisa por novas técnicas de prompt.")
            
            # Delega a pesquisa para outros tentáculos
            tarefa_busca = Evento(
                tipo="TAREFA_DELEGADA",
                dados={"descricao": "Pesquisar por 'advanced prompt engineering techniques 2025'"},
                origem=self.tipo
            )
            tarefa_oraculo = Evento(
                tipo="TAREFA_DELEGADA",
                dados={"descricao": "Consultar IA externa: 'Explique as 3 técnicas de prompt mais eficazes que você conhece.'"},
                origem=self.tipo
            )
            await self.barramento.publicar(tarefa_busca)
            await self.barramento.publicar(tarefa_oraculo)
            
            # Aguarda e processa os resultados
            await self._processar_resultados_pesquisa()

    async def _processar_resultados_pesquisa(self):
        """Aguarda por um tempo e processa os resultados de pesquisa que chegaram."""
        await asyncio.sleep(30) # Espera 30s pelos resultados
        
        textos_coletados = []
        while not self.fila_resultados_pesquisa.empty():
            evento = self.fila_resultados_pesquisa.get_nowait()
            # Garante que está processando um resultado de sua própria pesquisa
            if evento.origem in ["Busca na Web", "Oráculo de IAs"]:
                 textos_coletados.append(evento.dados.get("resultado", ""))
        
        if not textos_coletados:
            logger.info("🔬 Pesquisa não retornou novos materiais para análise.")
            return

        contexto_pesquisa = "\n\n".join(textos_coletados)
        prompt_sintese = (
            "Analise os seguintes textos sobre engenharia de prompt e extraia o nome de uma "
            "técnica promissora que ainda não esteja na lista de técnicas conhecidas. "
            "Responda apenas com o nome da técnica em maiúsculas (ex: CHAIN_OF_THOUGHT).\n\n"
            f"Técnicas Conhecidas: {self.tecnicas_conhecidas}\n\nTextos:\n{contexto_pesquisa}\n\nTécnica Nova:"
        )
        
        nova_tecnica = self.cerebro.gerar_pensamento(prompt_sintese, max_tokens=10)
        
        if nova_tecnica and nova_tecnica not in self.tecnicas_conhecidas:
            self.tecnicas_conhecidas.add(nova_tecnica)
            logger.info(f"✨ Nova técnica de prompt aprendida e adicionada à base de conhecimento: {nova_tecnica}!")
        else:
            logger.info("🔬 Nenhuma técnica nova encontrada na pesquisa atual.")

    # ... (resto do código do Promptsmith: _loop_escuta_forja, forjar_prompt, etc.) ...
    # O método forjar_prompt pode agora ser modificado para usar as self.tecnicas_conhecidas
    # Ex: if "CHAIN_OF_THOUGHT" in self.tecnicas_conhecidas and intencao == TipoIntencao.RACIOCINIO_LOGICO:
    #         partes_prompt.append("Vamos pensar passo a passo.")
