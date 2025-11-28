# OCTOPUS-CONSCIOUSNESS/src/tentaculos/tentaculo_musa.py

import asyncio
import logging
from typing import Dict, Any, Optional, List
import random
import hashlib

from src.tentaculos.musa.modelos import (
    FaseCreativa, TipoPromptDivergente, IdeiaBruta, IdeiaAvaliada,
    DossieDeConceito, ConfiguracaoMusa, MetricasMusa
)
from src.cognitive.cerebro import Cerebro # Assumindo que o Cerebro é o modelo de IA

logger = logging.getLogger(__name__)

class TentaculoMusa:
    """
    O Tentáculo Musa é responsável pela ideiação criativa, utilizando um ciclo
    Divergir-Convergir-Sintetizar para gerar conceitos inovadores.
    """
    def __init__(self, cerebro: Cerebro, habilitado: bool = True, config: ConfiguracaoMusa = ConfiguracaoMusa()):
        self.cerebro = cerebro
        self.habilitado = habilitado
        self.config = config
        self.metricas = MetricasMusa()
        logger.info(f"🎨 Tentáculo Musa v2.0 inicializado. Habilitado: {self.habilitado}")

    def liga_desliga(self, estado: bool):
        """Ativa ou desativa o tentáculo."""
        self.habilitado = estado
        logger.info(f"Tentáculo Musa agora está {'habilitado' if estado else 'desabilitado'}.")

    async def _fase_divergencia(self, tema: str) -> List[IdeiaBruta]:
        """Gera um grande volume de ideias brutas a partir de prompts criativos."""
        logger.info(f"Iniciando Fase de Divergência para o tema: {tema}")
        ideias_brutas: List[IdeiaBruta] = []
        
        prompts_criativos = [
            f"Gere uma analogia forçada para '{tema}' usando um conceito de culinária.",
            f"O que seria o oposto óbvio de '{tema}' e como isso poderia ser útil?",
            f"Injete um elemento de ruído (ex: 'viagem no tempo') em '{tema}' e descreva o resultado."
        ]
        
        for i in range(self.config.num_ideias_divergencia):
            prompt = random.choice(prompts_criativos)
            
            # Simulação de geração de ideia pelo modelo de IA (Cerebro)
            await asyncio.sleep(0.05)
            descricao_ideia = f"Ideia {i+1} para '{tema}' gerada com prompt: {prompt[:30]}..."
            
            # Geração de fingerprint para deduplicação
            fingerprint = hashlib.sha256(descricao_ideia.encode('utf-8')).hexdigest()
            
            ideias_brutas.append(IdeiaBruta(
                id=i + 1,
                descricao=descricao_ideia,
                origem_prompt=prompt,
                fingerprint=fingerprint
            ))
            self.metricas.ideias_geradas += 1

        logger.info(f"Fase de Divergência concluída. {len(ideias_brutas)} ideias geradas.")
        return ideias_brutas

    async def _fase_convergencia(self, ideias: List[IdeiaBruta]) -> List[IdeiaAvaliada]:
        """Avalia e seleciona as melhores ideias com base em critérios."""
        logger.info("Iniciando Fase de Convergência (Avaliação e Seleção)")
        ideias_avaliadas: List[IdeiaAvaliada] = []
        
        # Deduplicação (simulada)
        ideias_unicas = {ideia.fingerprint: ideia for ideia in ideias}.values()
        self.metricas.ideias_deduplicadas = len(ideias) - len(ideias_unicas)
        
        for ideia in ideias_unicas:
            # Simulação de avaliação pelo modelo de IA (Cerebro)
            await asyncio.sleep(0.1)
            
            score_orig = random.uniform(0.5, 1.0)
            score_pot = random.uniform(0.4, 0.9)
            score_viab = random.uniform(0.3, 0.8)
            
            score_final = (
                score_orig * self.config.peso_originalidade +
                score_pot * self.config.peso_potencial +
                score_viab * self.config.peso_viabilidade
            )
            
            ideias_avaliadas.append(IdeiaAvaliada(
                ideia=ideia,
                score_originalidade=score_orig,
                score_potencial=score_pot,
                score_viabilidade=score_viab,
                score_final=score_final,
                justificativa=f"Pontuação final {score_final:.2f} baseada em originalidade, potencial e viabilidade."
            ))

        # Seleciona as N melhores ideias
        ideias_avaliadas.sort(key=lambda x: x.score_final, reverse=True)
        sementes = ideias_avaliadas[:self.config.num_sementes_selecionadas]
        
        logger.info(f"Fase de Convergência concluída. {len(sementes)} sementes selecionadas.")
        return sementes

    async def _fase_sintese(self, sementes: List[IdeiaAvaliada], tema: str) -> DossieDeConceito:
        """Combina as sementes selecionadas em um conceito coeso e detalhado."""
        logger.info("Iniciando Fase de Síntese (Criação do Conceito Vencedor)")
        
        # Simulação de síntese pelo modelo de IA (Cerebro)
        await asyncio.sleep(0.5)
        
        semente_vencedora = sementes[0]
        
        conceito_vencedor = f"Conceito Sintetizado para '{tema}'"
        manifesto = f"Este conceito é uma fusão da ideia principal '{semente_vencedora.ideia.descricao[:50]}...' com elementos de outras sementes."
        descricao_detalhada = "Detalhes técnicos e conceituais do novo conceito, pronto para ser transformado em um Plano de Ação pelo Estrategista."
        proximo_passo = "Criar um Plano de Ação para prototipar o conceito."
        
        self.metricas.conceitos_vencedores[tema] = self.metricas.conceitos_vencedores.get(tema, 0) + 1
        
        return DossieDeConceito(
            sucesso=True,
            conceito_vencedor=conceito_vencedor,
            manifesto=manifesto,
            descricao_detalhada=descricao_detalhada,
            proximo_passo_sugerido=proximo_passo,
            ideia_original=semente_vencedora
        )

    async def ciclo_criativo(self, tema: str) -> Optional[DossieDeConceito]:
        """Executa o ciclo completo Divergir-Convergir-Sintetizar."""
        if not self.habilitado:
            logger.warning("Tentáculo Musa desabilitado. Não é possível iniciar o ciclo criativo.")
            return None

        start_time = datetime.now()
        logger.info(f"Iniciando Ciclo Criativo para: {tema}")

        try:
            # 1. Divergência
            ideias_brutas = await self._fase_divergencia(tema)
            
            # 2. Convergência
            sementes = await self._fase_convergencia(ideias_brutas)
            
            if not sementes:
                logger.error("Nenhuma ideia foi selecionada na fase de convergência.")
                return None
                
            # 3. Síntese
            dossie = await self._fase_sintese(sementes, tema)
            
            end_time = datetime.now()
            tempo_total = (end_time - start_time).total_seconds()
            
            # Atualização de Métricas
            self.metricas.total_ciclos_criativos += 1
            self.metricas.tempo_medio_ciclo = (self.metricas.tempo_medio_ciclo * (self.metricas.total_ciclos_criativos - 1) + tempo_total) / self.metricas.total_ciclos_criativos

            logger.info(f"Ciclo Criativo concluído em {tempo_total:.2f}s. Conceito Vencedor: {dossie.conceito_vencedor}")
            return dossie

        except Exception as e:
            logger.error(f"Erro durante o ciclo criativo: {e}")
            return None
