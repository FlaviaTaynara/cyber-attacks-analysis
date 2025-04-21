import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

# 📂 Caminho do banco de dados
DB_PATH = "../database/cyber_attacks.db"
TABLE_NAME = "cyber_incidents_processed"
PCA_TABLE = "pca_variance"  # Nome da tabela para armazenar os resultados do PCA

# 👥 Carregar dados do banco de dados
def load_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(f"SELECT * FROM {TABLE_NAME}", conn)
    conn.close()
    print(f"📊 {len(df)} registros carregados do banco de dados.")
    return df

# 🔄 Selecionar apenas colunas numéricas para PCA
def select_numeric_columns(df):
    numeric_cols = [
        "sector_tag_norm", "attack_type_tag_norm", "attacker_category_tag_norm",
        "impact_indicator_tag_norm", "total_attack_severity_norm", "cyber_intensity_norm"
    ]
    return df[numeric_cols]

# 📊 Gerar o Mapa de Calor da Matriz de Correlação
def plot_correlation_heatmap(data):
    plt.figure(figsize=(10, 6))
    correlation_matrix = data.corr()
    sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5)
    plt.title("Mapa de Calor da Matriz de Correlação")
    plt.show()

# 🔄 Aplicar PCA e calcular variância explicada
def apply_pca(data, n_components=6):
    scaler = StandardScaler()
    data_scaled = scaler.fit_transform(data)

    pca = PCA(n_components=n_components)
    pca_result = pca.fit_transform(data_scaled)

    explained_variance = pca.explained_variance_ratio_
    cumulative_variance = np.cumsum(explained_variance)  # Variância acumulada

    print(f"✅ PCA aplicado! Variância explicada por componente:")
    for i, (var, cum_var) in enumerate(zip(explained_variance, cumulative_variance)):
        print(f"PC{i + 1}: {var:.4f} (Acumulada: {cum_var:.4f})")

    return pca_result, explained_variance, cumulative_variance, pca

# 🔖 Salvar os resultados do PCA no banco de dados SQLite
def save_pca_results(explained_variance, cumulative_variance):
    df_pca = pd.DataFrame({
        "PC": [f"PC{i + 1}" for i in range(len(explained_variance))],
        "Variancia_Explicada": explained_variance,
        "Variancia_Acumulada": cumulative_variance
    })
    conn = sqlite3.connect(DB_PATH)
    df_pca.to_sql(PCA_TABLE, conn, if_exists="replace", index=False)
    conn.close()
    print(f"✅ Resultados do PCA salvos na tabela '{PCA_TABLE}'!")

# 📊 Gráfico da Variância Explicada e Acumulada
def plot_explained_variance(explained_variance, cumulative_variance):
    plt.figure(figsize=(10, 6))
    plt.bar(range(1, len(explained_variance) + 1), explained_variance, alpha=0.6, label="Variância Explicada")
    plt.plot(range(1, len(cumulative_variance) + 1), cumulative_variance, marker='o', linestyle='--', color='r', label="Variância Acumulada")
    plt.xlabel("Componentes Principais")
    plt.ylabel("Proporção da Variância Explicada")
    plt.title("Variância Explicada e Acumulada por Componente Principal")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.show()

# ✨ Executar pipeline completo
if __name__ == "__main__":
    print("📊 Carregando dados...")
    df = load_data()

    print("🔄 Selecionando colunas numéricas...")
    df_numeric = select_numeric_columns(df)

    print("📊 Gerando Mapa de Calor da Matriz de Correlação...")
    plot_correlation_heatmap(df_numeric)

    print("📈 Aplicando PCA...")
    pca_result, explained_variance, cumulative_variance, pca = apply_pca(df_numeric)

    print("🔖 Salvando resultados do PCA no banco de dados...")
    save_pca_results(explained_variance, cumulative_variance)

    print("📊 Gerando gráfico de variância explicada...")
    plot_explained_variance(explained_variance, cumulative_variance)

    print("✅ Processo concluído!")