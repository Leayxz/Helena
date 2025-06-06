# ⚡ Automação LN Markets - V001
Um bot de automação para operar contratos futuros de Bitcoin via LN Markets, utilizando critérios de variação de preço e gestão de ordens ativas. A aplicação verifica o preço do BTC a cada segundo, executa ordens de compra com base em critérios de margem e volatilidade, e fecha posições automaticamente com base em lucro esperado, considerando taxas de operação e funding. Atualmente está hospedado em uma instância EC2 da AWS.

## 🚀 Tecnologias Utilizadas
- Biblioteca ln-markets para interação com a API da exchange;
- Variáveis de ambiente com python-decouple;
- Deploy em nuvem com AWS EC2;

## 📌 Funcionalidades
- Detecção automática de variações significativas de preço do BTC;
- Execução de ordens com margem e alavancagem configuradas;
- Fechamento de trades lucrativos com cálculo dinâmico de taxas (carry fees e taxas fixas);
- Consulta e limpeza de ordens abertas em tempo real;

## 🧠 Aprendizados
- Uso prático da API da LN Markets com autenticação segura;
- Controle de fluxo com try/except para automações contínuas;
- Deploy e execução contínua da automação na AWS EC2;
- Estratégias básicas de gestão de risco com margem disponível e controle de perdas;

## 🧪 Caso Queira Testar
- Você vai precisar criar sua chave API e fazer as substituições correspondentes para abrir conexão.
- A Automação precisa de um nome para funcionar. Dê um nome para ela, ou ele.
- Só vai funcionar em tempo de execução. Caso queira 24/7, precisa subir para uma instância EC2 da AWS.
- Então basta abrir o terminal e digitar:
```bash
git clone https://github.com/Leayxz/Helena.git
pip install ln-markets python-decouple
python Index.py
```
