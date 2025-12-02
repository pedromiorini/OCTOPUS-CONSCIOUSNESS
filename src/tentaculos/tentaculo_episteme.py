# src/tentaculos/tentaculo_episteme.py

import logging
import json
from typing import Dict, Any, List
from enum import Enum

from .base_tentaculo import BaseTentaculo
from src.cognitive.cerebro import Cerebro
from src.shared.comunicacao import BarramentoEventos, Evento

logger = logging.getLogger(__name__)

class VereditoEpistemologico(Enum):
    VALIDADO_E_RELEVANTE = "VALIDADO_E_RELEVANTE"
    VALIDO_MAS_INCREMENTAL = "VÁLIDO, MAS INCREMENTAL"
    CONTROVERSO = "CONTROVERSO"
    NAO_VERIFICAVEL_HYPE = "NÃO VERIFICÁVEL / HYPE"
    ALERTA_DE_DESINFORMACAO = "ALERTA_DE_DESINFORMACAO"

class TentaculoEpisteme(BaseTentaculo):
    """
    Especialista em validar criticamente o conhecimento científico.
    Atua como um revisor por pares interno, protegendo o sistema
    contra desinformação, hype e armadilhas.
    """
    def __init__(self, cerebro: Cerebro, barramento: BarramentoEventos, tentaculos: Dict[str, BaseTentaculo]):
        super().__init__("Episteme", cerebro, barramento)
        self.tentaculos = tentaculos
        logger.info("🛡️ Tentáculo Episteme (Guardião da Verdade Científica) instanciado.")

    async def pode_executar(self, tarefa: str) -> bool:
        """Verifica se a tarefa é de validação de conhecimento."""
        palavras_chave = ["valide o dossiê", "análise crítica de", "verifique a credibilidade"]
        return any(palavra in tarefa.lower() for palavra in palavras_chave)

    async def executar_tarefa(self, tarefa: str, **kwargs) -> Dict[str, Any]:
        """
        Executa o pipeline de validação epistemológica.
        
        Args:
            tarefa: "Valide o dossiê do artigo [ID]"
            **kwargs:
                - dossie: O objeto DossieInteligenciaBruta a ser validado.
        """
        dossie = kwargs.get("dossie")
        if not dossie:
            return {"sucesso": False, "erro": "Dossiê do artigo não fornecido."}

        id_arxiv = dossie.get("id_arxiv")
        await self._publicar_raciocinio(f"Iniciando validação epistemológica para o artigo '{id_arxiv}'.")

        try:
            # FASE 1: Análise de Credibilidade da Fonte
            score_credibilidade, analise_fonte = await self._analisar_credibilidade_fonte(dossie["autores"])

            # FASE 2: Verificação Cruzada de Citações (simulado)
            score_verificacao, analise_verificacao = await self._verificar_citacoes(dossie)

            # FASE 3: Detecção de Hype e Anomalias
            score_hype, analise_hype = await self._detectar_hype_e_anomalias(dossie)

            # FASE 4: Síntese do Veredito
            veredito_final, score_final = self._sintetizar_veredito(
                score_credibilidade, score_verificacao, score_hype
            )

            relatorio_final = {
                "id_arxiv": id_arxiv,
                "titulo": dossie["titulo"],
                "veredito": veredito_final.value,
                "score_confianca_final": score_final,
                "analises": {
                    "credibilidade_fonte": {"score": score_credibilidade, "analise": analise_fonte},
                    "verificacao_cruzada": {"score": score_verificacao, "analise": analise_verificacao},
                    "deteccao_hype": {"score": score_hype, "analise": analise_hype},
                }
            }
            
            await self._publicar_raciocinio(f"Validação concluída. Veredito para '{id_arxiv}': {veredito_final.value}.")
            return {"sucesso": True, "relatorio_validacao": relatorio_final}

        except Exception as e:
            logger.error(f"Erro no TentaculoEpisteme: {e}", exc_info=True)
            return {"sucesso": False, "erro": str(e)}

    async def _analisar_credibilidade_fonte(self, autores: List[str]) -> (float, str):
        """Avalia a reputação dos autores e suas afiliações."""
        await self._publicar_raciocinio(f"Verificando credibilidade dos autores: {', '.join(autores)}.")
        
        # Delega ao TentaculoBusca para pesquisar os autores
        # Em uma implementação real, faria buscas mais detalhadas no Google Scholar, etc.
        busca_autor = await self.tentaculos["Busca"].executar_tarefa(f"perfil acadêmico de {autores[0]}")
        
        # Simulação de análise
        if "nenhum resultado" in busca_autor.get("resumo", "").lower():
            return 0.2, "Autores com pouca ou nenhuma presença acadêmica online. Afiliações desconhecidas."
        else:
            return 0.8, "Autores com histórico de publicações em conferências e jornais relevantes."

    async def _verificar_citacoes(self, dossie: Dict[str, Any]) -> (float, str):
        """Verifica as principais alegações contra o conhecimento estabelecido."""
        await self._publicar_raciocinio("Verificando alegações e citações cruzadas.")
        # Simulação: Delega ao Wikipediana para buscar o conceito principal
        conceito_chave = dossie["metodologia_proposta"]
        resultado_wiki = await self.tentaculos["Wikipediana"].executar_tarefa(f"wikipedia sobre {conceito_chave}")
        
        if resultado_wiki.get("sucesso"):
            return 0.7, f"O conceito de '{conceito_chave}' é bem estabelecido. As alegações parecem ser uma extensão incremental."
        else:
            return 0.4, f"O conceito de '{conceito_chave}' é novo e não possui uma página de referência, indicando alto grau de novidade ou falta de validação pela comunidade."

    async def _detectar_hype_e_anomalias(self, dossie: Dict[str, Any]) -> (float, str):
        """Usa o Cérebro para análise crítica do texto."""
        await self._publicar_raciocinio("Analisando o texto em busca de sinais de hype ou anomalias.")
        
        prompt = (
            "Analise criticamente o seguinte resumo de um artigo científico. "
            "Procure por linguagem excessivamente promocional, falta de discussão sobre limitações, "
            "e resultados que parecem bons demais para ser verdade. "
            "Forneça uma análise curta e um score de 'hype' de 0 (sóbrio) a 1 (puro marketing).\n\n"
            f"Título: {dossie['titulo']}\n"
            f"Resultados Reivindicados: {dossie['resultados_reivindicados']}\n"
            f"Limitações Admitidas: {dossie['limitacoes_admitidas']}\n\n"
            "Responda em JSON com chaves 'analise' e 'score_hype'."
        )
        
        resposta = self.cerebro.gerar_pensamento(prompt)
        analise_json = json.loads(resposta)
        
        score_hype = analise_json.get("score_hype", 0.5)
        analise_texto = analise_json.get("analise")
        
        # O score de confiança é o inverso do score de hype
        return 1.0 - score_hype, analise_texto

    def _sintetizar_veredito(self, score_credibilidade: float, score_verificacao: float, score_hype: float) -> (VereditoEpistemologico, float):
        """Combina os scores para gerar um veredito e uma confiança final."""
        score_final = (score_credibilidade * 0.4) + (score_verificacao * 0.4) + (score_hype * 0.2)

        if score_final > 0.8:
            return VereditoEpistemologico.VALIDADO_E_RELEVANTE, score_final
        elif score_final > 0.6:
            return VereditoEpistemologico.VALIDO_MAS_INCREMENTAL, score_final
        elif score_final > 0.4:
            return VereditoEpistemologico.CONTROVERSO, score_final
        elif score_final > 0.2:
            return VereditoEpistemologico.NAO_VERIFICAVEL_HYPE, score_final
        else:
            return VereditoEpistemologico.ALERTA_DE_DESINFORMACAO, score_final

    async def _publicar_raciocinio(self, pensamento: str):
        await self.barramento.publicar(Evento("EVENTO_RACIOCINIO", {"pensamento": f"🛡️ Episteme: {pensamento}"}, self.nome))
