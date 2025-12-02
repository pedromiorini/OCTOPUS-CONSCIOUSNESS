# src/tentaculos/tentaculo_scholara.py

import logging
import requests
import xml.etree.ElementTree as ET
from typing import Dict, Any, List
from dataclasses import dataclass, field

from .base_tentaculo import BaseTentaculo
from src.cognitive.cerebro import Cerebro
from src.shared.comunicacao import BarramentoEventos

logger = logging.getLogger(__name__)

@dataclass
class DossieInteligenciaBruta:
    """Estrutura para o resumo de um artigo científico."""
    id_arxiv: str
    titulo: str
    autores: List[str]
    afiliacoes: List[str] = field(default_factory=list) # Simulado
    resumo: str
    problema_declarado: str
    metodologia_proposta: str
    resultados_reivindicados: str
    limitacoes_admitidas: str
    referencias_citadas: List[str] = field(default_factory=list) # Simulado
    url_pdf: str
    timestamp_extracao: str

class TentaculoScholara(BaseTentaculo):
    """
    Especialista em descobrir, extrair e sumarizar conhecimento bruto
    de artigos científicos, primariamente do arXiv.
    """
    def __init__(self, cerebro: Cerebro, barramento: BarramentoEventos):
        super().__init__("Scholara", cerebro, barramento)
        self.api_base_url = "http://export.arxiv.org/api/query?"
        logger.info("🔭 Tentáculo Scholara (Caçador de Conhecimento) instanciado.")

    async def pode_executar(self, tarefa: str) -> bool:
        """Verifica se a tarefa é de busca ou extração de artigos."""
        palavras_chave = ["arxiv", "artigo científico", "pesquisa de ponta", "últimos papers"]
        return any(palavra in tarefa.lower() for palavra in palavras_chave)

    async def executar_tarefa(self, tarefa: str, **kwargs) -> Dict[str, Any]:
        """
        Executa tarefas de descoberta e extração de artigos.
        
        Exemplos de tarefas:
        - "Busque os últimos artigos sobre 'Mixture of Experts' no arXiv"
        - "Extraia o dossiê do artigo com ID '2511.13593'"
        """
        logger.info(f"Scholara: Recebida tarefa '{tarefa}'")
        try:
            if "busque os últimos artigos" in tarefa.lower():
                topico = tarefa.split("sobre")[-1].strip().replace("'", "")
                return await self._buscar_novos_artigos(topico)
            
            if "extraia o dossiê" in tarefa.lower():
                id_arxiv = tarefa.split("'")[-2]
                return await self._gerar_dossie_de_artigo(id_arxiv)

            return {"sucesso": False, "erro": "Comando Scholara não reconhecido."}
        except Exception as e:
            logger.error(f"Erro no TentaculoScholara: {e}", exc_info=True)
            return {"sucesso": False, "erro": str(e)}

    async def _buscar_novos_artigos(self, topico: str, max_results: int = 5) -> Dict[str, Any]:
        """Busca por novos artigos relevantes no arXiv."""
        await self._publicar_raciocinio(f"Buscando novos artigos no arXiv sobre '{topico}'.")
        
        query = f'search_query=all:"{topico}"&sortBy=submittedDate&sortOrder=descending&max_results={max_results}'
        response = requests.get(self.api_base_url + query)
        
        if response.status_code != 200:
            return {"sucesso": False, "erro": f"Falha na API do arXiv (status {response.status_code})"}

        root = ET.fromstring(response.content)
        namespace = {'arxiv': 'http://www.w3.org/2005/Atom'}
        
        artigos_encontrados = []
        for entry in root.findall('arxiv:entry', namespace):
            id_arxiv = entry.find('arxiv:id', namespace).text.split('/abs/')[-1]
            titulo = entry.find('arxiv:title', namespace).text.strip()
            autores = [author.find('arxiv:name', namespace).text for author in entry.findall('arxiv:author', namespace)]
            
            artigos_encontrados.append({
                "id_arxiv": id_arxiv,
                "titulo": titulo,
                "autores": autores
            })
        
        await self._publicar_raciocinio(f"Encontrados {len(artigos_encontrados)} artigos recentes.")
        return {"sucesso": True, "artigos": artigos_encontrados}

    async def _gerar_dossie_de_artigo(self, id_arxiv: str) -> Dict[str, Any]:
        """Extrai e sumariza um único artigo para criar um dossiê."""
        await self._publicar_raciocinio(f"Gerando dossiê de inteligência bruta para o artigo '{id_arxiv}'.")
        
        # 1. Obter metadados do artigo
        query = f'id_list={id_arxiv}'
        response = requests.get(self.api_base_url + query)
        if response.status_code != 200:
            return {"sucesso": False, "erro": f"Artigo '{id_arxiv}' não encontrado no arXiv."}

        root = ET.fromstring(response.content)
        namespace = {'arxiv': 'http://www.w3.org/2005/Atom'}
        entry = root.find('arxiv:entry', namespace)
        
        if entry is None:
            return {"sucesso": False, "erro": f"Metadados para '{id_arxiv}' não puderam ser parseados."}

        titulo = entry.find('arxiv:title', namespace).text.strip()
        autores = [author.find('arxiv:name', namespace).text for author in entry.findall('arxiv:author', namespace)]
        resumo = entry.find('arxiv:summary', namespace).text.strip()
        url_pdf = entry.find('arxiv:link', namespace).attrib['href'].replace('/abs/', '/pdf/') + '.pdf'

        # 2. Simular extração de texto do PDF e usar o Cérebro para sumarizar
        # (Em uma implementação real, usaria PyMuPDF para extrair o texto completo)
        texto_completo_simulado = f"Texto completo simulado do artigo '{titulo}'. {resumo}"
        
        prompt_sumarizacao = (
            f"Com base no resumo e no texto do artigo '{titulo}', extraia as seguintes informações:\n"
            "1. Problema Declarado: Qual problema o artigo tenta resolver?\n"
            "2. Metodologia Proposta: Qual é a principal técnica ou abordagem usada?\n"
            "3. Resultados Reivindicados: Quais são os principais resultados ou ganhos de performance alegados?\n"
            "4. Limitações Admitidas: Quais limitações os próprios autores mencionam?\n"
            "Responda em um formato JSON com as chaves: 'problema', 'metodologia', 'resultados', 'limitacoes'."
        )
        
        resposta_sumarizacao = self.cerebro.gerar_pensamento(prompt_sumarizacao)
        sumarizacao_json = json.loads(resposta_sumarizacao)

        dossie = DossieInteligenciaBruta(
            id_arxiv=id_arxiv,
            titulo=titulo,
            autores=autores,
            resumo=resumo,
            problema_declarado=sumarizacao_json.get("problema"),
            metodologia_proposta=sumarizacao_json.get("metodologia"),
            resultados_reivindicados=sumarizacao_json.get("resultados"),
            limitacoes_admitidas=sumarizacao_json.get("limitacoes"),
            url_pdf=url_pdf,
            timestamp_extracao=datetime.now().isoformat()
        )
        
        await self._publicar_raciocinio(f"Dossiê para '{id_arxiv}' gerado.")
        return {"sucesso": True, "dossie": dossie.__dict__}

    async def _publicar_raciocinio(self, pensamento: str):
        await self.barramento.publicar(Evento("EVENTO_RACIOCINIO", {"pensamento": f"🔭 Scholara: {pensamento}"}, self.nome))
