# OCTOPUS-CONSCIOUSNESS/src/tentaculos/tentaculo_babel.py

import asyncio
import logging
from typing import Dict, Any, Optional, List

from src.cognitive.cerebro import Cerebro
from src.tentaculos.babel.lexico_conceitual import LexicoConceitual
from src.tentaculos.babel.validador_codigo import ValidadorCodigo
from src.tentaculos.babel.otimizador_lexico import OtimizadorLexico
from src.tentaculos.babel.transpilador_octo_latent import TranspiladorOctoLatent
from src.tentaculos.babel.modelos import ResultadoTranspilacao, Conceito, CategoriaConceito

logger = logging.getLogger(__name__)

class TentaculoBabel:
    """
    O Tentáculo Babel é o especialista em linguagem e código.
    Ele gerencia o Léxico Conceitual e transpila intenções de alto nível
    (Octo-Latent) para código funcional.
    """
    def __init__(self, cerebro: Cerebro, habilitado: bool = True):
        self.cerebro = cerebro
        self.habilitado = habilitado
        
        # Componentes internos
        self.lexico = LexicoConceitual(cerebro=self.cerebro, arquivo_lexico="OCTOPUS-CONSCIOUSNESS/src/tentaculos/babel/lexico_conceitual.json")
        self.validador = ValidadorCodigo()
        self.otimizador = OtimizadorLexico(lexico=self.lexico)
        self.transpilador = TranspiladorOctoLatent(lexico=self.lexico, validador=self.validador)
        
        # Adiciona um conceito inicial de exemplo para o léxico
        self._adicionar_conceito_inicial()
        
        logger.info(f"📜 Tentáculo Babel v2.0 inicializado. Habilitado: {self.habilitado}")

    def _adicionar_conceito_inicial(self):
        """Adiciona um conceito de exemplo para inicializar o léxico."""
        conceito_exemplo = Conceito(
            descricao="função de análise de dados",
            implementacao="""
import pandas as pd
def analisar_dados_basico(df: pd.DataFrame) -> dict:
    return {
        "linhas": len(df),
        "colunas": len(df.columns),
        "media_coluna_numerica": df.select_dtypes(include=['number']).mean().to_dict()
    }
""",
            categoria=CategoriaConceito.DADOS
        )
        # O LexicoConceitual já lida com a codificação e salvamento
        self.lexico.adicionar_conceito(conceito_exemplo)

    def liga_desliga(self, estado: bool):
        """Ativa ou desativa o tentáculo."""
        self.habilitado = estado
        logger.info(f"Tentáculo Babel agora está {'habilitado' if estado else 'desabilitado'}.")

    async def transpilhar_intencao(self, intencao_octo_latent: str) -> Optional[ResultadoTranspilacao]:
        """
        Transpila uma intenção de alto nível para código funcional.
        """
        if not self.habilitado:
            logger.warning("Tentáculo Babel desabilitado. Não é possível transpilhar.")
            return None

        return await self.transpilador.transpilhar(intencao_octo_latent)

    def otimizar_lexico(self) -> Dict[str, Any]:
        """
        Executa a rotina de otimização e manutenção do léxico.
        """
        return self.otimizador.analisar_lexico()
