import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import silhouette_score, davies_bouldin_score, silhouette_samples
from scipy.spatial.distance import cdist

# 📂 Configurações
DB_PATH = "../database/cyber_attacks.db"
TABLE_KMEANS = "kmeans_named_clusters"
TABLE_AGGLO = "agglomerative_table"

# 🎯 Carregar dados pré-processados
def load_data(table_name):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
    conn.close()
    print(f"✅ Dados carregados: {table_name} ({len(df)} registros)")
    return df

# 🔢 Selecionar features
def select_features(df):
    return df[["total_attack_severity_norm", "cyber_intensity_norm"]]

# 📊 Gráfico da Silhueta com nomes personalizados
def plot_silhouette(data, labels, cluster_names, title):
    silhouette_vals = silhouette_samples(data, labels)
    y_lower = 10
    plt.figure(figsize=(10, 6))

    for i, cluster_name in cluster_names.items():
        ith_silhouette_vals = silhouette_vals[labels == i]
        ith_silhouette_vals.sort()
        size_cluster_i = ith_silhouette_vals.shape[0]
        y_upper = y_lower + size_cluster_i

        plt.fill_betweenx(np.arange(y_lower, y_upper), 0, ith_silhouette_vals, alpha=0.7)
        plt.text(-0.05, y_lower + 0.5 * size_cluster_i, cluster_name)
        y_lower = y_upper + 10

    plt.xlabel("Coeficiente de Silhueta")
    plt.ylabel("Clusters")
    plt.title(title)
    plt.axvline(x=silhouette_vals.mean(), color="red", linestyle="--",
                label=f"Média ({silhouette_vals.mean():.3f})")
    plt.legend()
    plt.tight_layout()
    plt.show()

# 📊 Avaliar clusters existentes
def evaluate_existing_clusters(features, labels):
    silhouette = silhouette_score(features, labels)
    davies = davies_bouldin_score(features, labels)
    return silhouette, davies

# 📋 Mostrar tabela de resultados (imagem)
def plot_scores_table(scores_df):
    fig, ax = plt.subplots(figsize=(10, 2))
    ax.axis('off')
    table = ax.table(cellText=scores_df.values,
                     colLabels=scores_df.columns,
                     cellLoc='center',
                     loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1.5, 2.0)
    plt.title("Tabela de Avaliação dos Modelos", fontsize=14, pad=20)
    plt.tight_layout()
    plt.show()

# 📋 Mostrar também no terminal
def print_scores_table(scores_df):
    print("\n📋Avaliação dos Modelos:")
    print(scores_df.to_string(index=False))
    print("\n")

# 💾 Salvar resultados no banco
def save_evaluation_results(scores_df):
    conn = sqlite3.connect(DB_PATH)
    scores_df.to_sql("model_evaluation_metrics", conn, if_exists="replace", index=False)
    conn.close()

# 📋 Tabela detalhada Davies-Bouldin
def detailed_davies_bouldin(features, labels, cluster_names):
    clusters = np.unique(labels)
    centroids = np.array([features[labels == k].mean(axis=0) for k in clusters])
    dispersions = np.array([
        np.mean(cdist(features[labels == k], [centroids[i]], 'euclidean'))
        for i, k in enumerate(clusters)
    ])

    db_table = []
    for i, cluster_i in enumerate(clusters):
        max_ratio = -np.inf
        closest_cluster = None
        for j, cluster_j in enumerate(clusters):
            if i != j:
                distance = np.linalg.norm(centroids[i] - centroids[j])
                ratio = (dispersions[i] + dispersions[j]) / distance
                if ratio > max_ratio:
                    max_ratio = ratio
                    closest_cluster = cluster_j
        db_table.append({
            "Cluster": cluster_names[cluster_i],
            "Dispersão Interna (σ)": round(dispersions[i], 3),
            "Cluster mais próximo": cluster_names[closest_cluster],
            "Índice Parcial": round(max_ratio, 3)
        })

    return pd.DataFrame(db_table)

# 📋 Plotar tabela detalhada Davies-Bouldin
def plot_detailed_db_table(df_db, title):
    fig, ax = plt.subplots(figsize=(12, 2 + len(df_db)*0.4))
    ax.axis('off')
    table = ax.table(cellText=df_db.values,
                     colLabels=df_db.columns,
                     cellLoc='center',
                     loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1.2, 1.5)
    plt.title(title, fontsize=14, pad=20)
    plt.tight_layout()
    plt.show()

# 📋 Mostrar também no terminal
def print_detailed_db_table(df_db, label):
    print(f"\n📋 {label}")
    print(df_db.to_string(index=False))
    print("\n")

# 🚀 Execução principal
if __name__ == "__main__":
    # Carregar dados existentes
    df_kmeans = load_data(TABLE_KMEANS)
    df_agglo = load_data(TABLE_AGGLO)

    # Selecionar features e labels
    features_kmeans = select_features(df_kmeans)
    labels_kmeans = df_kmeans["Cluster"]

    features_agglo = select_features(df_agglo)
    labels_agglo = df_agglo["Cluster"]

    # Avaliar numericamente
    k_silhouette, k_davies = evaluate_existing_clusters(features_kmeans, labels_kmeans)
    a_silhouette, a_davies = evaluate_existing_clusters(features_agglo, labels_agglo)

    # Resultados em tabela
    scores_df = pd.DataFrame({
        "Algoritmo": ["K-Means", "Agglomerative Clustering"],
        "Coeficiente de Silhouette": [round(k_silhouette, 3), round(a_silhouette, 3)],
        "Índice Davies-Bouldin": [round(k_davies, 3), round(a_davies, 3)]
    })

    # Nomes dos clusters
    kmeans_cluster_names = {
        0: "Baixa Severidade",
        1: "Média Severidade",
        2: "Alta Severidade",
        3: "Crítico"
    }

    agglo_cluster_names = {
        0: "Europa Central e Mídia",
        1: "Infraestrutura Crítica",
        2: "Governos e Energia",
        3: "Militar e Financeiro"
    }

    # Gráficos da Silhueta
    plot_silhouette(features_kmeans.values, labels_kmeans, kmeans_cluster_names, "Silhueta - K-Means")
    plot_silhouette(features_agglo.values, labels_agglo, agglo_cluster_names, "Silhueta - Agglomerative Clustering")

    # Mostrar tabelas
    plot_scores_table(scores_df)
    print_scores_table(scores_df)

    # Salvar no banco
    save_evaluation_results(scores_df)
    print("✅ Avaliação concluída e resultados salvos no banco de dados.")

    # ➕ Tabelas detalhadas Davies-Bouldin
    kmeans_db_table = detailed_davies_bouldin(features_kmeans.values, labels_kmeans.values, kmeans_cluster_names)
    plot_detailed_db_table(kmeans_db_table, "Resultado Detalhada Davies-Bouldin (K-Means)")
    print_detailed_db_table(kmeans_db_table, "Resultado Detalhada Davies-Bouldin (K-Means)")

    agglo_db_table = detailed_davies_bouldin(features_agglo.values, labels_agglo.values, agglo_cluster_names)
    plot_detailed_db_table(agglo_db_table, "Resultado Detalhada Davies-Bouldin (Agglomerative Clustering)")
    print_detailed_db_table(agglo_db_table, "Resultado Detalhada Davies-Bouldin (Agglomerative Clustering)")