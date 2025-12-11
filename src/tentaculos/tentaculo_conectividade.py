# src/tentaculos/tentaculo_conectividade.py

import logging
import asyncio
import subprocess
from typing import Dict, Any

from .base_tentaculo import BaseTentaculo
from src.cognitive.cerebro import Cerebro
from src.shared.comunicacao import BarramentoEventos, Evento

logger = logging.getLogger(__name__)

class TentaculoConectividade(BaseTentaculo):
    """
    Engenheiro de Rede Autônomo. Gerencia e soluciona problemas de conexões
    Wi-Fi e Ethernet, e mantém o Manto informado sobre o status da conectividade.
    """
    def __init__(self, cerebro: Cerebro, barramento: BarramentoEventos):
        super().__init__("Conectividade", cerebro, barramento)
        self.status_rede = {"online": False, "interface": None, "tipo": None, "latencia_ms": 9999}
        self.cofre_credenciais = {"WIFI_CASA": "senha123", "HOTSPOT_CELULAR": "senha456"}
        logger.info("📡 Tentáculo de Conectividade (v2) instanciado.")

    # ... (métodos pode_executar e iniciar inalterados) ...

    async def _loop_monitoramento_saude(self):
        """Loop de fundo que verifica a saúde da conexão, priorizando cabo."""
        while True:
            conexao_anterior = self.status_rede["online"]
            
            # 1. Prioridade máxima: Verificar conexão a cabo (Ethernet)
            conectado_cabo, latencia_cabo = await self._verificar_interface("eth0")
            
            if conectado_cabo:
                self.status_rede = {"online": True, "interface": "eth0", "tipo": "Cabo", "latencia_ms": latencia_cabo}
                if not conexao_anterior:
                    await self.notificar_mudanca_status(online=True)
            else:
                # 2. Se o cabo falhar, verificar Wi-Fi
                conectado_wifi, latencia_wifi = await self._verificar_interface("wlan0")
                if conectado_wifi:
                    self.status_rede = {"online": True, "interface": "wlan0", "tipo": "Wi-Fi", "latencia_ms": latencia_wifi}
                    if not conexao_anterior:
                        await self.notificar_mudanca_status(online=True)
                    
                    # Lógica de degradação específica para Wi-Fi
                    if latencia_wifi > 200:
                        logger.warning(f"📡 Saúde Wi-Fi: Conexão DEGRADADA (Latência: {latencia_wifi:.0f}ms).")
                        await self.solucionar_problema_wifi()
                else:
                    # 3. Se ambos falharem, o sistema está offline
                    if conexao_anterior:
                        self.status_rede["online"] = False
                        await self.notificar_mudanca_status(online=False)
                        # Tenta solucionar o problema de forma geral
                        await self.solucionar_problema_geral()

            await asyncio.sleep(10)

    async def _verificar_interface(self, interface: str) -> (bool, float):
        """Verifica a conectividade de uma interface de rede específica."""
        try:
            # O comando -I força o ping a usar uma interface específica
            cmd = f"ping -c 1 -W 2 -I {interface} 8.8.8.8"
            process = await asyncio.create_subprocess_shell(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            stdout, _ = await process.communicate()
            
            if process.returncode == 0:
                latencia = float(stdout.decode().split("time=")[1].split(" ms")[0])
                return True, latencia
        except (IndexError, ValueError, asyncio.TimeoutError, Exception):
            pass # Ignora erros, o resultado será 'False'
        return False, 9999

    async def notificar_mudanca_status(self, online: bool):
        """Publica um evento para o Manto sobre a mudança no status da conexão."""
        if online:
            logger.info(f"✅ CONEXÃO REESTABELECIDA via {self.status_rede['tipo']} ({self.status_rede['interface']}).")
            evento = Evento(tipo="CONEXAO_REESTABELECIDA", dados=self.status_rede, origem=self.tipo)
        else:
            logger.error("❌ CONEXÃO PERDIDA. Manto deve entrar em modo offline.")
            evento = Evento(tipo="CONEXAO_PERDIDA", dados={}, origem=self.tipo)
        await self.barramento.publicar(evento)

    async def solucionar_problema_wifi(self):
        """Usa o cérebro para diagnosticar problemas complexos de Wi-Fi."""
        logger.info("  -> Iniciando diagnóstico cognitivo de Wi-Fi...")
        # Simulação de escanear canais e potência
        dados_rede = "Nossa rede 'WIFI_CASA' está no canal 6 (-68dBm). Canais vizinhos 6, 7, 8 estão congestionados."
        
        prompt = (
            "Você é um engenheiro de redes. Analise os dados: "
            f"'{dados_rede}'. Qual a causa provável da instabilidade e a ação recomendada?"
        )
        analise_cerebro = self.cerebro.gerar_pensamento(prompt, max_tokens=100)
        logger.warning(f"  -> Análise do Cérebro: {analise_cerebro}")
        # Ação futura poderia ser baseada nesta análise

    async def solucionar_problema_geral(self):
        """Tenta se reconectar à melhor rede disponível quando tudo falha."""
        logger.info("  -> Iniciando protocolo de reconexão geral...")
        # Lógica para tentar se conectar à melhor rede conhecida (cabo, depois Wi-Fi)
        await asyncio.sleep(5)
        logger.info("  -> Tentativa de reconexão concluída (simulação).")

    async def executar_tarefa(self, tarefa: str) -> str:
        # ... (lógica para gerar relatório de rede, etc.) ...
        return super().executar_tarefa(tarefa)
