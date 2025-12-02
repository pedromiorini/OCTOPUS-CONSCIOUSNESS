# src/tentaculos/tentaculo_wikipediana.py

import logging
import requests # Adicionar 'requests' e 'wikipedia-api' ao requirements.txt
import wikipediaapi
from typing import Dict, Any, List

from .base_tentaculo import BaseTentaculo
from src.cognitive.cerebro import Cerebro
from src.shared.comunicacao import BarramentoEventos

logger = logging.getLogger(__name__)

class TentaculoWikipediana(BaseTentaculo):
    """
    Especialista em conhecimento factual e enciclopédico da Wikipedia.
    Atua como fonte secundária para fatos científicos, históricos e imutáveis.
    """
    def __init__(self, cerebro: Cerebro, barramento: BarramentoEventos):
        super().__init__("Wikipediana", cerebro, barramento)
        # Configura a API da Wikipedia para o idioma português
        self.wiki_api = wikipediaapi.Wikipedia(
            language='pt',
            extract_format=wikipediaapi.ExtractFormat.WIKI
        )
        self.categorias_permitidas = {
            "FATO_CIENTIFICO", "DADO_HISTORICO", "BIOGRAFIA_ESTABELECIDA",
            "CONCEITO_MATEMATICO", "GEOGRAFIA"
        }
        logger.info("📜 Tentáculo Wikipediana (Arquivista Factual) instanciado.")

    async def pode_executar(self, tarefa: str) -> bool:
        # Este tentáculo é geralmente chamado como fallback, mas pode responder a buscas diretas
        palavras_chave = ["wikipedia sobre", "enciclopédia sobre", "fato histórico sobre"]
        return any(palavra in tarefa.lower() for palavra in palavras_chave)

    async def executar_tarefa(self, tarefa: str) -> Dict[str, Any]:
        """Busca e extrai conhecimento factual da Wikipedia."""
        logger.info(f"Wikipediana: Iniciando busca para '{tarefa}'")
        try:
            topico = tarefa.split("sobre")[-1].strip()

            # FASE 1: Filtro de Relevância Temática
            categoria = self._classificar_topico(topico)
            if categoria not in self.categorias_permitidas:
                return {
                    "sucesso": False,
                    "erro": "Tópico fora do escopo",
                    "mensagem": f"O tópico '{topico}' (classificado como {categoria}) não é adequado para busca factual na Wikipedia."
                }
            
            logger.info(f"  -> Tópico '{topico}' classificado como {categoria}. Busca permitida.")

            # FASE 2: Extração via API
            pagina = self.wiki_api.page(topico)
            if not pagina.exists():
                return {"sucesso": False, "erro": "Página não encontrada", "topico": topico}

            # FASE 3: Processamento e Limpeza
            resumo = pagina.summary
            # A extração da Infobox é complexa, aqui simulamos o conceito
            dados_estruturados = {"título": pagina.title, "url": pagina.fullurl}
            
            logger.info(f"  -> Página '{pagina.title}' encontrada e processada.")

            return {
                "sucesso": True,
                "topico": pagina.title,
                "resumo": resumo,
                "dados_estruturados": dados_estruturados,
                "fonte": "Wikipedia"
            }
        except Exception as e:
            logger.error(f"Erro no TentaculoWikipediana: {e}", exc_info=True)
            return {"sucesso": False, "erro": str(e)}

    def _classificar_topico(self, topico: str) -> str:
        """Usa o Cérebro para classificar a natureza do tópico."""
        prompt = (
            f"Classifique o seguinte tópico em uma das categorias: "
            f"[{', '.join(self.categorias_permitidas)}, EVENTO_ATUAL, OPINIAO, TECNOLOGIA_EM_EVOLUCAO].\n"
            f"Tópico: '{topico}'\n"
            "Responda apenas com a categoria."
        )
        return self.cerebro.gerar_pensamento(prompt).strip()

