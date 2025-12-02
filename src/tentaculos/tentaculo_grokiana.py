# src/tentaculos/tentaculo_grokiana.py

import logging
import json
import asyncio
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime

from .base_tentaculo import BaseTentaculo
from src.cognitive.cerebro import Cerebro
from src.shared.comunicacao import BarramentoEventos

logger = logging.getLogger(__name__)


class FormatoDataset(Enum):
    """Formatos suportados para exportação de datasets."""
    ALPACA = "alpaca"
    SHAREGPT = "sharegpt"
    OPENAI_CHAT = "openai_chat"
    INSTRUCTION_RESPONSE = "instruction_response"


@dataclass
class ParQA:
    """Representa um par de instrução/resposta com metadados."""
    instruction: str
    output: str
    input: str = ""
    source_url: Optional[str] = None
    confidence_score: float = 1.0
    timestamp: str = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self, formato: FormatoDataset = FormatoDataset.ALPACA) -> Dict[str, Any]:
        """Converte o par para o formato especificado."""
        if formato == FormatoDataset.ALPACA:
            return {
                "instruction": self.instruction,
                "input": self.input,
                "output": self.output
            }
        elif formato == FormatoDataset.SHAREGPT:
            return {
                "conversations": [
                    {"from": "human", "value": self.instruction},
                    {"from": "gpt", "value": self.output}
                ]
            }
        elif formato == FormatoDataset.OPENAI_CHAT:
            return {
                "messages": [
                    {"role": "user", "content": self.instruction},
                    {"role": "assistant", "content": self.output}
                ]
            }
        return asdict(self)


class WebScraperCognitivo:
    """Extrator inteligente de conteúdo web usando análise semântica."""
    
    def __init__(self, cerebro: Cerebro):
        self.cerebro = cerebro
        self.cache = {}
    
    async def extrair_conteudo(self, topico: str, url: Optional[str] = None) -> Tuple[str, Dict[str, Any]]:
        """
        Extrai conteúdo relevante sobre um tópico.
        
        Returns:
            Tuple[str, Dict]: (conteúdo extraído, metadados)
        """
        cache_key = hashlib.md5(topico.encode()).hexdigest()
        
        if cache_key in self.cache:
            logger.info(f"  📦 Conteúdo de '{topico}' recuperado do cache.")
            return self.cache[cache_key]
        
        logger.info(f"  🔍 Extraindo conteúdo sobre '{topico}'...")
        
        # Prompt aprimorado para extração estruturada
        prompt = f"""Você é um extrator especializado de conhecimento técnico.
        
Tarefa: Gere um artigo técnico detalhado e estruturado sobre: "{topico}"

Requisitos:
1. Use seções claras com subtítulos
2. Inclua definições precisas
3. Forneça exemplos práticos
4. Cite conceitos relacionados
5. Mantenha rigor técnico
6. Comprimento: 800-1200 palavras

Estrutura sugerida:
## Visão Geral
## Conceitos Fundamentais
## Aplicações Práticas
## Técnicas Avançadas
## Considerações e Limitações

Artigo:"""

        conteudo = self.cerebro.gerar_pensamento(prompt, max_tokens=2000)
        
        metadados = {
            "topico": topico,
            "url_fonte": url,
            "timestamp_extracao": datetime.utcnow().isoformat(),
            "tamanho_caracteres": len(conteudo),
            "tamanho_palavras": len(conteudo.split())
        }
        
        resultado = (conteudo, metadados)
        self.cache[cache_key] = resultado
        
        return resultado


class GeradorDeParesQA:
    """Transformador inteligente de texto em pares instrução/resposta."""
    
    def __init__(self, cerebro: Cerebro):
        self.cerebro = cerebro
        self.min_chunk_size = 150
        self.max_chunk_size = 800
        self.min_confidence = 0.6
    
    async def gerar_pares(self, texto: str, metadados: Dict[str, Any]) -> List[ParQA]:
        """
        Gera pares QA de alta qualidade a partir do texto.
        
        Args:
            texto: Texto fonte
            metadados: Metadados da extração
            
        Returns:
            Lista de ParQA validados
        """
        logger.info("  🧠 Gerando pares de instrução/resposta...")
        
        chunks = self._segmentar_texto_inteligente(texto)
        logger.info(f"    → Texto dividido em {len(chunks)} chunks semânticos")
        
        pares = []
        tarefas = [self._processar_chunk(chunk, metadados, idx) 
                   for idx, chunk in enumerate(chunks)]
        
        # Processamento paralelo dos chunks
        resultados = await asyncio.gather(*tarefas, return_exceptions=True)
        
        for resultado in resultados:
            if isinstance(resultado, ParQA):
                if resultado.confidence_score >= self.min_confidence:
                    pares.append(resultado)
                else:
                    logger.debug(f"    ⚠️ Par descartado (confiança: {resultado.confidence_score:.2f})")
        
        logger.info(f"    ✅ {len(pares)} pares de alta qualidade gerados")
        return pares
    
    def _segmentar_texto_inteligente(self, texto: str) -> List[str]:
        """Segmenta texto respeitando limites semânticos."""
        # Primeiro tenta dividir por seções (##)
        secoes = texto.split('\n## ')
        chunks = []
        
        for secao in secoes:
            if len(secao) < self.min_chunk_size:
                continue
                
            if len(secao) <= self.max_chunk_size:
                chunks.append(secao.strip())
            else:
                # Divide seções grandes por parágrafos
                paragrafos = secao.split('\n\n')
                chunk_atual = ""
                
                for paragrafo in paragrafos:
                    if len(chunk_atual) + len(paragrafo) <= self.max_chunk_size:
                        chunk_atual += "\n\n" + paragrafo if chunk_atual else paragrafo
                    else:
                        if chunk_atual:
                            chunks.append(chunk_atual.strip())
                        chunk_atual = paragrafo
                
                if chunk_atual:
                    chunks.append(chunk_atual.strip())
        
        return [c for c in chunks if len(c) >= self.min_chunk_size]
    
    async def _processar_chunk(self, chunk: str, metadados: Dict, idx: int) -> ParQA:
        """Processa um chunk individual gerando um par QA."""
        prompt = f"""Você é um especialista em criar dados de treinamento para modelos de linguagem.

**Tarefa:** Gerar uma instrução/pergunta e sua resposta baseada no texto abaixo.

**Texto:**
{chunk}

**Requisitos:**
1. A instrução deve ser natural, específica e desafiadora
2. A resposta deve reformular o conhecimento do texto (não copiar literalmente)
3. Mantenha precisão técnica
4. Use linguagem clara e profissional

**Formato de saída (JSON válido):**
{{
  "instruction": "sua pergunta ou instrução aqui",
  "output": "resposta detalhada aqui",
  "confidence": 0.95,
  "reasoning": "breve explicação da qualidade do par"
}}

JSON:"""

        try:
            resposta = self.cerebro.gerar_pensamento(prompt, max_tokens=800)
            
            # Limpeza robusta do JSON
            resposta = resposta.strip()
            if "```json" in resposta:
                resposta = resposta.split("```json")[1].split("```")[0]
            elif "```" in resposta:
                resposta = resposta.split("```")[1].split("```")[0]
            
            dados = json.loads(resposta.strip())
            
            return ParQA(
                instruction=dados["instruction"],
                output=dados["output"],
                source_url=metadados.get("url_fonte"),
                confidence_score=dados.get("confidence", 0.8),
                metadata={
                    "chunk_index": idx,
                    "reasoning": dados.get("reasoning", ""),
                    "topico_fonte": metadados.get("topico")
                }
            )
            
        except Exception as e:
            logger.warning(f"    ⚠️ Erro ao processar chunk {idx}: {e}")
            # Retorna par com confiança baixa para ser filtrado
            return ParQA(
                instruction="erro",
                output="erro",
                confidence_score=0.0
            )


class MontadorDeDataset:
    """Compilador e validador de datasets de treinamento."""
    
    def __init__(self, diretorio_saida: str = "datasets"):
        self.diretorio = Path(diretorio_saida)
        self.diretorio.mkdir(parents=True, exist_ok=True)
    
    def montar_dataset(
        self,
        pares: List[ParQA],
        nome_topico: str,
        formato: FormatoDataset = FormatoDataset.ALPACA
    ) -> Dict[str, Any]:
        """
        Compila pares em um dataset formatado.
        
        Returns:
            Dict com estatísticas e caminho do arquivo
        """
        logger.info(f"  📊 Montando dataset no formato {formato.value}...")
        
        # Validação e filtragem final
        pares_validos = self._validar_pares(pares)
        
        # Gera nome de arquivo único
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"{nome_topico}_{formato.value}_{timestamp}.jsonl"
        caminho_completo = self.diretorio / nome_arquivo
        
        # Escreve dataset
        with open(caminho_completo, 'w', encoding='utf-8') as f:
            for par in pares_validos:
                linha = json.dumps(par.to_dict(formato), ensure_ascii=False)
                f.write(linha + '\n')
        
        # Gera arquivo de metadados
        self._salvar_metadados(pares_validos, nome_topico, caminho_completo)
        
        estatisticas = self._gerar_estatisticas(pares_validos)
        
        logger.info(f"    ✅ Dataset salvo: {caminho_completo}")
        logger.info(f"    📈 Estatísticas: {estatisticas['total_exemplos']} exemplos, "
                   f"confiança média: {estatisticas['confidence_media']:.2f}")
        
        return {
            "caminho": str(caminho_completo),
            "formato": formato.value,
            **estatisticas
        }
    
    def _validar_pares(self, pares: List[ParQA]) -> List[ParQA]:
        """Aplica filtros de qualidade nos pares."""
        validos = []
        
        for par in pares:
            # Filtros de qualidade
            if len(par.instruction) < 20:
                logger.debug(f"    ⚠️ Instrução muito curta descartada")
                continue
            
            if len(par.output) < 50:
                logger.debug(f"    ⚠️ Resposta muito curta descartada")
                continue
            
            if par.instruction.lower() == par.output.lower():
                logger.debug(f"    ⚠️ Instrução idêntica à resposta descartada")
                continue
            
            validos.append(par)
        
        logger.info(f"    ✓ {len(validos)}/{len(pares)} pares passaram na validação")
        return validos
    
    def _salvar_metadados(self, pares: List[ParQA], topico: str, caminho_dataset: Path):
        """Salva metadados do dataset para rastreabilidade."""
        metadados = {
            "topico": topico,
            "timestamp_criacao": datetime.utcnow().isoformat(),
            "total_exemplos": len(pares),
            "confidence_scores": [p.confidence_score for p in pares],
            "fonte_dados": "TentaculoGrokiana",
            "versao_pipeline": "2.0"
        }
        
        caminho_meta = caminho_dataset.with_suffix('.meta.json')
        with open(caminho_meta, 'w', encoding='utf-8') as f:
            json.dump(metadados, f, indent=2, ensure_ascii=False)
    
    def _gerar_estatisticas(self, pares: List[ParQA]) -> Dict[str, Any]:
        """Gera estatísticas descritivas do dataset."""
        if not pares:
            return {"total_exemplos": 0}
        
        tamanhos_inst = [len(p.instruction) for p in pares]
        tamanhos_out = [len(p.output) for p in pares]
        confidences = [p.confidence_score for p in pares]
        
        return {
            "total_exemplos": len(pares),
            "confidence_media": sum(confidences) / len(confidences),
            "confidence_min": min(confidences),
            "tamanho_medio_instrucao": sum(tamanhos_inst) / len(tamanhos_inst),
            "tamanho_medio_resposta": sum(tamanhos_out) / len(tamanhos_out),
        }


class TentaculoGrokiana(BaseTentaculo):
    """
    Especialista em transformar conhecimento externo em datasets de treinamento
    otimizados para fine-tuning de modelos de linguagem.
    
    Pipeline:
    1. WebScraperCognitivo: Extração inteligente de conteúdo
    2. GeradorDeParesQA: Transformação em pares instrução/resposta
    3. MontadorDeDataset: Compilação e validação do dataset final
    """
    
    def __init__(self, cerebro: Cerebro, barramento: BarramentoEventos):
        super().__init__("Grokiana", cerebro, barramento)
        self.scraper = WebScraperCognitivo(cerebro)
        self.gerador = GeradorDeParesQA(cerebro)
        self.montador = MontadorDeDataset()
        logger.info("📚 Tentáculo Grokiana (Minerador de Conhecimento v2.0) instanciado.")
    
    async def pode_executar(self, tarefa: str) -> bool:
        """Verifica se a tarefa é de competência do Grokiana."""
        palavras_chave = [
            "gere um dataset",
            "criar dataset",
            "treino com grokipedia",
            "minere conhecimento",
            "extrair conhecimento",
            "preparar dados de treinamento"
        ]
        return any(palavra in tarefa.lower() for palavra in palavras_chave)
    
    async def executar_tarefa(self, tarefa: str, **kwargs) -> Dict[str, Any]:
        """
        Executa o pipeline completo de mineração e compilação de dataset.
        
        Args:
            tarefa: Descrição da tarefa
            **kwargs: Parâmetros opcionais
                - formato: FormatoDataset (default: ALPACA)
                - url_fonte: URL específica para extração
                
        Returns:
            Dict com resultado da operação e metadados
        """
        logger.info(f"🚀 Grokiana: Iniciando missão para '{tarefa}'")
        
        try:
            # Extrai tópico da tarefa
            topico = self._extrair_topico(tarefa)
            formato = kwargs.get('formato', FormatoDataset.ALPACA)
            url = kwargs.get('url_fonte')
            
            logger.info(f"  📌 Tópico identificado: '{topico}'")
            logger.info(f"  📋 Formato de saída: {formato.value}")
            
            # FASE 1: Extração de Conteúdo
            texto_bruto, metadados = await self.scraper.extrair_conteudo(topico, url)
            
            # FASE 2: Geração de Pares QA
            pares_qa = await self.gerador.gerar_pares(texto_bruto, metadados)
            
            if not pares_qa:
                return {
                    "sucesso": False,
                    "erro": "Nenhum par de qualidade foi gerado",
                    "topico": topico
                }
            
            # FASE 3: Montagem do Dataset
            resultado_dataset = self.montador.montar_dataset(
                pares_qa,
                topico.replace(' ', '_'),
                formato
            )
            
            # Emite evento de conclusão
            await self.barramento.emitir("dataset_criado", {
                "tentaculo": self.nome,
                "topico": topico,
                **resultado_dataset
            })
            
            return {
                "sucesso": True,
                "mensagem": f"Dataset de treinamento gerado com sucesso sobre '{topico}'",
                "topico": topico,
                **resultado_dataset
            }
            
        except Exception as e:
            logger.error(f"❌ Erro no TentaculoGrokiana: {e}", exc_info=True)
            return {
                "sucesso": False,
                "erro": str(e),
                "tipo_erro": type(e).__name__
            }
    
    def _extrair_topico(self, tarefa: str) -> str:
        """Extrai o tópico principal da descrição da tarefa."""
        # Remove palavras de comando comuns
        palavras_remover = [
            "gere um dataset sobre",
            "criar dataset sobre",
            "minere conhecimento sobre",
            "extrair conhecimento sobre"
        ]
        
        topico = tarefa.lower()
        for palavra in palavras_remover:
            topico = topico.replace(palavra, "")
        
        return topico.strip()
    
    def get_estatisticas(self) -> Dict[str, Any]:
        """Retorna estatísticas de uso do tentáculo."""
        # Conta arquivos no diretório de datasets
        arquivos_dataset = list(self.montador.diretorio.glob("*.jsonl"))
        
        return {
            "total_datasets_gerados": len(arquivos_dataset),
            "diretorio_saida": str(self.montador.diretorio),
            "formatos_suportados": [f.value for f in FormatoDataset],
            "cache_extraidor": len(self.scraper.cache)
        }