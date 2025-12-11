# src/tentaculos/tentaculo_omni_memoria.py

import logging
import asyncio
import json
from typing import Dict, Any, List, Optional, Set
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

from .base_tentaculo import BaseTentaculo
from src.cognitive.cerebro import Cerebro
from src.shared.comunicacao import BarramentoEventos

logger = logging.getLogger(__name__)


class TipoMemoria(Enum):
    """Tipos de memória no sistema O-Mem."""
    PERSONA = "persona"
    TRABALHO = "trabalho"
    EPISODICA = "episodica"


@dataclass
class EventoVida:
    """Representa um evento significativo na vida do usuário."""
    data: str
    evento: str
    importancia: float  # 0.0 a 1.0
    contexto: Optional[str] = None
    turno: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AtributoPersona:
    """Atributo com metadata para rastreamento."""
    valor: Any
    confianca: float  # 0.0 a 1.0
    primeira_mencao: int  # turno
    ultima_atualizacao: int  # turno
    frequencia: int = 1  # quantas vezes foi mencionado

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class MemoriaPersona:
    """Memória de longo prazo com perfil rico da entidade."""
    
    def __init__(self, entidade_id: str):
        self.entidade_id = entidade_id
        self.atributos: Dict[str, AtributoPersona] = {}
        self.tracos_personalidade: Dict[str, float] = {}
        self.eventos_vida: List[EventoVida] = []
        self.preferencias: Dict[str, Any] = {}
        self.metadata = {
            "criado_em": datetime.now().isoformat(),
            "total_interacoes": 0,
            "ultima_atualizacao": None
        }

    def atualizar_atributo(self, chave: str, valor: Any, confianca: float, turno: int):
        """Atualiza ou cria um atributo com fusão inteligente."""
        if chave in self.atributos:
            atributo = self.atributos[chave]
            # Fusão ponderada baseada em confiança
            if confianca > atributo.confianca:
                atributo.valor = valor
                atributo.confianca = confianca
            atributo.frequencia += 1
            atributo.ultima_atualizacao = turno
        else:
            self.atributos[chave] = AtributoPersona(
                valor=valor,
                confianca=confianca,
                primeira_mencao=turno,
                ultima_atualizacao=turno
            )

    def adicionar_evento(self, evento: EventoVida):
        """Adiciona evento mantendo ordenação temporal."""
        self.eventos_vida.append(evento)
        self.eventos_vida.sort(key=lambda e: e.data, reverse=True)
        # Manter apenas eventos mais relevantes (top 50)
        if len(self.eventos_vida) > 50:
            self.eventos_vida = sorted(
                self.eventos_vida,
                key=lambda e: e.importancia,
                reverse=True
            )[:50]

    def to_dict(self) -> Dict[str, Any]:
        """Serializa para persistência."""
        return {
            "entidade_id": self.entidade_id,
            "atributos": {k: v.to_dict() for k, v in self.atributos.items()},
            "tracos_personalidade": self.tracos_personalidade,
            "eventos_vida": [e.to_dict() for e in self.eventos_vida],
            "preferencias": self.preferencias,
            "metadata": self.metadata
        }


class MemoriaTrabalho:
    """Memória de curto prazo para conversação recente."""
    
    def __init__(self, max_topicos: int = 20):
        self.max_topicos = max_topicos
        self.topicos: Dict[str, List[int]] = {}
        self.resumo_ultimos_turnos: List[str] = []

    def adicionar_topico(self, topico: str, turno: int):
        """Adiciona tópico com gerenciamento de capacidade."""
        if topico not in self.topicos:
            self.topicos[topico] = []
        self.topicos[topico].append(turno)
        
        # Limpar tópicos antigos se exceder capacidade
        if len(self.topicos) > self.max_topicos:
            topico_mais_antigo = min(self.topicos.items(), key=lambda x: x[1][-1])
            del self.topicos[topico_mais_antigo[0]]

    def obter_topicos_recentes(self, n: int = 5) -> List[str]:
        """Retorna os N tópicos mais recentes."""
        topicos_ordenados = sorted(
            self.topicos.items(),
            key=lambda x: x[1][-1],
            reverse=True
        )
        return [t[0] for t in topicos_ordenados[:n]]


class MemoriaEpisodica:
    """Memória baseada em pistas para recuperação precisa."""
    
    def __init__(self, limiar_raridade: int = 3):
        self.limiar_raridade = limiar_raridade
        self.pistas: Dict[str, List[int]] = {}  # pista -> lista de turnos
        self.frequencia_global: Dict[str, int] = {}

    def indexar_pista(self, pista: str, turno: int, conteudo: str):
        """Indexa pista se for rara o suficiente."""
        # Atualizar frequência global
        self.frequencia_global[pista] = self.frequencia_global.get(pista, 0) + 1
        
        # Indexar apenas se for rara
        if self.frequencia_global[pista] <= self.limiar_raridade:
            if pista not in self.pistas:
                self.pistas[pista] = []
            self.pistas[pista].append(turno)

    def buscar_por_pista(self, termo: str) -> Optional[List[int]]:
        """Busca turnos onde a pista apareceu."""
        return self.pistas.get(termo.lower())


class TentaculoOmniMemoria(BaseTentaculo):
    """
    Especialista em memória omni-dimensional, inspirado na arquitetura O-Mem.
    Implementa memória de persona, trabalho e episódica para personalização profunda.
    """
    
    def __init__(self, cerebro: Cerebro, barramento: BarramentoEventos):
        super().__init__("OmniMemoria", cerebro, barramento)
        
        # Sistema multi-entidade
        self.personas: Dict[str, MemoriaPersona] = {}
        self.memoria_trabalho = MemoriaTrabalho()
        self.memoria_episodica = MemoriaEpisodica()
        
        # Histórico completo para referência
        self.historico_turnos: List[Dict[str, Any]] = []
        self.contador_turnos = 0
        
        # Cache para otimização
        self._cache_contexto: Dict[str, tuple[str, int]] = {}
        self._cache_ttl = 5  # turnos
        
        logger.info("🧠 Tentáculo OmniMemoria (O-Mem) instanciado com sistema multi-entidade.")

    async def pode_executar(self, tarefa: str) -> bool:
        """Verifica se a tarefa é relacionada à memória."""
        palavras_chave = [
            "lembrar", "contexto", "atualizar perfil", "processar mensagem",
            "recuperar", "memoria", "histórico", "perfil", "personalizar"
        ]
        tarefa_lower = tarefa.lower()
        return any(palavra in tarefa_lower for palavra in palavras_chave)

    async def executar_tarefa(self, tarefa: str) -> Any:
        """Roteador principal de tarefas de memória."""
        try:
            tarefa_lower = tarefa.lower()
            
            if "processar mensagem" in tarefa_lower:
                return await self._processar_e_atualizar(tarefa)
            
            if "contexto sobre" in tarefa_lower or "contexto de" in tarefa_lower:
                return await self._recuperar_contexto(tarefa)
            
            if "criar perfil" in tarefa_lower:
                return await self._criar_perfil(tarefa)
            
            if "listar entidades" in tarefa_lower:
                return self._listar_entidades()
            
            if "exportar memoria" in tarefa_lower:
                return self._exportar_memoria()
            
            return {
                "sucesso": False,
                "erro": "Comando de memória não reconhecido",
                "comandos_disponiveis": [
                    "processar mensagem: <texto>",
                    "contexto sobre <entidade>",
                    "criar perfil <entidade_id>",
                    "listar entidades",
                    "exportar memoria"
                ]
            }
        except Exception as e:
            logger.error(f"Erro ao executar tarefa de memória: {e}", exc_info=True)
            return {"sucesso": False, "erro": str(e)}

    async def _processar_e_atualizar(self, tarefa: str) -> Dict[str, Any]:
        """
        Pipeline completo de processamento de mensagem com extração e atualização.
        Implementa o fluxo core do O-Mem: Extract -> Fuse -> Update.
        """
        try:
            # Extrair mensagem da tarefa
            if ":" in tarefa:
                mensagem = tarefa.split(":", 1)[1].strip()
            else:
                mensagem = tarefa.strip()
            
            self.contador_turnos += 1
            logger.info(f"📝 OmniMemoria: Processando turno {self.contador_turnos}")

            # Salvar no histórico
            self.historico_turnos.append({
                "turno": self.contador_turnos,
                "mensagem": mensagem,
                "timestamp": datetime.now().isoformat()
            })

            # FASE 1: EXTRAÇÃO usando o Cérebro
            extracao = await self._extrair_informacoes(mensagem)
            
            if not extracao["sucesso"]:
                return extracao

            # FASE 2: FUSÃO E ATUALIZAÇÃO
            entidade_id = extracao.get("entidade_id", "usuario_principal")
            
            # Garantir que persona existe
            if entidade_id not in self.personas:
                self.personas[entidade_id] = MemoriaPersona(entidade_id)

            persona = self.personas[entidade_id]
            
            # Atualizar atributos
            for chave, info in extracao.get("atributos", {}).items():
                valor = info.get("valor") if isinstance(info, dict) else info
                confianca = info.get("confianca", 0.7) if isinstance(info, dict) else 0.7
                persona.atualizar_atributo(chave, valor, confianca, self.contador_turnos)

            # Adicionar eventos
            for evento_data in extracao.get("eventos", []):
                evento = EventoVida(
                    data=evento_data.get("data", datetime.now().isoformat()[:10]),
                    evento=evento_data.get("descricao", ""),
                    importancia=evento_data.get("importancia", 0.5),
                    contexto=mensagem[:200],
                    turno=self.contador_turnos
                )
                persona.adicionar_evento(evento)

            # Atualizar memória de trabalho
            for topico in extracao.get("topicos", []):
                self.memoria_trabalho.adicionar_topico(topico, self.contador_turnos)

            # Atualizar memória episódica com pistas raras
            for pista in extracao.get("pistas_raras", []):
                self.memoria_episodica.indexar_pista(
                    pista.lower(),
                    self.contador_turnos,
                    mensagem
                )

            # Atualizar metadata
            persona.metadata["total_interacoes"] += 1
            persona.metadata["ultima_atualizacao"] = datetime.now().isoformat()

            # Invalidar cache
            self._cache_contexto.clear()

            logger.info(f"✅ Memórias atualizadas: {len(extracao.get('atributos', {}))} atributos, "
                       f"{len(extracao.get('eventos', []))} eventos, "
                       f"{len(extracao.get('topicos', []))} tópicos")

            return {
                "sucesso": True,
                "turno": self.contador_turnos,
                "entidade": entidade_id,
                "atualizacoes": {
                    "atributos": len(extracao.get("atributos", {})),
                    "eventos": len(extracao.get("eventos", [])),
                    "topicos": len(extracao.get("topicos", [])),
                    "pistas": len(extracao.get("pistas_raras", []))
                }
            }

        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}", exc_info=True)
            return {"sucesso": False, "erro": str(e)}

    async def _extrair_informacoes(self, mensagem: str) -> Dict[str, Any]:
        """
        Usa o Cérebro para extrair informações estruturadas da mensagem.
        Retorna: entidade_id, atributos, eventos, tópicos, pistas_raras.
        """
        prompt = f"""Analise a mensagem do usuário e extraia informações estruturadas em formato JSON.

Mensagem: "{mensagem}"

Extraia:
1. "entidade_id": identificador da pessoa/entidade (ex: "pedro", "usuario_principal")
2. "atributos": dicionário de fatos sobre a entidade (ex: {{"profissao": "desenvolvedor", "linguagem_preferida": "Python"}})
   - Cada atributo pode ter: {{"valor": "...", "confianca": 0.0-1.0}}
3. "eventos": lista de eventos significativos (ex: [{{"data": "2025-11-26", "descricao": "Iniciou projeto X", "importancia": 0.8}}])
4. "topicos": lista de palavras-chave/tópicos da conversa (ex: ["O-Mem", "arquitetura", "memória"])
5. "pistas_raras": termos específicos, técnicos ou únicos que merecem indexação especial (ex: ["OCTOPUS-CONSCIOUSNESS", "Maestrina"])

Retorne APENAS o JSON, sem texto adicional:"""

        try:
            resposta = self.cerebro.gerar_pensamento(prompt, max_tokens=500)
            
            # Tentar parsear JSON
            # Limpar possíveis markdown
            resposta_limpa = resposta.strip()
            if resposta_limpa.startswith("```"):
                resposta_limpa = resposta_limpa.split("```")[1]
                if resposta_limpa.startswith("json"):
                    resposta_limpa = resposta_limpa[4:]
            resposta_limpa = resposta_limpa.strip()
            
            extracao = json.loads(resposta_limpa)
            extracao["sucesso"] = True
            return extracao
            
        except json.JSONDecodeError as e:
            logger.warning(f"Falha ao parsear JSON da extração: {e}")
            # Fallback com extração básica
            return {
                "sucesso": True,
                "entidade_id": "usuario_principal",
                "atributos": {},
                "eventos": [],
                "topicos": [palavra for palavra in mensagem.lower().split() if len(palavra) > 4][:5],
                "pistas_raras": []
            }
        except Exception as e:
            logger.error(f"Erro na extração: {e}", exc_info=True)
            return {"sucesso": False, "erro": str(e)}

    async def _recuperar_contexto(self, tarefa: str) -> Dict[str, Any]:
        """
        Recupera contexto multifacetado das três memórias.
        Implementa a estratégia de recuperação do O-Mem.
        """
        try:
            # Extrair entidade alvo
            if "sobre" in tarefa.lower():
                alvo = tarefa.lower().split("sobre")[1].strip()
            elif "de" in tarefa.lower():
                alvo = tarefa.lower().split("de")[1].strip()
            else:
                alvo = "usuario_principal"
            
            # Normalizar ID
            entidade_id = alvo.split()[0] if alvo else "usuario_principal"

            # Verificar cache
            cache_key = f"{entidade_id}_{self.contador_turnos}"
            if cache_key in self._cache_contexto:
                contexto_cached, turno_cache = self._cache_contexto[cache_key]
                if self.contador_turnos - turno_cache < self._cache_ttl:
                    logger.info("📦 Usando contexto do cache")
                    return {"sucesso": True, "contexto": contexto_cached, "fonte": "cache"}

            # Recuperar persona
            persona = self.personas.get(entidade_id)
            if not persona:
                return {
                    "sucesso": False,
                    "erro": f"Nenhuma persona encontrada para '{entidade_id}'",
                    "entidades_disponiveis": list(self.personas.keys())
                }

            # CONSTRUIR CONTEXTO MULTIFACETADO
            blocos_contexto = []

            # 1. Perfil da Persona (atributos de alta confiança)
            atributos_relevantes = {
                k: v.valor for k, v in persona.atributos.items()
                if v.confianca > 0.5
            }
            if atributos_relevantes:
                blocos_contexto.append(
                    f"**Perfil de {entidade_id}:**\n" +
                    "\n".join(f"- {k}: {v}" for k, v in atributos_relevantes.items())
                )

            # 2. Eventos recentes (top 5 por importância)
            eventos_top = sorted(
                persona.eventos_vida,
                key=lambda e: e.importancia,
                reverse=True
            )[:5]
            if eventos_top:
                blocos_contexto.append(
                    "**Eventos Significativos:**\n" +
                    "\n".join(f"- {e.data}: {e.evento}" for e in eventos_top)
                )

            # 3. Tópicos recentes da memória de trabalho
            topicos_recentes = self.memoria_trabalho.obter_topicos_recentes(5)
            if topicos_recentes:
                blocos_contexto.append(
                    f"**Tópicos Recentes:** {', '.join(topicos_recentes)}"
                )

            # 4. Busca episódica por pistas no alvo
            pistas_encontradas = []
            for palavra in alvo.split():
                turnos = self.memoria_episodica.buscar_por_pista(palavra)
                if turnos:
                    pistas_encontradas.append(f"'{palavra}' (turnos: {turnos[-3:]})")
            
            if pistas_encontradas:
                blocos_contexto.append(
                    f"**Referências Episódicas:** {', '.join(pistas_encontradas)}"
                )

            # 5. Metadata
            blocos_contexto.append(
                f"\n**Meta:** {persona.metadata['total_interacoes']} interações, "
                f"última atualização: {persona.metadata['ultima_atualizacao'][:10]}"
            )

            contexto_final = "\n\n".join(blocos_contexto)

            # Atualizar cache
            self._cache_contexto[cache_key] = (contexto_final, self.contador_turnos)

            logger.info(f"✅ Contexto recuperado para '{entidade_id}': {len(contexto_final)} chars")

            return {
                "sucesso": True,
                "entidade": entidade_id,
                "contexto": contexto_final,
                "estatisticas": {
                    "atributos": len(atributos_relevantes),
                    "eventos": len(eventos_top),
                    "topicos": len(topicos_recentes),
                    "pistas": len(pistas_encontradas)
                }
            }

        except Exception as e:
            logger.error(f"Erro ao recuperar contexto: {e}", exc_info=True)
            return {"sucesso": False, "erro": str(e)}

    async def _criar_perfil(self, tarefa: str) -> Dict[str, Any]:
        """Cria um novo perfil de persona."""
        try:
            entidade_id = tarefa.split("criar perfil")[1].strip()
            if not entidade_id:
                return {"sucesso": False, "erro": "ID da entidade não fornecido"}
            
            if entidade_id in self.personas:
                return {
                    "sucesso": False,
                    "erro": f"Persona '{entidade_id}' já existe"
                }
            
            self.personas[entidade_id] = MemoriaPersona(entidade_id)
            logger.info(f"✨ Nova persona criada: '{entidade_id}'")
            
            return {
                "sucesso": True,
                "entidade": entidade_id,
                "mensagem": f"Perfil criado para '{entidade_id}'"
            }
        except Exception as e:
            return {"sucesso": False, "erro": str(e)}

    def _listar_entidades(self) -> Dict[str, Any]:
        """Lista todas as entidades com perfis."""
        entidades_info = {}
        for entidade_id, persona in self.personas.items():
            entidades_info[entidade_id] = {
                "total_interacoes": persona.metadata["total_interacoes"],
                "atributos": len(persona.atributos),
                "eventos": len(persona.eventos_vida),
                "ultima_atualizacao": persona.metadata.get("ultima_atualizacao")
            }
        
        return {
            "sucesso": True,
            "total_entidades": len(entidades_info),
            "entidades": entidades_info
        }

    def _exportar_memoria(self) -> Dict[str, Any]:
        """Exporta toda a memória para persistência."""
        try:
            export_data = {
                "versao": "1.0",
                "timestamp": datetime.now().isoformat(),
                "contador_turnos": self.contador_turnos,
                "personas": {
                    entidade_id: persona.to_dict()
                    for entidade_id, persona in self.personas.items()
                },
                "memoria_trabalho": {
                    "topicos": self.memoria_trabalho.topicos
                },
                "memoria_episodica": {
                    "pistas": self.memoria_episodica.pistas,
                    "frequencia_global": self.memoria_episodica.frequencia_global
                },
                "estatisticas": {
                    "total_entidades": len(self.personas),
                    "total_turnos": self.contador_turnos,
                    "total_pistas_indexadas": len(self.memoria_episodica.pistas)
                }
            }
            
            return {
                "sucesso": True,
                "export": export_data
            }
        except Exception as e:
            logger.error(f"Erro ao exportar memória: {e}", exc_info=True)
            return {"sucesso": False, "erro": str(e)}
