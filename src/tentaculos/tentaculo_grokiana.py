# src/tentaculos/tentaculo_grokiana.py

import logging
import json
from typing import Dict, Any, List

from .base_tentaculo import BaseTentaculo
from src.cognitive.cerebro import Cerebro
from src.shared.comunicacao import BarramentoEventos

logger = logging.getLogger(__name__)

class TentaculoGrokiana(BaseTentaculo):
    """
    Especialista em transformar o conhecimento da Grokipedia em datasets
    de treinamento para os modelos do OCTOPUS-CONSCIOUSNESS.
    """
    def __init__(self, cerebro: Cerebro, barramento: BarramentoEventos):
        super().__init__("Grokiana", cerebro, barramento)
        logger.info("📚 Tentáculo Grokiana (Minerador de Conhecimento) instanciado.")

    async def pode_executar(self, tarefa: str) -> bool:
        palavras_chave = ["gere um dataset", "treino com grokipedia", "minere conhecimento"]
        return any(palavra in tarefa.lower() for palavra in palavras_chave)

    async def executar_tarefa(self, tarefa: str) -> Dict[str, Any]:
        """Executa o pipeline completo de extração e compilação de dataset."""
        logger.info(f"Grokiana: Iniciando missão de mineração de conhecimento para '{tarefa}'")
        try:
            topico = tarefa.replace("gere um dataset sobre", "").strip()

            # FASE 1: Extrair conteúdo bruto (simulado)
            texto_bruto = self._extrair_conteudo_grokipedia(topico)
            logger.info(f"  -> Fase 1: Conteúdo sobre '{topico}' extraído com sucesso.")

            # FASE 2: Gerar pares de instrução/resposta
            pares_qa = self._gerar_pares_qa(texto_bruto)
            logger.info(f"  -> Fase 2: {len(pares_qa)} pares de instrução/resposta gerados.")

            # FASE 3: Montar e salvar o dataset
            nome_arquivo_dataset = f"dataset_{topico.replace(' ', '_')}.jsonl"
            self._montar_dataset(pares_qa, nome_arquivo_dataset)
            logger.info(f"  -> Fase 3: Dataset salvo como '{nome_arquivo_dataset}'.")

            return {
                "sucesso": True,
                "mensagem": "Dataset de treinamento gerado com sucesso.",
                "caminho_dataset": nome_arquivo_dataset,
                "total_exemplos": len(pares_qa)
            }
        except Exception as e:
            logger.error(f"Erro no TentaculoGrokiana: {e}", exc_info=True)
            return {"sucesso": False, "erro": str(e)}

    def _extrair_conteudo_grokipedia(self, topico: str) -> str:
        """Simula a extração de conteúdo da Grokipedia."""
        # Em um sistema real, usaria o WebScraperCognitivo
        prompt = f"Gere um texto técnico e detalhado, no estilo de um artigo da Grokipedia, sobre o tópico: '{topico}'."
        return self.cerebro.gerar_pensamento(prompt, max_tokens=1000)

    def _gerar_pares_qa(self, texto_bruto: str) -> List[Dict[str, str]]:
        """Usa o Cérebro para transformar texto em pares de instrução/resposta."""
        pares = []
        chunks = texto_bruto.split('\n\n') # Divide o texto em parágrafos
        for chunk in chunks:
            if len(chunk) < 100: continue # Ignora chunks muito pequenos
            
            prompt = (
                "Com base no seguinte texto, formule uma pergunta ou instrução detalhada "
                "cuja resposta seja exatamente este texto. Retorne um JSON com as chaves 'instruction' e 'output'.\n\n"
                f"Texto: \"{chunk}\"\n\n"
                "JSON:"
            )
            resposta_json = self.cerebro.gerar_pensamento(prompt)
            try:
                par = json.loads(resposta_json)
                if "instruction" in par and "output" in par:
                    pares.append(par)
            except json.JSONDecodeError:
                logger.warning("Falha ao parsear par QA, pulando chunk.")
        return pares

    def _montar_dataset(self, pares_qa: List[Dict[str, str]], nome_arquivo: str):
        """Salva os pares em um arquivo .jsonl."""
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            for par in pares_qa:
                # Adiciona o campo "input" vazio, comum em formatos de dataset
                par_completo = {"instruction": par["instruction"], "input": "", "output": par["output"]}
                f.write(json.dumps(par_completo, ensure_ascii=False) + '\n')

