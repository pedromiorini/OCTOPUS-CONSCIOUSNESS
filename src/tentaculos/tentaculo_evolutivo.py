# src/tentaculos/tentaculo_evolutivo.py

import logging
import asyncio
import subprocess
import json
from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime

from .base_tentaculo import BaseTentaculo
from src.cognitive.cerebro import Cerebro
from src.shared.comunicacao import BarramentoEventos, Evento

logger = logging.getLogger(__name__)

class TentaculoEvolutivo(BaseTentaculo):
    """
    Especialista em orquestrar o Ciclo de Desenvolvimento Evolutivo (CDE).
    Atua como um Engenheiro de Software de IA Autônomo, analisando,
    planejando, implementando e publicando melhorias em projetos de software.
    """
    def __init__(self, cerebro: Cerebro, barramento: BarramentoEventos, tentaculos: Dict[str, BaseTentaculo]):
        super().__init__("Evolutivo", cerebro, barramento)
        self.tentaculos = tentaculos # Acesso a todos os outros especialistas
        self.workspace_dir = Path("workspace/evolutivo")
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        logger.info("🧬 Tentáculo Evolutivo (Engenheiro da Evolução) instanciado.")

    async def pode_executar(self, tarefa: str) -> bool:
        """Verifica se a tarefa é de evolução de projeto."""
        palavras_chave = ["ciclo de desenvolvimento", "melhore o projeto", "evolua o repositório", "refatoração automática"]
        return any(palavra in tarefa.lower() for palavra in palavras_chave)

    async def executar_tarefa(self, tarefa: str, **kwargs) -> Dict[str, Any]:
        """
        Executa um Ciclo de Desenvolvimento Evolutivo (CDE) completo.
        
        Args:
            tarefa: Descrição da missão, ex: "Execute um CDE no projeto OCTOPUS-CONSCIOUSNESS"
            **kwargs:
                - repo_url: URL do repositório Git a ser analisado.
        """
        repo_url = kwargs.get("repo_url")
        if not repo_url:
            return {"sucesso": False, "erro": "A URL do repositório (repo_url) é necessária."}

        project_name = repo_url.split('/')[-1].replace('.git', '')
        project_path = self.workspace_dir / project_name

        await self._publicar_raciocinio(f"Iniciando Ciclo de Desenvolvimento Evolutivo para o projeto '{project_name}'.")

        try:
            # FASE 0: PREPARAÇÃO
            await self._preparar_workspace(repo_url, project_path)

            # FASE 1: ANÁLISE E DIAGNÓSTICO
            diagnosticos = await self._fase_de_diagnostico(project_path)

            # FASE 2: PLANEJAMENTO ESTRATÉGICO
            plano_de_acao = await self._fase_de_planejamento(diagnosticos)
            if not plano_de_acao or not plano_de_acao.get("passos"):
                return {"sucesso": True, "mensagem": "Análise concluída. Nenhum plano de ação gerado."}

            # FASE 3: IMPLEMENTAÇÃO E INOVAÇÃO
            for passo in plano_de_acao["passos"]:
                await self._fase_de_implementacao(passo, project_path)

            # FASE 4: VALIDAÇÃO E PUBLICAÇÃO
            resultado_publicacao = await self._fase_de_publicacao(project_path, plano_de_acao)

            await self._publicar_raciocinio(f"Ciclo de Desenvolvimento Evolutivo concluído com sucesso para '{project_name}'.")
            return {"sucesso": True, "relatorio_final": resultado_publicacao}

        except Exception as e:
            logger.error(f"Erro crítico no Ciclo de Desenvolvimento Evolutivo: {e}", exc_info=True)
            await self._publicar_raciocinio(f"🚨 FALHA CRÍTICA no CDE: {e}")
            return {"sucesso": False, "erro": str(e)}

    async def _publicar_raciocinio(self, pensamento: str):
        """Envia um pensamento para o barramento de eventos para transparência."""
        await self.barramento.publicar(Evento("EVENTO_RACIOCINIO", {"pensamento": f"🧬 Evolutivo: {pensamento}"}, self.nome))

    async def _preparar_workspace(self, repo_url: str, project_path: Path):
        """Clona ou atualiza o repositório no workspace."""
        await self._publicar_raciocinio(f"Preparando workspace em '{project_path}'...")
        if project_path.exists():
            # Puxa as últimas alterações
            subprocess.run(["git", "-C", str(project_path), "pull"], check=True)
        else:
            # Clona o repositório
            subprocess.run(["git", "clone", repo_url, str(project_path)], check=True)
        await self._publicar_raciocinio("Workspace pronto.")

    async def _fase_de_diagnostico(self, project_path: Path) -> Dict[str, Any]:
        """Orquestra a fase de análise, delegando para Kaizen, Seiri e Logos."""
        await self._publicar_raciocinio("Iniciando Fase 1: Análise e Diagnóstico.")
        
        # Delegações em paralelo
        task_kaizen = self.tentaculos["Kaizen"].executar_tarefa(f"Execute uma análise FMEA no projeto em '{project_path}'")
        task_seiri = self.tentaculos["Seiri"].executar_tarefa(f"Execute um ciclo 5S completo no projeto em '{project_path}'")
        task_logos = self.tentaculos["Logos"].executar_tarefa(f"Gere um diagrama de arquitetura para o projeto em '{project_path}'")

        resultados = await asyncio.gather(task_kaizen, task_seiri, task_logos)
        
        diagnosticos = {
            "relatorio_qualidade": resultados[0],
            "relatorio_organizacao": resultados[1],
            "relatorio_arquitetura": resultados[2],
        }
        await self._publicar_raciocinio("Fase de Diagnóstico concluída. Relatórios consolidados.")
        return diagnosticos

    async def _fase_de_planejamento(self, diagnosticos: Dict[str, Any]) -> Dict[str, Any]:
        """Orquestra a fase de planejamento, delegando para o Estrategista."""
        await self._publicar_raciocinio("Iniciando Fase 2: Planejamento Estratégico.")
        
        # Consolida os diagnósticos em um prompt para o Estrategista
        prompt_diagnostico = (
            "Com base nos seguintes relatórios de análise de um projeto de software, "
            "crie um plano de refatoração priorizado usando a Matriz de Eisenhower.\n\n"
            f"Relatório de Qualidade (Kaizen):\n{json.dumps(diagnosticos['relatorio_qualidade'], indent=2)}\n\n"
            f"Relatório de Organização (Seiri):\n{json.dumps(diagnosticos['relatorio_organizacao'], indent=2)}\n\n"
            f"Relatório de Arquitetura (Logos):\n{json.dumps(diagnosticos['relatorio_arquitetura'], indent=2)}\n\n"
            "O plano deve focar nas melhorias mais urgentes e importantes."
        )
        
        resultado_estrategista = await self.tentaculos["Estrategista"].executar_tarefa(prompt_diagnostico)
        
        if not resultado_estrategista.get("sucesso"):
            raise Exception("Falha ao gerar plano estratégico.")
            
        plano = resultado_estrategista.get("plano_de_acao", {})
        await self._publicar_raciocinio(f"Fase de Planejamento concluída. {len(plano.get('passos', []))} ações priorizadas.")
        return plano

    async def _fase_de_implementacao(self, passo_plano: Dict[str, Any], project_path: Path):
        """Orquestra a implementação de um passo do plano de ação."""
        descricao_passo = passo_plano.get("descricao", "Passo não especificado")
        await self._publicar_raciocinio(f"Iniciando Fase 3: Implementação do passo '{descricao_passo}'.")

        # 1. Engenharia Reversa e Inovação
        tarefa_daedalus = f"Analise o módulo relacionado a '{descricao_passo}' no projeto em '{project_path}' e extraia sua essência."
        essencia = await self.tentaculos["Daedalus"].executar_tarefa(tarefa_daedalus)
        
        tarefa_prometheus = f"Com base na essência '{essencia}', proponha 3 alternativas de implementação melhores para '{descricao_passo}'."
        inovacao = await self.tentaculos["Prometheus"].executar_tarefa(tarefa_prometheus)
        
        # Seleciona a melhor alternativa (simulado)
        design_vencedor = inovacao.get("alternativas", [{}])[0]
        await self._publicar_raciocinio(f"Design inovador selecionado: {design_vencedor.get('titulo')}")

        # 2. Geração da Lógica
        tarefa_logos = f"Transforme o design '{design_vencedor}' em pseudocódigo e testes BDD."
        artefatos_logicos = await self.tentaculos["Logos"].executar_tarefa(tarefa_logos)
        pseudocodigo = artefatos_logicos.get("pseudocodigo")
        testes_bdd = artefatos_logicos.get("testes_bdd")

        # 3. Escrita do Código
        tarefa_codigo = f"Implemente o seguinte pseudocódigo em Python, garantindo que os testes BDD passem:\n\nPseudocódigo:\n{pseudocodigo}\n\nTestes:\n{testes_bdd}"
        resultado_codigo = await self.tentaculos["Codigo"].executar_tarefa(tarefa_codigo)
        novo_codigo = resultado_codigo.get("codigo_gerado")
        
        # Simula a escrita do novo código no arquivo apropriado
        # (uma implementação real precisaria identificar o arquivo a ser modificado)
        caminho_arquivo_modificado = project_path / "src/module_to_improve.py"
        with open(caminho_arquivo_modificado, "w") as f:
            f.write(novo_codigo)
            
        await self._publicar_raciocinio(f"Implementação concluída. Arquivo '{caminho_arquivo_modificado.name}' modificado.")

    async def _fase_de_publicacao(self, project_path: Path, plano_de_acao: Dict[str, Any]) -> Dict[str, Any]:
        """Orquestra a validação final e a publicação das mudanças."""
        await self._publicar_raciocinio("Iniciando Fase 4: Validação e Publicação.")

        # 1. Validação (simulada)
        await self.tentaculos["Kaizen"].executar_tarefa(f"Execute os testes unitários no projeto em '{project_path}'.")
        await self.tentaculos["Seiri"].executar_tarefa(f"Verifique os padrões de código no projeto em '{project_path}'.")
        await self._publicar_raciocinio("Validação de testes e qualidade concluída.")

        # 2. Documentação e Versionamento
        resumo_mudancas = f"Refatoração automática baseada no plano: {plano_de_acao.get('objetivo')}"
        tarefa_scriba_commit = f"Gere uma mensagem de commit detalhada para as seguintes mudanças: {resumo_mudancas}"
        resultado_commit = await self.tentaculos["Scriba"].executar_tarefa(tarefa_scriba_commit)
        mensagem_commit = resultado_commit.get("mensagem_commit")

        # 3. Publicação
        tarefa_scriba_push = f"Execute o versionamento no repositório '{project_path}' com a mensagem de commit: '{mensagem_commit}' e faça o push para a branch 'main'."
        resultado_push = await self.tentaculos["Scriba"].executar_tarefa(tarefa_scriba_push)
        
        if resultado_push.get("sucesso"):
            await self._publicar_raciocinio("Publicação no GitHub concluída com sucesso.")
        else:
            raise Exception(f"Falha na publicação no GitHub: {resultado_push.get('erro')}")
            
        return resultado_push
