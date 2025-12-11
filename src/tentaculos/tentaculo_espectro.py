# src/tentaculos/tentaculo_espectro.py

import logging
import asyncio
from typing import Dict, Any

from .utils.mock_bluetooth import BleakScanner, BleakClient, MockDevice
from .base_tentaculo import BaseTentaculo
from src.cognitive.cerebro import Cerebro
from src.shared.comunicacao import BarramentoEventos, Evento

logger = logging.getLogger(__name__)

class TentaculoEspectro(BaseTentaculo):
    """
    Especialista autodidata em Bluetooth. Descobre, aprende e controla
    dinamicamente novos dispositivos IoT e celulares.
    """
    def __init__(self, cerebro: Cerebro, barramento: BarramentoEventos):
        super().__init__("Espectro Bluetooth", cerebro, barramento)
        self.dispositivos_conhecidos: Dict[str, Any] = {}
        self.conexoes_ativas: Dict[str, BleakClient] = {}
        # Base de conhecimento de protocolos (drivers dinâmicos)
        self.base_de_protocolos: Dict[str, Any] = self._carregar_protocolos()
        self.fila_resultados_pesquisa = asyncio.Queue()
        logger.info("👻 Tentáculo Espectro (Autodidata v2) instanciado.")

    async def iniciar(self):
        """Inicia os loops de escuta e tarefas de aprendizagem."""
        await super().iniciar() # Assina TAREFA_DELEGADA
        # Assina os resultados de suas próprias missões de pesquisa
        await self.barramento.assinar("TAREFA_CONCLUIDA", self.fila_resultados_pesquisa)

    def _carregar_protocolos(self) -> Dict[str, Any]:
        """Carrega a base de conhecimento de protocolos conhecidos."""
        # Em um sistema real, isso viria de um arquivo de configuração ou banco de dados.
        return {
            "Serviço de Bateria": {
                "uuid_servico": "0000180f-0000-1000-8000-00805f9b34fb",
                "comandos": {
                    "LER_BATERIA": {
                        "uuid_caracteristica": "00002a19-0000-1000-8000-00805f9b34fb",
                        "acao": "ler_valor_int"
                    }
                }
            }
        }

    async def executar_tarefa(self, tarefa: str) -> str:
        """Executa uma tarefa, aprendendo sobre novos dispositivos se necessário."""
        logger.info(f"Espectro: Recebi a tarefa '{tarefa}'.")
        try:
            # Usa o Cérebro para extrair a intenção e o alvo da tarefa
            prompt_analise = (
                "Analise a tarefa e extraia a AÇÃO e o ALVO em formato JSON. "
                "Ações válidas: 'LER_BATERIA', 'FAZER_VIBRAR', 'LER_GPS'.\n"
                f"Tarefa: '{tarefa}'\n\nJSON:"
            )
            analise = self.cerebro.gerar_pensamento(prompt_analise, max_tokens=50)
            # Simulação da análise JSON
            acao = "LER_BATERIA"
            alvo = "Fone de Ouvido Sony"

            # Encontra o dispositivo
            cliente, dispositivo = await self._encontrar_e_conectar(alvo)
            
            # Tenta executar o comando com os protocolos conhecidos
            for protocolo in self.base_de_protocolos.values():
                if acao in protocolo["comandos"]:
                    comando_info = protocolo["comandos"][acao]
                    if comando_info["acao"] == "ler_valor_int":
                        valor_byte = await cliente.read_gatt_char(comando_info["uuid_caracteristica"])
                        valor_int = int.from_bytes(valor_byte, byteorder='little')
                        return f"Sucesso: {acao} do dispositivo '{alvo}' é {valor_int}."
            
            # Se chegou aqui, o comando ou dispositivo é desconhecido. Inicia o aprendizado.
            return await self._aprender_novo_dispositivo(cliente, dispositivo)

        except Exception as e:
            logger.error(f"Erro ao executar tarefa Bluetooth: {e}", exc_info=True)
            return f"Falha na tarefa Bluetooth. Erro: {e}"
        finally:
            # Lógica de desconexão
            pass

    async def _encontrar_e_conectar(self, nome_dispositivo: str) -> (BleakClient, MockDevice):
        # ... (lógica de escanear e conectar inalterada) ...
        # Retorna tanto o cliente quanto o objeto do dispositivo
        pass

    async def _aprender_novo_dispositivo(self, cliente: BleakClient, dispositivo: MockDevice) -> str:
        """Inicia o ciclo de aprendizagem para um dispositivo desconhecido."""
        logger.info(f"Iniciando ciclo de aprendizagem para o dispositivo desconhecido: '{dispositivo.name}'")
        
        # 1. Introspecção: Descobrir serviços
        servicos = await cliente.get_services()
        uuids_desconhecidos = []
        for servico in servicos:
            if not any(p['uuid_servico'] == servico.uuid for p in self.base_de_protocolos.values()):
                uuids_desconhecidos.append(servico.uuid)

        if not uuids_desconhecidos:
            return "Dispositivo não possui serviços desconhecidos para aprender."

        # 2. Investigação Cognitiva: Delega a pesquisa
        logger.info(f"  -> Encontrados UUIDs desconhecidos: {uuids_desconhecidos}. Pesquisando online...")
        for uuid in uuids_desconhecidos:
            tarefa_busca = Evento(
                tipo="TAREFA_DELEGADA",
                dados={"descricao": f"Pesquisar documentação para 'Bluetooth service UUID {uuid}'"},
                origem=self.tipo
            )
            await self.barramento.publicar(tarefa_busca)

        # 3. Síntese (simulação)
        # Em um sistema real, aguardaria e processaria os resultados da pesquisa
        await asyncio.sleep(5) # Simula o tempo de pesquisa e análise
        
        # Simula que a pesquisa encontrou um novo protocolo
        novo_protocolo_nome = "Serviço de Notificação Imediata"
        novo_protocolo_driver = {
            "uuid_servico": uuids_desconhecidos[0],
            "comandos": {
                "LER_ALERTA": {
                    "uuid_caracteristica": "00002a46-0000-1000-8000-00805f9b34fb",
                    "acao": "ler_valor_string"
                }
            }
        }
        self.base_de_protocolos[novo_protocolo_nome] = novo_protocolo_driver
        logger.info(f"✨ Novo protocolo aprendido e adicionado à base de conhecimento: '{novo_protocolo_nome}'!")

        return f"Aprendizagem concluída para '{dispositivo.name}'. Agora eu sei como interagir com '{novo_protocolo_nome}'. Por favor, repita sua tarefa."

