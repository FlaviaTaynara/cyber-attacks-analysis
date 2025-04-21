# 📊 Cyber Attacks Clustering Analysis (2000–2025)

Este projeto realiza uma análise de ataques cibernéticos registrados na União Europeia entre 2000 e 2025, utilizando algoritmos de aprendizado não supervisionado como **K-Means**, **Agglomerative Clustering** e **PCA (Análise de Componentes Principais)**. O objetivo é identificar padrões de severidade e intensidade dos ataques com base em setores, tipos de ataques e países afetados.

## 🧠 Objetivos do Projeto

- 📥 Carregar e tratar dados da base **EUREPOC**
- 🧼 Aplicar transformação, categorização e normalização
- 📊 Realizar **clusterização não supervisionada** com K-Means e Hierárquico
- 🔍 Explorar **redução de dimensionalidade com PCA**
- 📈 Avaliar os agrupamentos com **Silhouette Score** e **Davies-Bouldin Index**
- 🧾 Gerar visualizações explicativas como **gráficos 2D/3D, dendrogramas e tabelas**

## 🗂️ Organização dos Scripts

| Script | Função Principal |
|--------|------------------|
| `script_1_load_and_prepare.py` | Carrega o CSV original e cria a tabela `cyber_incidents` no banco SQLite. |
| `script_2_preprocessing_pipeline.py` | Aplica limpeza, criação de atributos compostos, mapeamento categórico e normalização. |
| `script_3_pca_analysis.py` | Aplica PCA e gera gráficos de variância explicada e mapa de calor da matriz de correlação. |
| `script_3_alt_pipeline.py` | Versão alternativa do pipeline de pré-processamento. |
| `script_4_kmeans_clustering.py` | Executa K-Means e plota gráficos com **PCA 2D/3D**, além de salvar clusters com nomes descritivos. |
| `script_4.1_agglomerative_clustering.py` | Executa o algoritmo hierárquico e plota **dendrogramas por setor+ataque e por país**. |
| `script_5_model_evaluation.py` | Compara os modelos com métricas de avaliação e apresenta os resultados em tabelas e gráficos. |

## 💾 Banco de Dados

Todos os dados processados e resultados são armazenados no arquivo SQLite:  
📁 `/database/cyber_attacks.db`

Tabelas principais:
- `cyber_incidents`
- `cyber_incidents_processed`
- `pca_variance`
- `kmeans_named_clusters`
- `agglomerative_table`
- `model_evaluation_metrics`

## ▶️ Como Executar

```bash
# 1. Clone o repositório
git clone https://github.com/FlaviaTaynara/cyber-attacks-analysis.git
cd cyber-attacks-analysis

# 2. Instale as dependências
pip install pandas matplotlib seaborn scikit-learn scipy

# 3. Execute os scripts na ordem
python script_1_load_and_prepare.py
python script_2_preprocessing_pipeline.py
python script_3_pca_analysis.py
python script_4.1_kmeans_clustering.py
python script_4.3_agglomerative_clustering.py
python script_5_model_evaluation.py


Exemplos de Saída
	•	✅ Gráficos do método do cotovelo e silhueta
	•	✅ Visualizações com PCA em 2D e 3D
	•	✅ Dendrogramas com legendas explicativas
	•	✅ Tabelas de avaliação: Silhouette Score e Davies-Bouldin Index
	•	✅ Tabelas descritivas dos clusters (em imagem e no terminal)


📎 Apêndice

Para fins de transparência e reprodutibilidade, todos os scripts utilizados para esta análise estão disponíveis neste repositório, na branch principal:
🔗 https://github.com/FlaviaTaynara/cyber-attacks-analysis


👩‍💻 Autoria

Projeto desenvolvido por FM.
📚 Mestrado em Ciência de Dados – TCC: Evolução dos Ataques Cibernéticos e seus Padrões de Risco na União Europeia (2000–2025)
📬 Contato: https://www.linkedin.com/in/flavia-maciulevicius/