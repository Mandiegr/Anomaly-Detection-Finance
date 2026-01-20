## Tecnologias Utilizadas

O projeto foi construído utilizando o ecossistema de dados do Python:

* **Python 3.10+** - Linguagem base
*  **Pandas & Numpy** - Processamento e análise matricial
*  **Matplotlib & Seaborn** - Data Visualization
*  **SQLite3** - Banco de dados relacional leve
*  **Openpyxl** - Motor de exportação para Excel

## Estrutura do Projeto

A organização segue o padrão de separação de responsabilidades:

```text
analisador_2026/
├── data/       # Armazenamento persistente (DB e JSON)
├── scripts/    # Core do sistema (.py)
├── outputs/    # Artefatos gerados (Gráficos, Planilhas, TXT)
└── README.md   # Guia do projeto
```
Como Executar:

### 1. Clone o repositório
git clone https://github.com/seu-usuario/analisador-2026.git

### 2. Acesse a pasta
cd analisador_2026

### 3. Instale as dependências
pip install pandas matplotlib seaborn openpyxl

### 4. Rode o analisador
python scripts/main.py