# OCTOPUS-CONSCIOUSNESS/src/tentaculos/tentaculo_perceptivo.py

import asyncio
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

from src.cognitive.cerebro import Cerebro # Assumindo que o Cerebro é o modelo de IA

logger = logging.getLogger(__name__)

class EstadoContextual(BaseModel):
    """Modelo de dados para o estado contextual percebido."""
    timestamp: datetime = Field(default_factory=datetime.now)
    estado_fisico: Dict[str, Any] = Field(default_factory=dict, description="Dados de sensores, ambiente, recursos.")
    estado_emocional: Dict[str, Any] = Field(default_factory=dict, description="Sentimentos, humor, nível de estresse do sistema.")
    estado_cognitivo: Dict[str, Any] = Field(default_factory=dict, description="Carga de trabalho, complexidade da tarefa, taxa de erro.")
    estado_social: Dict[str, Any] = Field(default_factory=dict, description="Interações com o usuário, outros tentáculos, APIs externas.")
    resumo_executivo: str = Field(..., description="Resumo conciso do estado atual.")

class TentaculoPerceptivo:
    """
    O Tentáculo Perceptivo é responsável por coletar, processar e inferir
    o estado contextual multidimensional do sistema e do ambiente.
    """
    def __init__(self, cerebro: Cerebro, habilitado: bool = True):
        self.cerebro = cerebro
        self.habilitado = habilitado
        logger.info(f"👁️ Tentáculo Perceptivo v2.0 inicializado. Habilitado: {self.habilitado}")

    def liga_desliga(self, estado: bool):
        """Ativa ou desativa o tentáculo."""
        self.habilitado = estado
        logger.info(f"Tentáculo Perceptivo agora está {'habilitado' if estado else 'desabilitado'}.")

    async def inferir_estado_contextual(self, dados_brutos: Dict[str, Any]) -> Optional[EstadoContextual]:
        """
        Processa dados brutos e infere o estado contextual multidimensional.
        """
        if not self.habilitado:
            logger.warning("Tentáculo Perceptivo desabilitado. Não é possível inferir o estado.")
            return None

        logger.info("Iniciando inferência de estado contextual...")
        
        # Simulação de processamento de dados e inferência
        await asyncio.sleep(0.5) 

        # 1. Processamento de Dados Brutos (Simulação)
        estado_fisico = {
            "uso_cpu": dados_brutos.get("cpu", 0.1),
            "uso_memoria": dados_brutos.get("memoria", 0.3),
            "latencia_rede": dados_brutos.get("latencia", 50)
        }
        
        estado_emocional = {
            "nivel_estresse": "Baixo" if estado_fisico["uso_cpu"] < 0.5 else "Médio",
            "humor_sistema": "Estável"
        }
        
        estado_cognitivo = {
            "tarefas_pendentes": dados_brutos.get("tarefas_pendentes", 2),
            "complexidade_media": dados_brutos.get("complexidade_media", 0.6),
            "erros_recente": dados_brutos.get("erros_recente", 0)
        }
        
        estado_social = {
            "interacoes_usuario": dados_brutos.get("interacoes_usuario", 5),
            "tentaculos_ativos": dados_brutos.get("tentaculos_ativos", 4)
        }
        
        # 2. Geração do Resumo Executivo (Simulação de chamada ao modelo de IA)
        resumo = f"O sistema está estável. Uso de CPU em {estado_fisico['uso_cpu'] * 100:.0f}%. Há {estado_cognitivo['tarefas_pendentes']} tarefas pendentes. O nível de estresse é {estado_emocional['nivel_estresse']}."
        
        estado = EstadoContextual(
            estado_fisico=estado_fisico,
            estado_emocional=estado_emocional,
            estado_cognitivo=estado_cognitivo,
            estado_social=estado_social,
            resumo_executivo=resumo
        )
        
        logger.info("Inferência de estado contextual concluída.")
        return estado

    async def monitorar_ambiente(self, intervalo_segundos: int = 5):
        """
        Loop de monitoramento contínuo (simulado).
        """
        logger.info(f"Iniciando monitoramento a cada {intervalo_segundos} segundos...")
        while self.habilitado:
            # Simulação de coleta de dados brutos
            dados_brutos = {
                "cpu": 0.1 + (datetime.now().second % 10) / 100,
                "memoria": 0.3,
                "latencia": 50,
                "tarefas_pendentes": 2,
                "complexidade_media": 0.6,
                "erros_recente": 0,
                "interacoes_usuario": 5,
                "tentaculos_ativos": 4
            }
            
            estado = await self.inferir_estado_contextual(dados_brutos)
            if estado:
                logger.debug(f"Estado atual: {estado.resumo_executivo}")
                # Aqui o estado seria enviado para o Manto para orquestração
            
            await asyncio.sleep(intervalo_segundos)
