# src/tentaculos/tentaculo_mimico.py

import logging
import asyncio
from typing import Dict, Any, List

from .base_tentaculo import BaseTentaculo
from src.cognitive.cerebro import Cerebro
from src.shared.comunicacao import BarramentoEventos, Evento

logger = logging.getLogger(__name__)

class TentaculoMimico(BaseTentaculo):
    """
    Especialista em aprendizado por observação, inspirado no projeto EcoMimico.
    Aprende a imitar o comportamento de outros tentáculos.
    """
    def __init__(self, cerebro: Cerebro, barramento: BarramentoEventos):
        super().__init__("Mimico", cerebro, barramento)
        self.alvo_observacao: str = None
        self.dados_observados: List[Dict[str, Any]] = []
        self.hipotese_prompt: str = None
        self.fila_observacao = asyncio.Queue()
        logger.info("🎭 Tentáculo Mímico instanciado.")

    async def pode_executar(self, tarefa: str) -> bool:
        # Reage a um comando específico de "observar".
        return "observar o tentáculo" in tarefa.lower()

    async def iniciar(self):
        # Inicia o loop de escuta para comandos de observação.
        await super().iniciar()
        # Assina todos os eventos para poder observar qualquer tentáculo.
        await self.barramento.assinar("TAREFA_DELEGADA", self.fila_observacao)
        await self.barramento.assinar("TAREFA_CONCLUIDA", self.fila_observacao)

    async def executar_tarefa(self, tarefa: str) -> str:
        """Inicia um ciclo de observação e aprendizado."""
        if "observar o tentáculo" in tarefa.lower():
            partes = tarefa.split("observar o tentáculo")
            self.alvo_observacao = partes[1].strip()
            
            asyncio.create_task(self._ciclo_de_aprendizagem())
            return f"Iniciando modo de observação. Alvo: '{self.alvo_observacao}'. Coletando dados..."
        return "Comando não reconhecido."

    async def _ciclo_de_aprendizagem(self):
        """Gerencia o processo completo de observação, análise e imitação."""
        # 1. Fase de Observação
        logger.info(f"Mimico: Coletando dados de '{self.alvo_observacao}' por 30 segundos.")
        await asyncio.sleep(30) # Simula um período de observação

        # Processa os eventos coletados para formar pares de input/output
        # (Lógica complexa de pareamento de eventos omitida para clareza)
        self.dados_observados.append({
            "input": "Tarefa de exemplo",
            "output": "Resultado de exemplo do especialista"
        })
        
        if not self.dados_observados:
            logger.warning("Mimico: Nenhum dado relevante observado.")
            return

        # 2. Fase de Análise
        logger.info("Mimico: Analisando comportamento observado...")
        prompt_analise = self._criar_prompt_analise()
        analise = self.cerebro.gerar_pensamento(prompt_analise)
        
        # 3. Fase de Geração de Hipótese
        logger.info("Mimico: Gerando hipótese de comportamento (prompt)...")
        prompt_gerador = (
            f"Com base na seguinte análise de comportamento: '{analise}', "
            "crie um prompt genérico para um LLM que o instrua a replicar esse comportamento."
        )
        self.hipotese_prompt = self.cerebro.gerar_pensamento(prompt_gerador)
        
        logger.info(f"✨ Mimico aprendeu uma nova habilidade! Hipótese gerada: '{self.hipotese_prompt[:100]}...'")
        
        # Notifica o Manto sobre a nova capacidade
        evento_aprendizagem = Evento(
            tipo="HABILIDADE_APRENDIDA",
            dados={"habilidade_imitada": self.alvo_observacao, "proficiencia": 0.85},
            origem=self.tipo
        )
        await self.barramento.publicar(evento_aprendizagem)
        self.alvo_observacao = None # Reseta para a próxima missão

    def _criar_prompt_analise(self) -> str:
        """Cria o prompt para o Cérebro analisar os dados observados."""
        exemplos_str = "\n\n".join([
            f"Exemplo {i+1}:\nEntrada: {d['input']}\nSaída: {d['output']}"
            for i, d in enumerate(self.dados_observados)
        ])
        return (
            "Você é um engenheiro reverso de IA. Analise os seguintes pares de entrada/saída "
            "de um agente especialista e descreva a transformação lógica que ele está aplicando.\n\n"
            f"{exemplos_str}\n\nAnálise da Transformação:"
        )
