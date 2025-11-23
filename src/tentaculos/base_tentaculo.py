# src/tentaculos/base_tentaculo.py
from abc import ABC, abstractmethod
import random
import time
from typing import Dict

class BaseTentaculo(ABC):
    """
    Classe base abstrata para todos os agentes especialistas (Tentáculos).
    Cada tentáculo é um "ninja" focado em sua missão.
    """
    def __init__(self, id_tentaculo: int, especialidade: str):
        self.id = id_tentaculo
        self.especialidade = especialidade
        # Em uma implementação real, cada tentáculo carregaria seu próprio
        # modelo de linguagem especializado aqui.
        print(f"    - Tentáculo #{self.id} (Especialidade: {self.especialidade}) inicializado e em modo de escuta.")

    @abstractmethod
    def pode_executar(self, token_missao: Dict) -> bool:
        """
        Avalia se a missão recebida é compatível com sua especialidade.
        Retorna True se puder executar, False caso contrário.
        """
        pass

    def gerar_proposta(self, token_missao: Dict) -> Dict:
        """
        Gera uma proposta de prontidão para o Manto, incluindo uma
        estimativa de confiança no sucesso da missão.
        """
        # A confiança pode ser calculada com base na complexidade da tarefa
        # e na especialização do modelo do tentáculo.
        confianca_base = 0.9
        return {
            "id_tentaculo": self.id,
            "habilidade": self.especialidade,
            "custo_estimado": random.uniform(1, 5), # Simula custo em recursos
            "confianca": confianca_base + random.uniform(-0.1, 0.09)
        }

    @abstractmethod
    def executar(self, token_missao: Dict) -> str:
        """
        Executa a missão designada e retorna o resultado como uma string.
        """
        pass
