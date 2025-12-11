# src/tentaculos/tentaculo_antialucinacao.py

import logging
import asyncio
from enum import Enum, auto
from typing import Dict, Any

from .base_tentaculo import BaseTentaculo
from src.cognitive.cerebro import Cerebro
from src.shared.comunicacao import BarramentoEventos, Evento

logger = logging.getLogger(__name__)

class NivelIrregularidade(Enum):
    CONFIRMADO = auto()
    ERRO_BENIGNO = auto()
    FABRICACAO_BAIXO_RISCO = auto()
    IRREGULARIDADE_GRAVE = auto()
    ALERTA_SEGURANCA = auto()

class TentaculoAntialucinacao(BaseTentaculo):
    """
    O Guardião da Realidade. Um especialista em detectar, classificar e mitigar
    irregularidades factuais nas informações processadas pelo sistema.
    """
    def __init__(self, cerebro: Cerebro, barramento: BarramentoEventos):
        super().__init__("Antialucinação", cerebro, barramento)
        logger.info("🛡️ Tentáculo Antialucinação instanciado e conectado.")

    async def pode_executar(self, tarefa: str) -> bool:
        # Este tentáculo é reativo a um tipo de evento específico, não a palavras-chave.
        # A lógica de ativação estará no seu loop de escuta.
        return False # Não será ativado por delegação padrão.

    async def iniciar(self):
        """Sobrescreve o método base para assinar um evento específico."""
        await self.barramento.assinar("VERIFICAR_INFORMACAO", self.fila_tarefas)
        asyncio.create_task(self._loop_escuta_verificacao())

    async def _loop_escuta_verificacao(self):
        """Loop de vida que escuta por missões de verificação."""
        while True:
            evento = await self.fila_tarefas.get()
            logger.info(f"🛡️ Antialucinação: Recebida missão de verificação de '{evento.origem}'.")
            
            texto_para_verificar = evento.dados.get("texto")
            contexto = evento.dados.get("contexto", "geral")
            
            veredicto = await self.executar_verificacao(texto_para_verificar, contexto)
            
            evento_resultado = Evento(
                tipo="VERIFICACAO_CONCLUIDA",
                dados={"veredicto": veredicto},
                origem=self.tipo
            )
            await self.barramento.publicar(evento_resultado)
            self.fila_tarefas.task_done()

    async def executar_verificacao(self, texto: str, contexto: str) -> Dict[str, Any]:
        """
        Executa o pipeline completo de verificação de fatos.
        """
        if not texto:
            return {"nivel": NivelIrregularidade.ERRO_BENIGNO.name, "detalhes": "Texto de entrada vazio."}

        # 1. Extrair afirmações (simulação)
        afirmacoes = await self._extrair_afirmacoes(texto)
        if not afirmacoes:
            return {"nivel": NivelIrregularidade.CONFIRMADO.name, "detalhes": "Nenhuma afirmação factual encontrada para verificar."}

        # 2. Verificação Cruzada (simulação)
        # Em uma implementação real, isso publicaria eventos para Busca e Oraculo
        logger.info(f"  -> Verificando {len(afirmacoes)} afirmações...")
        await asyncio.sleep(1) # Simula o tempo de consulta
        evidencias = "Evidências simuladas confirmam a maioria das afirmações, mas apontam uma inconsistência."

        # 3. Calibrar Incerteza (simulação)
        score_confianca = await self._calibrar_incerteza(afirmacoes, evidencias)

        # 4. Análise de Risco de Domínio (simulação)
        fator_risco = 1.5 if contexto in ["medico", "legal"] else 1.0
        score_confianca_ajustado = score_confianca / fator_risco

        # 5. Gerar Veredito
        if score_confianca_ajustado > 0.8:
            nivel = NivelIrregularidade.CONFIRMADO
        elif score_confianca_ajustado > 0.5:
            nivel = NivelIrregularidade.ERRO_BENIGNO
        else:
            nivel = NivelIrregularidade.IRREGULARIDADE_GRAVE
        
        logger.info(f"  -> Veredito: {nivel.name} (Confiança: {score_confianca_ajustado:.2f})")
        return {"nivel": nivel.name, "confianca": score_confianca_ajustado, "detalhes": evidencias}

    async def _extrair_afirmacoes(self, texto: str) -> List[str]:
        """Usa o cérebro para isolar as afirmações factuais de um texto."""
        prompt = (
            f"Analise o texto a seguir e extraia uma lista de afirmações factuais verificáveis. "
            f"Ignore opiniões e linguagem subjetiva.\n\nTexto: '{texto}'\n\nAfirmações (lista numerada):"
        )
        resposta = self.cerebro.gerar_pensamento(prompt, max_tokens=256)
        return [linha.strip() for linha in resposta.split('\n') if linha.strip()]

    async def _calibrar_incerteza(self, afirmacoes: List[str], evidencias: str) -> float:
        """Usa o cérebro para gerar um score de confiança com base nas evidências."""
        prompt = (
            f"Dadas as afirmações originais e as evidências coletadas, avalie a confiança geral "
            f"das afirmações em uma escala de 0.0 (totalmente falso) a 1.0 (totalmente confirmado).\n\n"
            f"Afirmações: {afirmacoes}\nEvidências: {evidencias}\n\nScore de Confiança (apenas o número):"
        )
        resposta = self.cerebro.gerar_pensamento(prompt, max_tokens=10)
        try:
            return float(resposta)
        except ValueError:
            return 0.5 # Retorna um valor neutro em caso de falha na conversão
