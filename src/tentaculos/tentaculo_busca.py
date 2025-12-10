# src/tentaculos/tentaculo_busca.py

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional

from duckduckgo_search import DDGS

# Importando os componentes da nova arquitetura
from .base_tentaculo import BaseTentaculo
from src.shared.estado_sistema import StatusTentaculo

# Configuração do logger para este módulo específico
logger = logging.getLogger(__name__)

class ResultadoBusca:
    """Estrutura de dados para um resultado de busca. Usa __slots__ para eficiência."""
    __slots__ = ("titulo", "url", "snippet")

    def __init__(self, titulo: str, url: str, snippet: str):
        self.titulo: str = titulo
        self.url: str = url
        self.snippet: str = snippet

class TentaculoBusca(BaseTentaculo):
    """
    Tentáculo especialista em busca na web, adaptado para a arquitetura bicefálica assíncrona.
    """
    PALAVRAS_CHAVE = {"pesquisar", "buscar", "procurar", "encontrar", "o que é", "quem foi"}
    PALAVRAS_REMOVER = {"pesquisar", "buscar", "procurar", "encontrar", "informações sobre", "sobre", "por"}

    def __init__(self, id_tentaculo: int, max_resultados: int = 3):
        super().__init__(id_tentaculo, "Busca na Web")
        self.search_engine = DDGS()
        self.max_resultados = max_resultados
        self.cache_buscas: Dict[str, List[ResultadoBusca]] = {}

    def _extrair_query(self, descricao_missao: str) -> str:
        """Extrai e limpa o termo de busca da descrição da missão."""
        query = descricao_missao.lower()
        for palavra in self.PALAVRAS_REMOVER:
            query = query.replace(palavra, "")
        return query.strip()

    async def gerar_proposta(self, token_missao: Dict) -> Optional[Dict[str, Any]]:
        """
        Analisa a missão e, se for relevante, gera uma proposta de execução.
        Este é o passo cognitivo do tentáculo.
        """
        descricao = token_missao.get("descricao", "").lower()
        
        # 1. Autoavaliação: A missão pertence à minha especialidade?
        if not any(palavra in descricao for palavra in self.PALAVRAS_CHAVE):
            return None  # Não é uma missão para mim

        # 2. Análise da Missão: Qual é a tarefa real?
        query = self._extrair_query(descricao)
        if not query:
            return None # Missão de busca, mas sem um termo válido

        # 3. Geração da Proposta: Construir a proposta para o Manto
        proposta = {
            "id_tentaculo": self.id,
            "tipo": self.tipo,
            "confianca": 0.9,  # Simulação da confiança do modelo especialista
            "plano_de_acao_interno": f"Extrair query '{query}', buscar com DDGS, formatar {self.max_resultados} resultados.",
            "custo_estimado": 1, # Custo simbólico
            "query_extraida": query # Informação útil para o Manto
        }
        logger.info(f"🐙 Tentáculo #{self.id} gerou proposta para a missão: '{descricao}'")
        return proposta

    async def executar(self, token_missao: Dict) -> str:
        """
        Executa a busca de forma assíncrona, com cache e tratamento de erros.
        """
        self.status = StatusTentaculo.OCUPADO
        query = self._extrair_query(token_missao.get("descricao", ""))

        logger.info(f"⚡ Tentáculo #{self.id} ativado. Executando busca por: '{query}'")

        # 1. Verificar cache
        if query in self.cache_buscas:
            logger.info(f"💾 Resultado para '{query}' encontrado no cache.")
            self.status = StatusTentaculo.ATIVO
            return self._formatar_resultados(self.cache_buscas[query])

        # 2. Realizar busca assíncrona
        logger.info(f"🌐 Realizando busca na web para '{query}'...")
        inicio = time.time()
        
        try:
            # Executa a chamada síncrona da biblioteca em um executor de thread
            # para não bloquear o loop de eventos principal do asyncio.
            loop = asyncio.get_event_loop()
            raw_results = await loop.run_in_executor(
                None,  # Usa o executor de thread padrão
                lambda: list(self.search_engine.text(
                    query,
                    region="br-pt",
                    safesearch="moderate",
                    max_results=self.max_resultados
                ))
            )
        except Exception as e:
            logger.error(f"❌ Erro durante a busca para '{query}': {e}", exc_info=True)
            self.status = StatusTentaculo.ERRO # Entra em estado de erro
            return f"❌ Erro ao executar a busca. Detalhes: {e}"

        duracao = time.time() - inicio
        logger.info(f"⏱️  Busca por '{query}' completada em {duracao:.2f}s.")

        # 3. Processar e armazenar resultados
        resultados_finais = [
            ResultadoBusca(
                titulo=r.get("title", "Sem título"),
                url=r.get("href", "#"),
                snippet=r.get("body", "Nenhum resumo disponível.")
            ) for r in raw_results
        ]
        self.cache_buscas[query] = resultados_finais
        logger.info(f"💾 Resultados para '{query}' armazenados no cache.")
        
        self.status = StatusTentaculo.ATIVO # Retorna ao estado ativo
        return self._formatar_resultados(resultados_finais)

    def _formatar_resultados(self, resultados: List[ResultadoBusca]) -> str:
        """Formata os resultados em uma string legível para o Manto."""
        if not resultados:
            return "🔍 Busca concluída: Nenhum resultado encontrado."

        linhas = [f"🔍 Busca concluída. {len(resultados)} resultado(s) principal(is) encontrado(s):\n"]
        for i, res in enumerate(resultados, 1):
            linhas.append(f"{i}. 📄 Título: {res.titulo}")
            linhas.append(f"   🔗 URL: {res.url}")
            if res.snippet:
                snippet_curto = (res.snippet[:200] + "...") if len(res.snippet) > 200 else res.snippet
                linhas.append(f"   💬 Resumo: {snippet_curto}")
            linhas.append("")
        return "\n".join(linhas)

