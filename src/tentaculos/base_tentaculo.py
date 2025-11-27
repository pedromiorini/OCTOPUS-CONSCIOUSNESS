# src/tentaculos/base_tentaculo.py
from abc import ABC, abstractmethod
from src.cognitive.cerebro import Cerebro
from src.shared.comunicacao import BarramentoEventos

class BaseTentaculo(ABC):
    """Classe base abstrata para todos os Tentáculos especialistas."""
    def __init__(self, nome: str, cerebro: Cerebro, barramento: BarramentoEventos):
        self.nome = nome
        self.cerebro = cerebro
        self.barramento = barramento

    @abstractmethod
    async def pode_executar(self, tarefa: str) -> bool:
        """Verifica se este tentáculo é qualificado para a tarefa."""
        pass

    @abstractmethod
    async def executar_tarefa(self, tarefa: str, **kwargs) -> dict:
        """Executa a tarefa designada."""
        pass
