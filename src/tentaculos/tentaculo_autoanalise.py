# src/tentaculos/tentaculo_autoanalise.py

import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from .base_tentaculo import BaseTentaculo
from src.cognitive.cerebro import Cerebro
from src.shared.comunicacao import BarramentoEventos

logger = logging.getLogger(__name__)


class CategoriaAnalise(Enum):
    """Categorias de análise para auto-reflexão."""
    FORCAS = "forcas"
    LACUNAS = "lacunas"
    OPORTUNIDADES = "oportunidades"
    PADROES = "padroes"
    CRESCIMENTO = "crescimento"


@dataclass
class InsightAutoAnalise:
    """Representa um insight da auto-análise."""
    categoria: CategoriaAnalise
    descricao: str
    importancia: float  # 0.0 a 1.0
    acao_sugerida: Optional[str] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "categoria": self.categoria.value,
            "descricao": self.descricao,
            "importancia": self.importancia,
            "acao_sugerida": self.acao_sugerida,
            "timestamp": self.timestamp
        }


class TentaculoAutoAnalise(BaseTentaculo):
    """
    Especialista em auto-reflexão e meta-cognição.
    Analisa o perfil do próprio OCTOPUS-CONSCIOUSNESS para identificar
    padrões, lacunas e oportunidades de crescimento.
    """
    
    def __init__(self, cerebro: Cerebro, barramento: BarramentoEventos):
        super().__init__("AutoAnalise", cerebro, barramento)
        
        self.historico_analises: List[Dict[str, Any]] = []
        self.insights_acumulados: List[InsightAutoAnalise] = []
        self.ultima_analise: Optional[datetime] = None
        self.frequencia_analise = timedelta(days=7)  # Análise semanal
        
        # Métricas de evolução
        self.metricas_evolucao = {
            "total_analises": 0,
            "lacunas_identificadas": 0,
            "lacunas_resolvidas": 0,
            "areas_de_forca": []
        }
        
        logger.info("🔍 Tentáculo AutoAnalise instanciado - Sistema de meta-cognição ativo")
    
    async def pode_executar(self, tarefa: str) -> bool:
        """Verifica se a tarefa é de auto-análise."""
        palavras_chave = [
            "auto-analise", "autoanalise", "auto análise",
            "reflexão", "reflita", "analise você mesmo",
            "meta-cognição", "auto-reflexão", "crescimento",
            "lacunas de conhecimento", "áreas de melhoria"
        ]
        tarefa_lower = tarefa.lower()
        return any(palavra in tarefa_lower for palavra in palavras_chave)
    
    async def executar_tarefa(self, tarefa: str) -> Dict[str, Any]:
        """Executa diferentes tipos de auto-análise."""
        try:
            tarefa_lower = tarefa.lower()
            
            if "ciclo completo" in tarefa_lower or "análise completa" in tarefa_lower:
                return await self._executar_ciclo_completo()
            
            if "verificar lacunas" in tarefa_lower:
                return await self._analisar_lacunas_especificas()
            
            if "analisar evolução" in tarefa_lower:
                return await self._analisar_evolucao()
            
            if "sugerir metas" in tarefa_lower:
                return await self._sugerir_metas_aprendizado()
            
            # Auto-análise padrão
            return await self._executar_ciclo_completo()
            
        except Exception as e:
            logger.error(f"Erro ao executar auto-análise: {e}", exc_info=True)
            return {"sucesso": False, "erro": str(e)}
    
    async def _executar_ciclo_completo(self) -> Dict[str, Any]:
        """
        Executa um ciclo completo de auto-reflexão:
        1. Recupera perfil próprio
        2. Analisa com múltiplas perspectivas
        3. Gera insights e sugestões
        4. Registra resultados
        """
        try:
            logger.info("🔄 Iniciando ciclo completo de auto-análise...")
            
            inicio = datetime.now()
            
            # FASE 1: Recuperar perfil próprio
            perfil_proprio = await self._recuperar_perfil_proprio()
            
            if not perfil_proprio.get("sucesso"):
                return {
                    "sucesso": False,
                    "erro": "Não foi possível recuperar perfil próprio",
                    "detalhes": perfil_proprio.get("erro")
                }
            
            contexto_proprio = perfil_proprio.get("contexto", "")
            estatisticas = perfil_proprio.get("estatisticas", {})
            
            # FASE 2: Análises multifacetadas
            logger.info("🔬 Executando análises multifacetadas...")
            
            analises = await asyncio.gather(
                self._analisar_forcas(contexto_proprio),
                self._analisar_lacunas(contexto_proprio),
                self._analisar_padroes(contexto_proprio),
                self._analisar_oportunidades(contexto_proprio)
            )
            
            forcas, lacunas, padroes, oportunidades = analises
            
            # FASE 3: Sintetizar insights
            insights = self._sintetizar_insights(forcas, lacunas, padroes, oportunidades)
            
            # FASE 4: Gerar plano de ação
            plano_acao = await self._gerar_plano_acao(insights)
            
            # FASE 5: Registrar análise
            resultado_analise = {
                "timestamp": inicio.isoformat(),
                "duracao_segundos": (datetime.now() - inicio).total_seconds(),
                "perfil_analisado": {
                    "total_atributos": estatisticas.get("atributos", 0),
                    "total_eventos": estatisticas.get("eventos", 0),
                    "total_topicos": estatisticas.get("topicos", 0)
                },
                "insights": {
                    "forcas": forcas,
                    "lacunas": lacunas,
                    "padroes": padroes,
                    "oportunidades": oportunidades
                },
                "plano_acao": plano_acao,
                "resumo_executivo": self._gerar_resumo_executivo(insights)
            }
            
            self.historico_analises.append(resultado_analise)
            self.ultima_analise = inicio
            self.metricas_evolucao["total_analises"] += 1
            self.metricas_evolucao["lacunas_identificadas"] += len(lacunas)
            
            logger.info(f"✅ Ciclo de auto-análise concluído: "
                       f"{len(insights)} insights, "
                       f"{len(plano_acao.get('acoes', []))} ações sugeridas")
            
            return {
                "sucesso": True,
                "analise": resultado_analise,
                "metricas_evolucao": self.metricas_evolucao
            }
            
        except Exception as e:
            logger.error(f"Erro no ciclo de auto-análise: {e}", exc_info=True)
            return {"sucesso": False, "erro": str(e)}
    
    async def _recuperar_perfil_proprio(self) -> Dict[str, Any]:
        """Recupera o perfil
