# OCTOPUS-CONSCIOUSNESS/src/tentaculos/estrategista/frameworks.py

from abc import ABC, abstractmethod
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class FrameworkEstrategico(ABC):
    """Classe base abstrata para todos os frameworks de pensamento estratégico."""
    
    @property
    @abstractmethod
    def nome(self) -> str:
        """Nome do framework."""
        pass

    @property
    @abstractmethod
    def descricao(self) -> str:
        """Descrição do framework e seu propósito."""
        pass

    @abstractmethod
    def aplicar(self, contexto: Dict[str, Any]) -> Dict[str, Any]:
        """Aplica o framework ao contexto fornecido e retorna a análise."""
        pass

class FrameworkSWOT(FrameworkEstrategico):
    nome = "Análise SWOT"
    descricao = "Identifica Forças (Strengths), Fraquezas (Weaknesses), Oportunidades (Opportunities) e Ameaças (Threats) para planejamento estratégico."

    def aplicar(self, contexto: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"Aplicando {self.nome} ao contexto.")
        # Simulação de análise
        analise = {
            "Forças": ["Modularidade v2.0", "Arquitetura bio-inspirada"],
            "Fraquezas": ["Dependência de token de acesso", "Complexidade de orquestração"],
            "Oportunidades": ["Expansão para novos tentáculos", "Integração com novas APIs"],
            "Ameaças": ["Limites de contexto", "Evolução rápida de modelos de IA"]
        }
        return {"SWOT_Analysis": analise}

class Framework5Whys(FrameworkEstrategico):
    nome = "5 Porquês (5 Whys)"
    descricao = "Método de análise de causa raiz para identificar a causa fundamental de um problema."

    def aplicar(self, contexto: Dict[str, Any]) -> Dict[str, Any]:
        problema = contexto.get("problema", "Problema não especificado.")
        logger.info(f"Aplicando {self.nome} para: {problema}")
        # Simulação de análise
        analise = {
            "Problema Inicial": problema,
            "Por que 1": "Porque a causa raiz não foi identificada.",
            "Por que 2": "Porque a análise inicial foi superficial.",
            "Por que 3": "Porque o tentáculo Perceptivo não forneceu dados suficientes.",
            "Por que 4": "Porque o modelo do Perceptivo não estava treinado para o contexto.",
            "Por que 5 (Causa Raiz)": "A base de conhecimento do Perceptivo precisa de atualização contínua."
        }
        return {"5_Whys_Analysis": analise}

class FrameworkEisenhower(FrameworkEstrategico):
    nome = "Matriz de Eisenhower"
    descricao = "Prioriza tarefas com base em Urgência e Importância (Urgente/Não Urgente, Importante/Não Importante)."

    def aplicar(self, contexto: Dict[str, Any]) -> Dict[str, Any]:
        tarefas = contexto.get("tarefas", [])
        logger.info(f"Aplicando {self.nome} para {len(tarefas)} tarefas.")
        
        priorizacao = {
            "Fazer Imediatamente (Urgente e Importante)": [],
            "Agendar (Não Urgente e Importante)": [],
            "Delegar (Urgente e Não Importante)": [],
            "Eliminar (Não Urgente e Não Importante)": []
        }
        
        # Simulação de priorização
        for i, tarefa in enumerate(tarefas):
            if i % 4 == 0:
                priorizacao["Fazer Imediatamente (Urgente e Importante)"].append(tarefa)
            elif i % 4 == 1:
                priorizacao["Agendar (Não Urgente e Importante)"].append(tarefa)
            elif i % 4 == 2:
                priorizacao["Delegar (Urgente e Não Importante)"].append(tarefa)
            else:
                priorizacao["Eliminar (Não Urgente e Não Importante)"].append(tarefa)

        return {"Eisenhower_Matrix": priorizacao}

class FrameworkReversePlanning(FrameworkEstrategico):
    nome = "Planejamento Reverso"
    descricao = "Começa com o objetivo final e trabalha retroativamente para definir os passos necessários."

    def aplicar(self, contexto: Dict[str, Any]) -> Dict[str, Any]:
        objetivo = contexto.get("objetivo", "Objetivo final não especificado.")
        logger.info(f"Aplicando {self.nome} para o objetivo: {objetivo}")
        
        # Simulação de planejamento reverso
        passos_reversos = [
            "Passo 0: Objetivo Alcançado",
            "Passo -1: Executar o último passo do plano",
            "Passo -2: Garantir que todos os recursos estejam prontos",
            "Passo -3: Definir o plano de ação inicial"
        ]
        
        return {"Reverse_Planning_Steps": passos_reversos}

def get_all_frameworks() -> Dict[str, FrameworkEstrategico]:
    """Retorna um dicionário de todos os frameworks disponíveis."""
    return {
        "SWOT": FrameworkSWOT(),
        "5Whys": Framework5Whys(),
        "Eisenhower": FrameworkEisenhower(),
        "ReversePlanning": FrameworkReversePlanning()
    }
