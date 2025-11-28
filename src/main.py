# OCTOPUS-CONSCIOUSNESS/src/main.py

import asyncio
import logging
import sys
from typing import Dict, Any

# Configuração básica de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("OCTOPUS-CONSCIOUSNESS")

# Importação dos componentes principais
from src.cognitive.cerebro import Cerebro
from src.mantos.manto_alpha import MantoAlpha
from src.mantos.manto_beta import MantoBeta

async def main():
    """
    Função principal de inicialização e demonstração do sistema OCTOPUS-CONSCIOUSNESS v2.0.
    """
    logger.info("=====================================================")
    logger.info("  INICIALIZANDO OCTOPUS-CONSCIOUSNESS v2.0")
    logger.info("  Arquitetura Bio-Inspirada: Mantos e Tentáculos")
    logger.info("=====================================================")

    # 1. Inicializar o Cérebro (Modelo de IA Central)
    cerebro = Cerebro()

    # 2. Inicializar os Mantos (Coordenadores)
    manto_alpha = MantoAlpha(cerebro=cerebro)
    manto_beta = MantoBeta(cerebro=cerebro)

    # 3. Iniciar tarefas de monitoramento (ex: Perceptivo)
    await manto_alpha.iniciar_monitoramento()

    # 4. Demonstração de Uso - Manto Alpha (Estratégia)
    logger.info("\n--- DEMO: Manto Alpha (Estratégia e Execução) ---")
    objetivo_alpha = "Desenvolver um novo módulo de cache de alto desempenho."
    contexto_alpha = {"recursos": ["Python", "AsyncIO"], "prioridade": "Alta"}
    
    resultado_alpha = await manto_alpha.executar_objetivo(objetivo_alpha, contexto_alpha)
    logger.info(f"Resultado Final do Objetivo Alpha: Sucesso={resultado_alpha['sucesso']}")
    # logger.info(f"Log de Execução: {resultado_alpha['resultado_execucao']['log_execucao']}")

    # 5. Demonstração de Uso - Manto Beta (Criatividade)
    logger.info("\n--- DEMO: Manto Beta (Criatividade) ---")
    tema_beta = "Um novo mecanismo de comunicação inter-tentáculos."
    resultado_beta = await manto_beta.gerar_conceito_criativo(tema_beta)
    logger.info(f"Resultado Final do Ciclo Criativo: Sucesso={resultado_beta['sucesso']}")
    if resultado_beta['sucesso']:
        logger.info(f"Conceito Vencedor: {resultado_beta['dossie_conceito']['conceito_vencedor']}")

    # 6. Demonstração de Uso - Manto Beta (Transpilação)
    logger.info("\n--- DEMO: Manto Beta (Transpilação Babel) ---")
    intencao_babel = "analisar dados e salvar o resultado em um arquivo."
    resultado_babel = await manto_beta.transpilhar_e_validar(intencao_babel)
    logger.info(f"Resultado Final da Transpilação: Sucesso={resultado_babel['sucesso']}")
    if resultado_babel['sucesso'] and resultado_babel['resultado_transpilacao']['script_gerado']:
        logger.info(f"Código Gerado (trecho): \n{resultado_babel['resultado_transpilacao']['script_gerado'][:200]}...")

    logger.info("\n=====================================================")
    logger.info("  DEMONSTRAÇÃO CONCLUÍDA. Sistema v2.0 pronto.")
    logger.info("=====================================================")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Execução interrompida pelo usuário.")
    except Exception as e:
        logger.error(f"Erro fatal na execução: {e}", exc_info=True)
        sys.exit(1)
