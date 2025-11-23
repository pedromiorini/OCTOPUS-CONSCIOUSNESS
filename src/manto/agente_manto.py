# src/manto/agente_manto.py
import time
from typing import List, Dict

class Manto:
    """
    A Consciência Central (Manto) que planeja, decompõe e orquestra
    os agentes especialistas (Tentáculos).
    """
    def __init__(self, rede_tentaculos: 'RedeDeTentaculos'):
        self.rede_tentaculos = rede_tentaculos
        print("🐙 Manto (Consciência Central) ativado e pronto para estrategizar.")

    def decompor_e_orquestrar(self, objetivo_macro: str):
        """
        Recebe um objetivo de alto nível, decompõe em um plano de ação
        e orquestra a execução pelos tentáculos.
        """
        print(f"\n🎯 Objetivo Macro recebido: '{objetivo_macro}'")
        
        # Etapa 1: Decomposição do objetivo (simulada para este exemplo)
        print("🧠 Decompondo o objetivo em um plano estratégico...")
        plano = [
            {"id_tarefa": "T1", "descricao": "Pesquisar na web por 'frameworks de IA autônoma de código aberto'."},
            {"id_tarefa": "T2", "descricao": "Analisar o código do framework mais promissor encontrado."},
            {"id_tarefa": "T3", "descricao": "Gerar um relatório de síntese com os prós e contras."}
        ]
        time.sleep(1)
        print(f"🗺️ Plano gerado com {len(plano)} etapas.")

        # Etapa 2: Orquestração sequencial do plano
        resultados_finais = {}
        for tarefa in plano:
            print(f"\n---\n🚀 Iniciando etapa: '{tarefa['descricao']}'")
            
            # Etapa 3: Emissão do Token de Missão
            token_missao = tarefa
            print(f"📡 Emitindo Token de Missão: {token_missao['id_tarefa']}")
            
            # Etapa 4: Coleta de Propostas de Prontidão dos tentáculos
            propostas = self.rede_tentaculos.broadcast(token_missao)
            print(f"📩 Propostas de prontidão recebidas de {len(propostas)} tentáculos.")
            
            if not propostas:
                print(f"❌ Nenhum tentáculo disponível para a tarefa '{tarefa['id_tarefa']}'. Abortando etapa.")
                continue
                
            # Etapa 5: Seleção Estratégica (escolhe o de maior confiança)
            melhor_proposta = max(propostas, key=lambda p: p['confianca'])
            id_tentaculo_escolhido = melhor_proposta['id_tentaculo']
            print(f"🏆 Tentáculo #{id_tentaculo_escolhido} ('{melhor_proposta['habilidade']}') foi selecionado com confiança {melhor_proposta['confianca']:.2f}.")
            
            # Etapa 6: Autorização e Execução da Missão
            resultado = self.rede_tentaculos.executar_missao(id_tentaculo_escolhido, token_missao)
            resultados_finais[tarefa['id_tarefa']] = resultado
            print(f"✅ Missão {token_missao['id_tarefa']} concluída. Resultado: '{resultado}'")
        
        # Etapa 7: Síntese Final
        print("\n---\n🎉 Plano estratégico concluído! Sintetizando resultados...")
        sintese = f"Relatório Final: A pesquisa indicou que os frameworks mais citados são '{resultados_finais.get('T1', 'N/A')}'. A análise do código revelou '{resultados_finais.get('T2', 'N/A')}'."
        print(sintese)

class RedeDeTentaculos:
    """
    Simula o sistema nervoso: um barramento de comunicação que conecta
    o Manto aos Tentáculos.
    """
    def __init__(self, tentaculos: List['BaseTentaculo']):
        self.tentaculos = {t.id: t for t in tentaculos}

    def broadcast(self, token_missao: Dict) -> List[Dict]:
        """Envia o token para todos os tentáculos e coleta propostas."""
        propostas = []
        for tentaculo in self.tentaculos.values():
            if tentaculo.pode_executar(token_missao):
                propostas.append(tentaculo.gerar_proposta(token_missao))
        return propostas
    
    def executar_missao(self, id_tentaculo: int, token_missao: Dict) -> str:
        """Autoriza um tentáculo específico a executar a missão."""
        if id_tentaculo in self.tentaculos:
            return self.tentaculos[id_tentaculo].executar(token_missao)
        return "Erro: Tentáculo não encontrado."
