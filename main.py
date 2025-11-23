# main.py
# Ponto de entrada para a simulação da Arquitetura Consciência Polvo.
# Autor: Pedro Miorini

from src.manto.agente_manto import Manto, RedeDeTentaculos
from src.tentaculos.tentaculo_codigo import TentaculoCodigo
from src.tentaculos.tentaculo_busca import TentaculoBusca

def main():
    """
    Função principal que inicializa e executa a simulação.
    """
    print("="*70)
    print("🔥 PROJETO CONSCIÊNCIA POLVO v1.0 - INICIANDO SIMULAÇÃO 🔥")
    print("="*70)

    # 1. Inicializar os tentáculos especialistas
    print("\n[1/3] Inicializando a rede de tentáculos especialistas...")
    try:
        tentaculo1 = TentaculoBusca(id_tentaculo=1)
        tentaculo2 = TentaculoCodigo(id_tentaculo=2)
        # Futuros tentáculos (ex: TentaculoTreinamento, TentaculoAnaliseDados) podem ser adicionados aqui.
        
        rede = RedeDeTentaculos([tentaculo1, tentaculo2])
        print("✓ Rede de tentáculos online.")
    except Exception as e:
        print(f"❌ Erro ao inicializar tentáculos: {e}")
        return

    # 2. Ativar a consciência central (Manto)
    print("\n[2/3] Ativando o Manto (Consciência Central)...")
    consciencia_central = Manto(rede)
    
    # 3. Definir e executar um objetivo macro
    print("\n[3/3] Delegando objetivo macro para o Manto...")
    objetivo = "Pesquisar e analisar os principais frameworks de IA autônoma disponíveis publicamente."
    consciencia_central.decompor_e_orquestrar(objetivo)

if __name__ == "__main__":
    main()
