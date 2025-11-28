# OCTOPUS-CONSCIOUSNESS/src/tentaculos/estrategista/cache.py

import time
import logging
from typing import Dict, Any, Optional
from collections import OrderedDict

logger = logging.getLogger(__name__)

class CacheEstrategia:
    """
    Sistema de cache com TTL (Time-To-Live) e política de remoção LRU (Least Recently Used)
    para planos e resultados de estratégias.
    """
    def __init__(self, max_size: int = 100, ttl_segundos: int = 3600):
        self.max_size = max_size
        self.ttl_segundos = ttl_segundos
        # OrderedDict para implementar LRU
        self.cache: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        logger.info(f"Cache de Estratégia inicializado (Tamanho Máx: {max_size}, TTL: {ttl_segundos}s).")

    def _limpar_cache(self):
        """Remove itens expirados e, se necessário, aplica a política LRU."""
        agora = time.time()
        
        # 1. Remover expirados
        chaves_expiradas = []
        for chave, valor in self.cache.items():
            if agora - valor['timestamp'] > self.ttl_segundos:
                chaves_expiradas.append(chave)
        
        for chave in chaves_expiradas:
            del self.cache[chave]
            logger.debug(f"Item expirado removido: {chave}")

        # 2. Aplicar LRU se o tamanho exceder o máximo
        while len(self.cache) > self.max_size:
            chave_lru = next(iter(self.cache)) # Pega a chave mais antiga (LRU)
            del self.cache[chave_lru]
            logger.debug(f"Item LRU removido: {chave_lru}")

    def get(self, chave: str) -> Optional[Any]:
        """Recupera um item do cache, se não estiver expirado."""
        self._limpar_cache()
        
        if chave in self.cache:
            # Move o item para o final (mais recentemente usado)
            valor = self.cache.pop(chave)
            self.cache[chave] = valor
            logger.debug(f"Cache Hit para: {chave}")
            return valor['dado']
        
        logger.debug(f"Cache Miss para: {chave}")
        return None

    def set(self, chave: str, dado: Any):
        """Adiciona ou atualiza um item no cache."""
        self._limpar_cache()
        
        if chave in self.cache:
            # Remove a entrada antiga para garantir que a nova vá para o final (MRU)
            self.cache.pop(chave)
            
        self.cache[chave] = {
            'dado': dado,
            'timestamp': time.time()
        }
        logger.debug(f"Cache Set para: {chave}")

    def size(self) -> int:
        """Retorna o número atual de itens no cache."""
        self._limpar_cache()
        return len(self.cache)

    def clear(self):
        """Limpa todo o cache."""
        self.cache.clear()
        logger.info("Cache de Estratégia limpo.")
