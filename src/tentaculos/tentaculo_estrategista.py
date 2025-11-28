# OCTOPUS-CONSCIOUSNESS/src/tentaculos/tentaculo_estrategista.py

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

from src.tentaculos.estrategista.modelos import PlanoDeAcao, Passo, StatusPasso, MetricasEstrategista, ResultadoEstrategia
from src.tentaculos.estrategista.frameworks import get_all_frameworks, FrameworkEstrategico
from src.tentaculos.estrategista.cache import CacheEstrategia
from src.cognitive.cerebro import Cerebro # Assumindo que o Cerebro é o modelo de IA

logger = logging.getLogger(__name__)

class TentaculoEstrategista:
    """
    O Tentáculo Estrategista é responsável por planejar e coordenar ações complexas.
    Ele utiliza frameworks de pensamento e um sistema de cache para otimizar o planejamento.
    """
    def __init__(self, cerebro: Cerebro, habilitado: bool = True):
        self.cerebro = cerebro
        self.habilitado = habilitado
        self.cache = CacheEstrategia(max_size=50, ttl_segundos=7200)
        self.frameworks = get_all_frameworks()
        self.metricas = MetricasEstrategista()
        logger.info(f"🐙 Tentáculo Estrategista v2.0 inicializado. Habilitado: {self.habilitado}")

    def liga_desliga(self, estado: bool):
        """Ativa ou desativa o tentáculo."""
        self.habilitado = estado
        logger.info(f"Tentáculo Estrategista agora está {'habilitado' if estado else 'desabilitado'}.")

    async def planejar_acao(self, objetivo: str, contexto: Dict[str, Any], framework_preferido: Optional[str] = None) -> Optional[PlanoDeAcao]:
        """
        Gera um Plano de Ação para um objetivo, utilizando o framework mais adequado.
        """
        if not self.habilitado:
            logger.warning("Tentáculo Estrategista desabilitado. Não é possível planejar.")
            return None

        cache_key = f"plano:{objetivo}:{framework_preferido}:{hash(frozenset(contexto.items()))}"
        plano_cache = self.cache.get(cache_key)
        if plano_cache:
            logger.info(f"Plano de Ação recuperado do cache para o objetivo: {objetivo}")
            return plano_cache

        logger.info(f"Iniciando planejamento para o objetivo: {objetivo}")
        start_time = time.time()

        # 1. Seleção e Aplicação do Framework
        framework: FrameworkEstrategico
        if framework_preferido and framework_preferido in self.frameworks:
            framework = self.frameworks[framework_preferido]
        else:
            # Simulação de seleção inteligente baseada no objetivo
            framework = self.frameworks.get("ReversePlanning", self.frameworks["SWOT"])
        
        analise_framework = framework.aplicar(contexto)
        
        # 2. Geração do Plano de Ação (Simulação de chamada ao modelo de IA)
        # Em uma implementação real, o Cerebro (modelo de IA) usaria a análise do framework
        # para gerar a lista de Passos.
        
        passos_sugeridos = [
            Passo(id=1, descricao=f"Analisar o resultado do framework {framework.nome}", tentaculo_responsavel="Perceptivo", tempo_estimado_segundos=10),
            Passo(id=2, descricao="Gerar rascunho do código com Babel", tentaculo_responsavel="Babel", dependencias=[1], tempo_estimado_segundos=120),
            Passo(id=3, descricao="Revisar e refinar o código gerado", tentaculo_responsavel="Logos", dependencias=[2], tempo_estimado_segundos=60),
            Passo(id=4, descricao=f"Concluir o objetivo: {objetivo}", tentaculo_responsavel="Estrategista", dependencias=[3], tempo_estimado_segundos=5)
        ]

        plano = PlanoDeAcao(
            id_plano=str(uuid.uuid4()),
            objetivo=objetivo,
            passos=passos_sugeridos,
            mantos_envolvidos=["Manto Alpha"]
        )

        end_time = time.time()
        tempo_planejamento = end_time - start_time
        
        # 3. Atualização de Métricas e Cache
        self.metricas.planos_gerados += 1
        self.metricas.tempo_medio_planejamento_segundos = (self.metricas.tempo_medio_planejamento_segundos * (self.metricas.planos_gerados - 1) + tempo_planejamento) / self.metricas.planos_gerados
        self.cache.set(cache_key, plano)

        logger.info(f"Plano de Ação gerado em {tempo_planejamento:.2f}s com {len(plano.passos)} passos.")
        return plano

    async def executar_plano(self, plano: PlanoDeAcao) -> ResultadoEstrategia:
        """
        Simula a execução de um Plano de Ação, delegando tarefas aos tentáculos.
        """
        if not self.habilitado:
            return ResultadoEstrategia(sucesso=False, plano_executado=plano, log_execucao=["Tentáculo desabilitado."], metricas=self.metricas, tempo_total_segundos=0)

        logger.info(f"Iniciando execução do plano: {plano.id_plano} - {plano.objetivo}")
        start_time = time.time()
        log_execucao = []
        
        # Simulação de execução sequencial (em um sistema real seria assíncrona e paralela)
        for passo in plano.passos:
            passo.status = StatusPasso.EM_EXECUCAO
            log_execucao.append(f"[{datetime.now().isoformat()}] Executando Passo {passo.id} ({passo.tentaculo_responsavel}): {passo.descricao}")
            
            # Simulação de tempo de execução
            await asyncio.sleep(passo.tempo_estimado_segundos / 10) # Acelera a simulação
            
            # Simulação de sucesso/falha
            if passo.tentaculo_responsavel == "Babel" and passo.id == 2:
                # Simula um sucesso
                passo.status = StatusPasso.CONCLUIDO
                passo.resultado = "Código gerado com sucesso."
                self.metricas.passos_concluidos += 1
            elif passo.tentaculo_responsavel == "Logos" and passo.id == 3:
                # Simula uma falha
                passo.status = StatusPasso.FALHOU
                passo.resultado = "Falha na revisão: Erro de sintaxe."
                self.metricas.passos_falhados += 1
                log_execucao.append(f"[{datetime.now().isoformat()}] ERRO: Passo {passo.id} falhou.")
                break # Interrompe o plano em caso de falha crítica
            else:
                passo.status = StatusPasso.CONCLUIDO
                passo.resultado = "Execução simulada concluída."
                self.metricas.passos_concluidos += 1

            log_execucao.append(f"[{datetime.now().isoformat()}] Passo {passo.id} concluído com status: {passo.status.value}")

        end_time = time.time()
        tempo_total = end_time - start_time
        
        # Atualização de Métricas Finais
        self.metricas.planos_executados += 1
        sucesso_plano = all(p.status == StatusPasso.CONCLUIDO for p in plano.passos)
        
        # Atualiza taxa de sucesso (simples média móvel)
        taxa_atual = 1.0 if sucesso_plano else 0.0
        self.metricas.taxa_sucesso_plano = (self.metricas.taxa_sucesso_plano * (self.metricas.planos_executados - 1) + taxa_atual) / self.metricas.planos_executados

        logger.info(f"Execução do plano {plano.id_plano} finalizada. Sucesso: {sucesso_plano}")

        return ResultadoEstrategia(
            sucesso=sucesso_plano,
            plano_executado=plano,
            log_execucao=log_execucao,
            metricas=self.metricas,
            tempo_total_segundos=tempo_total
        )
