# src/tentaculos/tentaculo_codigo.py
from .base_tentaculo import BaseTentaculo
from typing import Dict
import time

class TentaculoCodigo(BaseTentaculo):
    """Agente especialista em análise e manipulação de código-fonte."""
    def __init__(self, id_tentaculo: int):
        super().__init__(id_tentaculo, "Análise de Código")

    def pode_executar(self, token_missao: Dict) -> bool:
        """Responde a missões que envolvem as palavras 'código' ou 'analisar'."""
        descricao = token_missao.get("descricao", "").lower()
        return "código" in descricao or "analisar" in descricao

    def executar(self, token_missao: Dict) -> str:
        """Simula a execução de uma análise de código."""
        print(f"    ⚡ Tentáculo #{self.id} ativado: Analisando código do framework...")
        time.sleep(2) # Simula tempo de processamento
        return "Análise de código concluída: 3 vulnerabilidades críticas e 10 oportunidades de refatoração foram encontradas."
