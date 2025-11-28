# OCTOPUS-CONSCIOUSNESS/src/tentaculos/estrategista/modelos.py

from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class StatusPasso(str, Enum):
    PENDENTE = "pendente"
    EM_EXECUCAO = "em_execucao"
    CONCLUIDO = "concluido"
    FALHOU = "falhou"
    CANCELADO = "cancelado"

class Passo(BaseModel):
    """Representa uma única ação ou sub-tarefa no plano."""
    id: int = Field(..., description="Identificador único do passo.")
    descricao: str = Field(..., min_length=10, description="Descrição detalhada do que deve ser feito.")
    tentaculo_responsavel: str = Field(..., description="Nome do tentáculo responsável pela execução (e.g., 'Babel', 'Musa').")
    status: StatusPasso = Field(default=StatusPasso.PENDENTE, description="Status atual do passo.")
    resultado: Optional[str] = Field(default=None, description="Resultado da execução do passo.")
    dependencias: List[int] = Field(default_factory=list, description="IDs dos passos que devem ser concluídos antes deste.")
    tempo_estimado_segundos: int = Field(default=60, ge=1, description="Tempo estimado para conclusão.")

class PlanoDeAcao(BaseModel):
    """O plano de ação completo gerado pelo Estrategista."""
    id_plano: str = Field(..., description="ID único do plano.")
    objetivo: str = Field(..., description="O objetivo principal do plano.")
    passos: List[Passo] = Field(default_factory=list, description="Lista ordenada de passos a serem executados.")
    criado_em: datetime = Field(default_factory=datetime.now)
    mantos_envolvidos: List[str] = Field(default_factory=list)

class MetricasEstrategista(BaseModel):
    """Métricas de desempenho do tentáculo Estrategista."""
    planos_gerados: int = 0
    planos_executados: int = 0
    taxa_sucesso_plano: float = 0.0
    tempo_medio_planejamento_segundos: float = 0.0
    passos_concluidos: int = 0
    passos_falhados: int = 0

class ResultadoEstrategia(BaseModel):
    """Resultado final de uma execução de estratégia."""
    sucesso: bool
    plano_executado: PlanoDeAcao
    log_execucao: List[str]
    metricas: MetricasEstrategista
    tempo_total_segundos: float
