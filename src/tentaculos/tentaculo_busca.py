# src/tentaculos/tentaculo_busca.py
from .base_tentaculo import BaseTentaculo
from typing import Dict
import time

class TentaculoBusca(BaseTentaculo):
    """Agente especialista em buscar informações na web."""
    def __init__(self, id_tentaculo: int):
        super().__init__(id_tentaculo, "Busca na Web")

    def pode_executar(self, token_missao: Dict) -> bool:
        """Responde a missões que envolvem a palavra 'pesquisar'."""
        return "pesquisar" in token_missao.get("descricao", "").lower()

    def executar(self, token_missao: Dict) -> str:
        """Simula a execução de uma busca na web."""
        print(f"    ⚡ Tentáculo #{self.id} ativado: Realizando busca na web...")
        time.sleep(1.5) # Simula tempo de processamento
        return "SuperAGI, AutoGPT e LangChain são os frameworks mais citados."
