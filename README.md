# Projeto Consciência Polvo v1.0

Este repositório contém a implementação do **Projeto Consciência Polvo**, uma arquitetura de inteligência artificial inspirada na estrutura neural descentralizada dos cefalópodes.

## Arquitetura

O sistema é projetado em torno de dois componentes principais, criando um modelo de computação distribuída e especializada:

-   **🐙 Manto (A Consciência Central):** Um agente de alto nível, análogo ao cérebro central de um polvo. Sua única função é o **pensamento estratégico**. Ele recebe objetivos complexos, os decompõe em um plano de ação com várias etapas e o orquestra a execução, selecionando os melhores especialistas para cada tarefa.

-   **🦾 Tentáculos (Agentes Especialistas):** Um conjunto de agentes modulares, independentes e especializados, análogos aos "cérebros" localizados nos tentáculos de um polvo. Cada tentáculo possui seu próprio modelo de IA e ferramentas otimizadas para uma única função (ex: `TentaculoCodigo` para análise de software, `TentaculoBusca` para pesquisa na web). Eles operam em modo de baixo consumo e são ativados pelo Manto para executar missões específicas.

## Como Executar a Simulação

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/pedromiorini/OCTOPUS-CONSCIOUSNESS.git
    cd OCTOPUS-CONSCIOUSNESS
    ```

2.  **(Opcional) Crie um ambiente virtual:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # No Windows: venv\Scripts\activate
    ```

3.  **Execute o ponto de entrada principal:**
    ```bash
    python main.py
    ```

O script simulará um fluxo de trabalho onde o Manto recebe um objetivo, o decompõe, consulta os tentáculos e orquestra a execução.

## Próximos Passos

-   Implementar modelos de linguagem reais em cada tentáculo.
-   Construir um barramento de mensagens assíncrono (ex: RabbitMQ) para a comunicação.
-   Adicionar mais tentáculos especialistas (ex: `TentaculoTreinamento`, `TentaculoAnaliseDados`).

---
*Este projeto é uma exploração conceitual e prática de arquiteturas de IA avançadas, de autoria de Pedro Miorini.*
