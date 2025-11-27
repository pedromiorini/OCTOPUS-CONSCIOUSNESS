# src/shared/comunicacao.py
import asyncio
from typing import Dict, Any, Callable, List
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Evento:
    tipo: str
    dados: Dict[str, Any]
    origem: str
    timestamp: datetime = field(default_factory=datetime.now)

class BarramentoEventos:
    def __init__(self):
        self.assinantes: Dict[str, List[Callable]] = {}

    async def assinar(self, tipo_evento: str, callback: Callable):
        if tipo_evento not in self.assinantes:
            self.assinantes[tipo_evento] = []
        self.assinantes[tipo_evento].append(callback)

    async def publicar(self, evento: Evento):
        if evento.tipo in self.assinantes:
            for callback in self.assinantes[evento.tipo]:
                if asyncio.iscoroutinefunction(callback):
                    await callback(evento)
                else:
                    # Para filas ou callbacks não-assíncronos
                    await callback.put(evento)
