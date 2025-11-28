# OCTOPUS-CONSCIOUSNESS/src/mantos/manto_beta.py

import asyncio
import logging
from typing import Dict, Any, List

from src.cognitive.cerebro import Cerebro
from src.tentaculos.tentaculo_musa import TentaculoMusa
from src.tentaculos.tentaculo_babel import TentaculoBabel

logger = logging.getLogger(__name__)

class MantoBeta:
    """
    O Manto Beta é o coordenador de suporte, focado em tarefas criativas e de transcodificação.
    Ele orquestra os tentáculos Musa e Babel.
    """
    def __init__(self, cerebro: Cerebro):
        self.cerebro = cerebro
        self.tentaculos: Dict[str, Any] = {}
        self._inicializar_tentaculos()
        logger.info("👑 Manto Beta inicializado. Focado em criatividade e transcodificação.")

    def _inicializar_tentaculos(self):
        """Instancia e registra os tentáculos sob o Manto Beta (compartilhados com Alpha)."""
        # Assume que os tentáculos são instâncias singleton ou gerenciadas centralmente
        # Para esta simulação, vamos instanciar novos (o que não é ideal em um sistema real)
        # Em um sistema real, os Mantos se comunicariam com instâncias singleton.
        self.tentaculos["Musa"] = TentaculoMusa(cerebro=self.cerebro)
        self.tentaculos["Babel"] = TentaculoBabel(cerebro=self.cerebro)
        
    def liga_desliga_tentaculo(self, nome_tentaculo: str, estado: bool):
        """Controla o estado de um tentáculo específico."""
        tentaculo = self.tentaculos.get(nome_tentaculo)
        if tentaculo and hasattr(tentaculo, 'liga_desliga'):
            tentaculo.liga_desliga(estado)
            logger.info(f"Tentáculo {nome_tentaculo} controlado para estado: {estado}")
        else:
            logger.warning(f"Tentáculo {nome_tentaculo} não encontrado ou não suporta liga/desliga.")

    async def gerar_conceito_criativo(self, tema: str) -> Dict[str, Any]:
        """
        Inicia um ciclo criativo completo usando o Tentáculo Musa.
        """
        logger.info(f"Iniciando geração de conceito criativo para: {tema}")
        musa = self.tentaculos["Musa"]
        dossie = await musa.ciclo_criativo(tema)
        
        if dossie:
            return {"sucesso": True, "dossie_conceito": dossie.dict()}
        else:
            return {"sucesso": False, "mensagem": "Falha na geração do conceito criativo."}

    async def transpilhar_e_validar(self, intencao_octo_latent: str) -> Dict[str, Any]:
        """
        Transpila uma intenção e valida o código gerado usando o Tentáculo Babel.
        """
        logger.info(f"Iniciando transpilação para: {intencao_octo_latent[:30]}...")
        babel = self.tentaculos["Babel"]
        resultado = await babel.transpilhar_intencao(intencao_octo_latent)
        
        if resultado:
            return {"sucesso": resultado.sucesso, "resultado_transpilacao": resultado.dict()}
        else:
            return {"sucesso": False, "mensagem": "Falha na transpilação (Babel desabilitado ou erro interno)."}
