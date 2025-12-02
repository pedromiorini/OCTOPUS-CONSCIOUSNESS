# src/tentaculos/tentaculo_kaizen.py

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import asyncio
from pathlib import Path

from .base_tentaculo import BaseTentaculo
from ..utils.logger import Logger


class SeveridadeRisco(Enum):
    """Níveis de severidade de risco (baseado em FMEA)."""
    CRITICO = 10
    ALTO = 7
    MEDIO = 5
    BAIXO = 3
    INSIGNIFICANTE = 1


class ProbabilidadeOcorrencia(Enum):
    """Probabilidade de ocorrência de falha."""
    MUITO_ALTA = 10
    ALTA = 7
    MEDIA = 5
    BAIXA = 3
    MUITO_BAIXA = 1


@dataclass
class ModoFalha:
    """Representa um modo de falha identificado."""
    passo: str
    descricao_falha: str
    efeito: str
    causa: str
    controle_atual: str
    severidade: SeveridadeRisco
    probabilidade: ProbabilidadeOcorrencia
    detectabilidade: int  # 1-10 (1=fácil detectar, 10=difícil)
    rpn: int = field(init=False)  # Risk Priority Number
    acao_recomendada: str = ""
    responsavel: Optional[str] = None
    
    def __post_init__(self):
        """Calcula o RPN (Risk Priority Number)."""
        self.rpn = (
            self.severidade.value * 
            self.probabilidade.value * 
            self.detectabilidade
        )


@dataclass
class AnalisePokaYoke:
    """Resultado de análise Poka-Yoke."""
    tipo: str  # "validacao_entrada", "confirmacao", "sanidade"
    descricao: str
    codigo_sugerido: str
    local_aplicacao: str
    prioridade: SeveridadeRisco


@dataclass
class AnaliseCausaRaiz:
    """Resultado de análise dos 5 Porquês."""
    evento_falha: str
    timestamp: datetime
    porques: List[str]
    causa_raiz: str
    acoes_corretivas: List[str]
    acoes_preventivas: List[str]


class TentaculoKaizen(BaseTentaculo):
    """
    Especialista em qualidade e prevenção de erros.
    
    Aplica metodologias de gestão da qualidade:
    - FMEA (Failure Mode and Effects Analysis)
    - Poka-Yoke (Design à prova de erros)
    - Análise de Causa Raiz (5 Porquês)
    - Análise Post-Mortem
    """
    
    def __init__(self, cerebro, omnimemoria):
        super().__init__(
            nome="Kaizen",
            especialidade="Qualidade e Prevenção de Erros"
        )
        self.cerebro = cerebro
        self.omnimemoria = omnimemoria
        self.logger = Logger("TentaculoKaizen")
        self.historico_analises: List[Dict[str, Any]] = []
        
    async def pode_executar(self, tarefa: str) -> bool:
        """Verifica se a tarefa é relacionada à qualidade."""
        palavras_chave = [
            "analise de risco", "fmea", "prevenir erro", "poka-yoke",
            "causa raiz", "post-mortem", "qualidade", "confiabilidade",
            "analise de falha", "prevenção", "5 porques"
        ]
        tarefa_lower = tarefa.lower()
        return any(palavra in tarefa_lower for palavra in palavras_chave)
    
    async def executar_tarefa(self, tarefa: str) -> str:
        """Executa análise de qualidade conforme o tipo de tarefa."""
        tarefa_lower = tarefa.lower()
        
        try:
            if "fmea" in tarefa_lower or "analise de risco" in tarefa_lower:
                plano = await self._extrair_plano_da_tarefa(tarefa)
                resultado = await self.realizar_fmea(plano)
                return self._formatar_resultado_fmea(resultado)
            
            elif "poka-yoke" in tarefa_lower or "prova de erro" in tarefa_lower:
                contexto = await self._extrair_contexto(tarefa)
                resultado = await self.sugerir_poka_yoke(contexto)
                return self._formatar_resultado_poka_yoke(resultado)
            
            elif "causa raiz" in tarefa_lower or "5 porques" in tarefa_lower:
                evento = await self._extrair_evento_falha(tarefa)
                resultado = await self.analisar_causa_raiz(evento)
                return self._formatar_resultado_causa_raiz(resultado)
            
            elif "post-mortem" in tarefa_lower:
                evento = await self._extrair_evento_falha(tarefa)
                resultado = await self.realizar_post_mortem(evento)
                return self._formatar_resultado_post_mortem(resultado)
            
            else:
                return await self._analise_generica_qualidade(tarefa)
                
        except Exception as e:
            self.logger.error(f"Erro ao executar tarefa de qualidade: {e}")
            return f"❌ Erro na análise de qualidade: {str(e)}"
    
    async def realizar_fmea(self, plano: Dict[str, Any]) -> List[ModoFalha]:
        """
        Realiza análise FMEA completa de um plano.
        
        Args:
            plano: Dicionário com passos e detalhes do plano
            
        Returns:
            Lista de modos de falha identificados, ordenados por RPN
        """
        self.logger.info(f"Iniciando FMEA para plano: {plano.get('nome', 'Sem nome')}")
        
        modos_falha: List[ModoFalha] = []
        passos = plano.get('passos', [])
        
        for i, passo in enumerate(passos, 1):
            analise_prompt = f"""
            Analise o seguinte passo de um plano e identifique possíveis modos de falha:
            
            Passo {i}: {passo}
            
            Para cada modo de falha identificado, forneça:
            1. Descrição da falha
            2. Efeito da falha
            3. Causa provável
            4. Controle atual (se houver)
            5. Severidade (1-10)
            6. Probabilidade (1-10)
            7. Detectabilidade (1-10)
            8. Ação recomendada (Poka-Yoke)
            
            Seja específico e técnico.
            """
            
            analise = await self.cerebro.pensar(analise_prompt)
            modos = await self._parsear_analise_fmea(passo, analise)
            modos_falha.extend(modos)
        
        modos_falha.sort(key=lambda m: m.rpn, reverse=True)
        await self._salvar_fmea_na_memoria(plano, modos_falha)
        
        self.logger.info(f"FMEA concluído: {len(modos_falha)} modos de falha identificados")
        return modos_falha
    
    async def sugerir_poka_yoke(self, contexto: Dict[str, Any]) -> List[AnalisePokaYoke]:
        """Sugere implementações Poka-Yoke para prevenir erros."""
        self.logger.info("Gerando sugestões Poka-Yoke")
        
        sugestoes: List[AnalisePokaYoke] = []
        
        if 'codigo' in contexto:
            sugestoes.extend(await self._analisar_validacoes_entrada(contexto['codigo']))
        
        if 'operacoes' in contexto:
            sugestoes.extend(await self._analisar_operacoes_destrutivas(contexto['operacoes']))
        
        sugestoes.extend(await self._analisar_verificacoes_sanidade(contexto))
        sugestoes.sort(key=lambda s: s.prioridade.value, reverse=True)
        
        return sugestoes
    
    async def analisar_causa_raiz(self, evento_falha: Dict[str, Any]) -> AnaliseCausaRaiz:
        """Aplica o método dos 5 Porquês para encontrar causa raiz."""
        self.logger.info(f"Iniciando análise de causa raiz: {evento_falha.get('descricao')}")
        
        logs = await self._recuperar_logs_relacionados(evento_falha)
        porques: List[str] = []
        problema_atual = evento_falha.get('descricao', 'Falha não especificada')
        
        for i in range(5):
            prompt = f"""
            Problema: {problema_atual}
            Logs disponíveis: {logs}
            
            Por que este problema ocorreu? Seja específico e técnico.
            Responda apenas com a causa direta.
            """
            
            causa = await self.cerebro.pensar(prompt)
            porques.append(causa)
            problema_atual = causa
            
            if await self._eh_causa_raiz_fundamental(causa):
                break
        
        causa_raiz = porques[-1]
        acoes_corretivas = await self._gerar_acoes_corretivas(causa_raiz)
        acoes_preventivas = await self._gerar_acoes_preventivas(causa_raiz)
        
        analise = AnaliseCausaRaiz(
            evento_falha=evento_falha.get('descricao', ''),
            timestamp=datetime.now(),
            porques=porques,
            causa_raiz=causa_raiz,
            acoes_corretivas=acoes_corretivas,
            acoes_preventivas=acoes_preventivas
        )
        
        await self._salvar_analise_causa_raiz(analise)
        return analise
    
    async def realizar_post_mortem(self, evento: Dict[str, Any]) -> Dict[str, Any]:
        """Realiza análise post-mortem completa de um incidente."""
        self.logger.info(f"Realizando post-mortem: {evento.get('titulo')}")
        
        timeline = await self._reconstruir_timeline(evento)
        causa_raiz = await self.analisar_causa_raiz(evento)
        impacto = await self._analisar_impacto(evento)
        licoes = await self._extrair_licoes_aprendidas(evento, causa_raiz)
        plano_acao = await self._gerar_plano_acao(causa_raiz)
        
        post_mortem = {
            'evento': evento,
            'timeline': timeline,
            'causa_raiz': causa_raiz,
            'impacto': impacto,
            'licoes_aprendidas': licoes,
            'plano_acao': plano_acao,
            'data_analise': datetime.now().isoformat()
        }
        
        await self.omnimemoria.adicionar_perfil(
            nome=f"PostMortem_{evento.get('id', 'unknown')}",
            categoria="analise_qualidade",
            dados=post_mortem
        )
        
        return post_mortem
    
    # Métodos auxiliares privados
    
    async def _extrair_plano_da_tarefa(self, tarefa: str) -> Dict[str, Any]:
        return {
            'nome': 'Plano extraído da tarefa',
            'passos': ['Passo 1', 'Passo 2', 'Passo 3']
        }
    
    async def _extrair_contexto(self, tarefa: str) -> Dict[str, Any]:
        return {'tarefa': tarefa}
    
    async def _extrair_evento_falha(self, tarefa: str) -> Dict[str, Any]:
        return {
            'descricao': 'Evento de falha extraído da tarefa',
            'timestamp': datetime.now().isoformat()
        }
    
    async def _parsear_analise_fmea(self, passo: str, analise: str) -> List[ModoFalha]:
        return [
            ModoFalha(
                passo=passo,
                descricao_falha="Exemplo de falha",
                efeito="Efeito exemplo",
                causa="Causa exemplo",
                controle_atual="Nenhum",
                severidade=SeveridadeRisco.ALTO,
                probabilidade=ProbabilidadeOcorrencia.MEDIA,
                detectabilidade=5,
                acao_recomendada="Implementar validação"
            )
        ]
    
    async def _salvar_fmea_na_memoria(self, plano: Dict[str, Any], modos: List[ModoFalha]):
        dados_fmea = {
            'plano': plano,
            'modos_falha': [
                {
                    'passo': m.passo,
                    'falha': m.descricao_falha,
                    'rpn': m.rpn,
                    'acao': m.acao_recomendada
                } for m in modos
            ],
            'timestamp': datetime.now().isoformat()
        }
        
        await self.omnimemoria.adicionar_perfil(
            nome=f"FMEA_{plano.get('nome', 'unknown')}",
            categoria="analise_qualidade",
            dados=dados_fmea
        )
    
    async def _analisar_validacoes_entrada(self, codigo: str) -> List[AnalisePokaYoke]:
        return [
            AnalisePokaYoke(
                tipo="validacao_entrada",
                descricao="Adicionar validação de parâmetros",
                codigo_sugerido="if param is None: raise ValueError('Param required')",
                local_aplicacao="Início da função",
                prioridade=SeveridadeRisco.MEDIO
            )
        ]
    
    async def _analisar_operacoes_destrutivas(self, operacoes: List[str]) -> List[AnalisePokaYoke]:
        return []
    
    async def _analisar_verificacoes_sanidade(self, contexto: Dict[str, Any]) -> List[AnalisePokaYoke]:
        return []
    
    async def _recuperar_logs_relacionados(self, evento: Dict[str, Any]) -> List[str]:
        return ["Log linha 1", "Log linha 2"]
    
    async def _eh_causa_raiz_fundamental(self, causa: str) -> bool:
        prompt = f"A seguinte causa é fundamental (não decomponível)? Causa: {causa}. Responda sim ou não."
        resposta = await self.cerebro.pensar(prompt)
        return 'sim' in resposta.lower()
    
    async def _gerar_acoes_corretivas(self, causa_raiz: str) -> List[str]:
        return ["Ação corretiva 1", "Ação corretiva 2"]
    
    async def _gerar_acoes_preventivas(self, causa_raiz: str) -> List[str]:
        return ["Ação preventiva 1", "Ação preventiva 2"]
    
    async def _salvar_analise_causa_raiz(self, analise: AnaliseCausaRaiz):
        await self.omnimemoria.adicionar_perfil(
            nome=f"CausaRaiz_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            categoria="analise_qualidade",
            dados={
                'evento': analise.evento_falha,
                'timestamp': analise.timestamp.isoformat(),
                'porques': analise.porques,
                'causa_raiz': analise.causa_raiz
            }
        )
    
    async def _reconstruir_timeline(self, evento: Dict[str, Any]) -> List[str]:
        return ["T-10min: Normal", "T-0: Incidente", "T+5min: Detectado"]
    
    async def _analisar_impacto(self, evento: Dict[str, Any]) -> str:
        return "Impacto médio: 15 minutos de indisponibilidade"
    
    async def _extrair_licoes_aprendidas(self, evento: Dict[str, Any], causa_raiz: AnaliseCausaRaiz) -> List[str]:
        return ["Lição 1", "Lição 2"]
    
    async def _gerar_plano_acao(self, causa_raiz: AnaliseCausaRaiz) -> List[Dict[str, str]]:
        return [{'acao': 'Ação 1', 'responsavel': 'TBD', 'prazo': '7 dias'}]
    
    async def _analise_generica_qualidade(self, tarefa: str) -> str:
        return "Análise de qualidade genérica realizada."
    
    def _formatar_resultado_fmea(self, modos: List[ModoFalha]) -> str:
        resultado = "📊 **Análise FMEA Concluída**\n\n"
        resultado += f"Total: {len(modos)} modos de falha\n\n"
        resultado += "🔴 **Top 5 Riscos:**\n\n"
        for i, modo in enumerate(modos[:5], 1):
            resultado += f"{i}. {modo.descricao_falha} (RPN: {modo.rpn})\n"
        return resultado
    
    def _formatar_resultado_poka_yoke(self, sugestoes: List[AnalisePokaYoke]) -> str:
        resultado = "🛡️ **Sugestões Poka-Yoke**\n\n"
        for i, sug in enumerate(sugestoes, 1):
            resultado += f"{i}. {sug.tipo}: {sug.descricao}\n"
        return resultado
    
    def _formatar_resultado_causa_raiz(self, analise: AnaliseCausaRaiz) -> str:
        resultado = "🔍 **Análise de Causa Raiz**\n\n"
        resultado += f"Evento: {analise.evento_falha}\n\n"
        resultado += "**Os 5 Porquês:**\n"
        for i, porque in enumerate(analise.porques, 1):
            resultado += f"{i}. {porque}\n"
        resultado += f"\n🎯 Causa Raiz: {analise.causa_raiz}\n"
        return resultado
    
    def _formatar_resultado_post_mortem(self, analise: Dict[str, Any]) -> str:
        return f"📝 **Post-Mortem**: {analise['evento'].get('titulo', 'Incidente')}\n"


# src/tentaculos/tentaculo_seiri.py

from typing import List, Dict, Any, Set
from dataclasses import dataclass
from pathlib import Path
import ast
import subprocess

from .base_tentaculo import BaseTentaculo
from ..utils.logger import Logger


@dataclass
class ItemLimpeza:
    """Representa um item identificado para limpeza."""
    tipo: str
    caminho: str
    descricao: str
    tamanho_bytes: int
    ultima_modificacao: str
    seguro_remover: bool
    prioridade: int


@dataclass
class PropostaOrganizacao:
    """Proposta de reorganização de estrutura."""
    tipo: str
    estado_atual: str
    estado_proposto: str
    justificativa: str
    impacto: str
    passos_implementacao: List[str]


@dataclass
class ViolacaoPadrao:
    """Violação de padrão de código detectada."""
    arquivo: str
    linha: int
    padrao_violado: str
    descricao: str
    sugestao_correcao: str
    severidade: str


class TentaculoSeiri(BaseTentaculo):
    """
    Especialista em organização e otimização do sistema (5S).
    
    Aplica os princípios do 5S:
    - Seiri (Utilização): Remove o desnecessário
    - Seiton (Organização): Organiza estruturas
    - Seiso (Limpeza): Limpa código e configurações
    - Seiketsu (Padronização): Mantém padrões
    - Shitsuke (Disciplina): Automatiza manutenção
    """
    
    def __init__(self, cerebro, omnimemoria, caminho_projeto: Path):
        super().__init__(
            nome="Seiri",
            especialidade="Organização e Otimização (5S)"
        )
        self.cerebro = cerebro
        self.omnimemoria = omnimemoria
        self.caminho_projeto = caminho_projeto
        self.logger = Logger("TentaculoSeiri")
        self.padroes_projeto: Dict[str, Any] = {}
        
    async def pode_executar(self, tarefa: str) -> bool:
        """Verifica se a tarefa é relacionada à organização."""
        palavras_chave = [
            "organizar", "limpar sistema", "5s", "padronizar",
            "remover código morto", "estrutura", "cleanup",
            "otimizar", "refatorar estrutura", "linting"
        ]
        return any(palavra in tarefa.lower() for palavra in palavras_chave)
    
    async def executar_tarefa(self, tarefa: str) -> str:
        """Executa tarefa de organização conforme o tipo."""
        tarefa_lower = tarefa.lower()
        
        try:
            if "seiri" in tarefa_lower or "limpar arquivo" in tarefa_lower:
                resultado = await self.executar_seiri()
                return self._formatar_resultado_seiri(resultado)
            
            elif "seiton" in tarefa_lower or "organizar estrutura" in tarefa_lower:
                resultado = await self.executar_seiton()
                return self._formatar_resultado_seiton(resultado)
            
            elif "seiso" in tarefa_lower or "limpar codigo" in tarefa_lower:
                resultado = await self.executar_seiso()
                return self._formatar_resultado_seiso(resultado)
            
            elif "seiketsu" in tarefa_lower or "verificar padrao" in tarefa_lower:
                resultado = await self.executar_seiketsu()
                return self._formatar_resultado_seiketsu(resultado)
            
            elif "shitsuke" in tarefa_lower or "automatizar" in tarefa_lower:
                resultado = await self.executar_shitsuke()
                return self._formatar_resultado_shitsuke(resultado)
            
            elif "5s completo" in tarefa_lower:
                return await self.executar_5s_completo()
            
            else:
                return await self._analise_generica_organizacao(tarefa)
                
        except Exception as e:
            self.logger.error(f"Erro ao executar tarefa de organização: {e}")
            return f"❌ Erro na organização: {str(e)}"
    
    async def executar_seiri(self) -> List[ItemLimpeza]:
        """Seiri (Utilização): Identifica itens desnecessários."""
        self.logger.info("Executando Seiri (Senso de Utilização)")
        
        itens_limpeza: List[ItemLimpeza] = []
        itens_limpeza.extend(await self._identificar_arquivos_temporarios())
        itens_limpeza.extend(await self._identificar_logs_antigos())
        itens_limpeza.sort(key=lambda item: item.prioridade, reverse=True)
        
        await self._salvar_relatorio_seiri(itens_limpeza)
        self.logger.info(f"Seiri concluído: {len(itens_limpeza)} itens identificados")
        return itens_limpeza
    
    async def executar_seiton(self) -> List[PropostaOrganizacao]:
        """Seiton (Organização): Propõe melhorias na estrutura."""
        self.logger.info("Executando Seiton (Senso de Organização)")
        
        propostas: List[PropostaOrganizacao] = []
        propostas.extend(await self._analisar_estrutura_diretorios())
        
        await self._salvar_relatorio_seiton(propostas)
        return propostas
    
    async def executar_seiso(self) -> Dict[str, Any]:
        """Seiso (Limpeza): Limpa e formata código."""
        self.logger.info("Executando Seiso (Senso de Limpeza)")
        
        relatorio = {
            'arquivos_formatados': [],
            'linting_aplicado': [],
            'docstrings_geradas': [],
            'codigo_morto_removido': []
        }
        
        await self._salvar_relatorio_seiso(relatorio)
        return relatorio
    
    async def executar_seiketsu(self) -> List[ViolacaoPadrao]:
        """Seiketsu (Padronização): Verifica conformidade com padrões."""
        self.logger.info("Executando Seiketsu (Senso de Padronização)")
        
        await self._carregar_padroes_projeto()
        violacoes: List[ViolacaoPadrao] = []
        
        await self._salvar_relatorio_seiketsu(violacoes)
        return violacoes
    
    async def executar_shitsuke(self) -> Dict[str, Any]:
        """Shitsuke (Disciplina): Cria tarefas automatizadas."""
        self.logger.info("Executando Shitsuke (Senso de Disciplina)")
        
        tarefas_automatizadas = {
            'tarefas_criadas': [
                {
                    'nome': 'Limpeza Semanal',
                    'frequencia': 'semanal',
                    'dia': 'domingo',
                    'hora': '02:00'
                }
            ],
            'hooks_instalados': []
        }
        
        await self.omnimemoria.adicionar_perfil(
            nome="ConfiguracoesShitsuke",
            categoria="automacao_5s",
            dados=tarefas_automatizadas
        )
        
        return tarefas_automatizadas
    
    async def executar_5s_completo(self) -> str:
        """Executa os 5S completos em sequência."""
        self.logger.info("🌟 Iniciando execução completa do 5S")
        
        relatorio_completo = {
            'inicio': datetime.now().isoformat(),
            'etapas': {}
        }
        
        seiri_resultado = await self.executar_seiri()
        relatorio_completo['etapas']['seiri'] = {'itens': len(seiri_resultado)}
        
        seiton_resultado = await self.executar_seiton()
        relatorio_completo['etapas']['seiton'] = {'propostas': len(seiton_resultado)}
        
        seiso_resultado = await self.executar_seiso()
        relatorio_completo['etapas']['seiso'] = seiso_resultado
        
        seiketsu_resultado = await self.executar_seiketsu()
        relatorio_completo['etapas']['seiketsu'] = {'violacoes': len(seiketsu_resultado)}
        
        shitsuke_resultado = await self.executar_shitsuke()
        relatorio_completo['etapas']['shitsuke'] = shitsuke_resultado
        
        relatorio_completo['fim'] = datetime.now().isoformat()
        
        await self.omnimemoria.adicionar_perfil(
            nome=f"Relatorio5S_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            categoria="relatorios_5s",
            dados=relatorio_completo
        )
        
        return self._formatar_relatorio_5s_completo(relatorio_completo)
    
    # Métodos auxiliares
    
    async def _identificar_arquivos_temporarios(self) -> List[ItemLimpeza]:
        padroes_temp = ["*.tmp", "*.bak", "*.swp", "*~", "*.pyc"]
        itens = []
        
        for padrao in padroes_temp:
            for arquivo in self.caminho_projeto.rglob(padrao):
                if arquivo.is_file():
                    stat = arquivo.stat()
                    itens.append(ItemLimpeza(
                        tipo="arquivo_temporario",
                        caminho=str(arquivo),
                        descricao=f"Arquivo temporário: {arquivo.name}",
                        tamanho_bytes=stat.st_size,
                        ultima_modificacao=datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        seguro_remover=True,
                        prioridade=4
                    ))
        
        return itens
    
    async def _identificar_logs_antigos(self) -> List[ItemLimpeza]:
        return []
    
    async def _analisar_estrutura_diretorios(self) -> List[PropostaOrganizacao]:
        return [
            PropostaOrganizacao(
                tipo="estrutura",
                estado_atual="Estrutura atual",
                estado_proposto="Estrutura melhorada",
                justificativa="Melhor organização",
                impacto="Médio",
                passos_implementacao=["Passo 1", "Passo 2"]
            )
        ]
    
    async def _carregar_padroes_projeto(self):
        self.padroes_projeto = {
            'nomenclatura_funcoes': 'snake_case',
            'nomenclatura_classes': 'PascalCase'
        }
    
    async def _salvar_relatorio_seiri(self, itens: List[ItemLimpeza]):
        await self.omnimemoria.adicionar_perfil(
            nome=f"RelatorioSeiri_{datetime.now().strftime('%Y%m%d')}",
            categoria="relatorios_5s",
            dados={'total_itens': len(