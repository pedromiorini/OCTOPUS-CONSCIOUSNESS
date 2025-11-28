# OCTOPUS-CONSCIOUSNESS/src/mantos/manto_alpha.py

import asyncio
import logging
from typing import Dict, Any, List

from src.cognitive.cerebro import Cerebro
from src.tentaculos.tentaculo_estrategista import TentaculoEstrategista
from src.tentaculos.tentaculo_perceptivo import TentaculoPerceptivo
from src.tentaculos.tentaculo_musa import TentaculoMusa
from src.tentaculos.tentaculo_babel import TentaculoBabel

logger = logging.getLogger(__name__)

class MantoAlpha:
    """
    O Manto Alpha é o coordenador estratégico principal.
    Ele orquestra os tentáculos para atingir objetivos de alto nível.
    """
    def __init__(self, cerebro: Cerebro):
        self.cerebro = cerebro
        self.tentaculos: Dict[str, Any] = {}
        self._inicializar_tentaculos()
        logger.info("👑 Manto Alpha inicializado. Pronta para orquestração.")

    def _inicializar_tentaculos(self):
        """Instancia e registra todos os tentáculos sob o Manto Alpha."""
        self.tentaculos["Estrategista"] = TentaculoEstrategista(cerebro=self.cerebro)
        self.tentaculos["Perceptivo"] = TentaculoPerceptivo(cerebro=self.cerebro)
        self.tentaculos["Musa"] = TentaculoMusa(cerebro=self.cerebro)
        self.tentaculos["Babel"] = TentaculoBabel(cerebro=self.cerebro)
        
        # Adicione outros tentáculos aqui conforme necessário

    def liga_desliga_tentaculo(self, nome_tentaculo: str, estado: bool):
        """Controla o estado de um tentáculo específico."""
        tentaculo = self.tentaculos.get(nome_tentaculo)
        if tentaculo and hasattr(tentaculo, 'liga_desliga'):
            tentaculo.liga_desliga(estado)
            logger.info(f"Tentáculo {nome_tentaculo} controlado para estado: {estado}")
        else:
            logger.warning(f"Tentáculo {nome_tentaculo} não encontrado ou não suporta liga/desliga.")

    async def executar_objetivo(self, objetivo: str, contexto: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa um objetivo de alto nível, gerando um plano e executando-o.
        """
        logger.info(f"Recebido novo objetivo: {objetivo}")
        
        estrategista = self.tentaculos["Estrategista"]
        
        # 1. Planejamento
        plano = await estrategista.planejar_acao(objetivo, contexto)
        
        if not plano:
            return {"sucesso": False, "mensagem": "Falha ao gerar plano de ação."}
            
        # 2. Execução
        resultado_execucao = await estrategista.executar_plano(plano)
        
        # 3. Percepção do Resultado
        perceptivo = self.tentaculos["Perceptivo"]
        estado_final = await perceptivo.inferir_estado_contextual({"log_execucao": resultado_execucao.log_execucao})
        
        return {
            "sucesso": resultado_execucao.sucesso,
            "objetivo": objetivo,
            "plano": plano.dict(),
            "resultado_execucao": resultado_execucao.dict(),
            "estado_final_sistema": estado_final.dict() if estado_final else None
        }

    async def iniciar_monitoramento(self):
        """Inicia tarefas assíncronas de monitoramento (ex: Perceptivo)."""
        perceptivo = self.tentaculos["Perceptivo"]
        # Inicia o monitoramento em background
        asyncio.create_task(perceptivo.monitorar_ambiente(intervalo_segundos=10))
        logger.info("Monitoramento do Perceptivo iniciado em background.")
