# src/tentaculos/tentaculo_busca.py

import asyncio
import logging
import time
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass

from duckduckgo_search import DDGS

# Importando componentes da arquitetura
from .base_tentaculo import BaseTentaculo
from src.shared.estado_sistema import StatusTentaculo

# Configuração do logger
logger = logging.getLogger(__name__)

# --- Constantes de Configuração ---

class ConfigBusca:
    """Constantes de configuração para o TentaculoBusca."""
    TIMEOUT_CONSULTA_SEGUNDOS = 15
    MAX_RETRIES = 3
    BACKOFF_BASE_SEGUNDOS = 1
    TAMANHO_MAX_CACHE = 200
    TEMPO_EXPIRACAO_CACHE_MINUTOS = 120 # 2 horas

# --- Estruturas de Dados ---

@dataclass
class MetricasBusca:
    """Métricas de desempenho para o tentáculo de busca."""
    total_consultas: int = 0
    consultas_sucesso: int = 0
    consultas_falha: int = 0
    tempo_total_ms: int = 0

    @property
    def taxa_sucesso(self) -> float:
        return self.consultas_sucesso / self.total_consultas if self.total_consultas > 0 else 0.0

    @property
    def latencia_media(self) -> float:
        return self.tempo_total_ms / self.total_consultas if self.total_consultas > 0 else 0.0

@dataclass
class EntradaCacheBusca:
    """Entrada do cache para resultados de busca."""
    resultado_formatado: str
    timestamp: datetime

# --- O Tentáculo de Busca Refatorado ---

class TentaculoBusca(BaseTentaculo):
    """
    Tentáculo especialista em busca na web, refatorado para robustez e eficiência.
    """
    PALAVRAS_CHAVE = {"pesquisar", "buscar", "procurar", "encontrar", "o que é", "quem foi"}
    PALAVRAS_REMOVER = {"pesquisar", "buscar", "procurar", "encontrar", "informações sobre", "sobre", "por"}

    def __init__(self, id_tentaculo: int, max_resultados: int = 3):
        super().__init__(id_tentaculo, "Busca na Web")
        self.search_engine = DDGS()
        self.max_resultados = max_resultados
        
        # Componentes de robustez
        self.cache_buscas: Dict[str, EntradaCacheBusca] = {}
        self.metricas = MetricasBusca()
        
        # Locks para operações concorrentes seguras
        self._lock_status = asyncio.Lock()
        self._lock_cache = asyncio.Lock()
        self._lock_metricas = asyncio.Lock()
        
        logger.info(f"✅ Tentáculo Busca #{id_tentaculo} inicializado com padrão industrial.")

    def _gerar_hash_query(self, query: str) -> str:
        """Gera um hash SHA256 para a query, usado como chave de cache."""
        return hashlib.sha256(query.encode('utf-8')).hexdigest()

    async def _verificar_cache(self, query: str) -> Optional[str]:
        """Verifica o cache por uma resposta válida e não expirada."""
        async with self._lock_cache:
            hash_query = self._gerar_hash_query(query)
            entrada = self.cache_buscas.get(hash_query)
            
            if entrada:
                idade = datetime.now() - entrada.timestamp
                if idade < timedelta(minutes=ConfigBusca.TEMPO_EXPIRACAO_CACHE_MINUTOS):
                    logger.info(f"  ✓ Cache hit para query '{query[:30]}...'")
                    return entrada.resultado_formatado
                else:
                    del self.cache_buscas[hash_query]
                    logger.info(f"  ✗ Cache expirado removido para query '{query[:30]}...'")
            return None

    async def _adicionar_cache(self, query: str, resultado: str):
        """Adiciona um resultado ao cache, com controle de tamanho."""
        async with self._lock_cache:
            if len(self.cache_buscas) >= ConfigBusca.TAMANHO_MAX_CACHE:
                entrada_mais_antiga = min(self.cache_buscas.items(), key=lambda x: x[1].timestamp)
                del self.cache_buscas[entrada_mais_antiga[0]]
                logger.info("  🗑️ Cache de busca cheio, entrada mais antiga removida.")
            
            hash_query = self._gerar_hash_query(query)
            self.cache_buscas[hash_query] = EntradaCacheBusca(
                resultado_formatado=resultado,
                timestamp=datetime.now()
            )

    def _extrair_query(self, descricao_missao: str) -> str:
        """Extrai e limpa o termo de busca da descrição da missão."""
        query = descricao_missao.lower()
        for palavra in self.PALAVRAS_REMOVER:
            query = query.replace(palavra, "")
        return query.strip()

    async def gerar_proposta(self, token_missao: Dict) -> Optional[Dict[str, Any]]:
        """Analisa a missão e gera uma proposta de execução."""
        descricao = token_missao.get("descricao", "").lower()
        if not any(palavra in descricao for palavra in self.PALAVRAS_CHAVE):
            return None

        query = self._extrair_query(descricao)
        if not query:
            return None

        # A confiança pode ser baseada na taxa de sucesso histórica
        confianca = 0.8 + (self.metricas.taxa_sucesso * 0.15)

        return {
            "id_tentaculo": self.id,
            "tipo": self.tipo,
            "confianca": round(confianca, 2),
            "plano_de_acao_interno": f"Buscar por '{query}' usando DDGS com {self.max_resultados} resultados.",
            "custo_estimado": "Nenhum (API Gratuita)"
        }

    async def executar(self, token_missao: Dict) -> str:
        """Executa a busca com cache, retry e coleta de métricas."""
        async with self._lock_status:
            self.status = StatusTentaculo.OCUPADO
        
        query = self._extrair_query(token_missao.get("descricao", ""))
        if not query:
            return "❌ Erro: Missão de busca sem um termo válido."

        logger.info(f"⚡ Tentáculo Busca ativado. Query: '{query}'")

        try:
            # 1. Verificar cache
            cache_hit = await self._verificar_cache(query)
            if cache_hit:
                return f"💨 Resposta do Cache:\n{cache_hit}"

            # 2. Executar busca com retry
            resultados, sucesso, latencia = await self._buscar_com_retry(query)

            # 3. Atualizar métricas
            async with self._lock_metricas:
                self.metricas.total_consultas += 1
                self.metricas.tempo_total_ms += latencia
                if sucesso:
                    self.metricas.consultas_sucesso += 1
                else:
                    self.metricas.consultas_falha += 1

            if not sucesso:
                return f"❌ Erro: Falha ao buscar por '{query}' após múltiplas tentativas."

            # 4. Formatar e adicionar ao cache
            resultado_formatado = self._formatar_resultados(resultados)
            await self._adicionar_cache(query, resultado_formatado)
            
            return resultado_formatado

        except Exception as e:
            logger.error(f"Erro crítico na execução do TentaculoBusca: {e}", exc_info=True)
            return f"❌ Erro interno no tentáculo: {str(e)}"
        finally:
            async with self._lock_status:
                self.status = StatusTentaculo.ATIVO

    async def _buscar_com_retry(self, query: str) -> Tuple[Optional[List[Dict]], bool, int]:
        """Tenta executar a busca com lógica de retry e backoff."""
        for tentativa in range(ConfigBusca.MAX_RETRIES):
            try:
                inicio = time.time()
                # Executa a chamada síncrona em um executor para não bloquear o loop
                loop = asyncio.get_event_loop()
                results = await asyncio.wait_for(
                    loop.run_in_executor(
                        None,
                        lambda: list(self.search_engine.text(
                            query,
                            region="br-pt",
                            safesearch="moderate",
                            max_results=self.max_resultados
                        ))
                    ),
                    timeout=ConfigBusca.TIMEOUT_CONSULTA_SEGUNDOS
                )
                latencia_ms = int((time.time() - inicio) * 1000)
                logger.info(f"  ✓ Busca por '{query}' bem-sucedida em {latencia_ms}ms.")
                return results, True, latencia_ms

            except asyncio.TimeoutError:
                logger.warning(f"  ⏱️ Timeout na busca por '{query}' (tentativa {tentativa + 1})")
            except Exception as e:
                logger.error(f"  ❌ Erro na busca por '{query}' (tentativa {tentativa + 1}): {e}")

            if tentativa < ConfigBusca.MAX_RETRIES - 1:
                tempo_espera = ConfigBusca.BACKOFF_BASE_SEGUNDOS * (2 ** tentativa)
                logger.info(f"  ⏳ Tentando novamente em {tempo_espera}s...")
                await asyncio.sleep(tempo_espera)
        
        return None, False, ConfigBusca.TIMEOUT_CONSULTA_SEGUNDOS * 1000

    def _formatar_resultados(self, resultados: Optional[List[Dict]]) -> str:
        """Formata os resultados da busca em uma string legível."""
        if not resultados:
            return "🔍 Busca concluída: Nenhum resultado encontrado."

        linhas = [f"🔍 Busca concluída. {len(resultados)} resultado(s) principal(is) encontrado(s):\n"]
        for i, res in enumerate(resultados, 1):
            linhas.append(f"{i}. 📄 Título: {res.get('title', 'Sem título')}")
            linhas.append(f"   🔗 URL: {res.get('href', '#')}")
            snippet = res.get('body')
            if snippet:
                snippet_curto = (snippet[:200] + "...") if len(snippet) > 200 else snippet
                linhas.append(f"   💬 Resumo: {snippet_curto}")
            linhas.append("")
        return "\n".join(linhas)

    def obter_relatorio_metricas(self) -> str:
        """Gera um relatório de métricas de desempenho do tentáculo."""
        return (
            f"📊 Relatório do Tentáculo Busca #{self.id}:\n"
            f"  Taxa de Sucesso: {self.metricas.taxa_sucesso:.2%}\n"
            f"  Consultas Totais: {self.metricas.total_consultas} (Sucesso: {self.metricas.consultas_sucesso}, Falha: {self.metricas.consultas_falha})\n"
            f"  Latência Média: {self.metricas.latencia_media:.0f}ms\n"
            f"  Entradas no Cache: {len(self.cache_buscas)}/{ConfigBusca.TAMANHO_MAX_CACHE}"
        )

