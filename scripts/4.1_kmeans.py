import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from mpl_toolkits.mplot3d import Axes3D

# 📂 CONFIG
DB_PATH = "../database/cyber_attacks.db"
TABLE_NAME = "cyber_incidents_processed"
KMEANS_TABLE = "kmeans_named_clusters"
N_CLUSTERS = 4


# 📥 Carregar dados
def load_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(f"SELECT * FROM {TABLE_NAME}", conn)
    conn.close()
    print(f"📊 {len(df)} registros carregados.")
    return df


# 🔢 Selecionar colunas normalizadas
def select_features(df):
    return df[[
        "sector_tag_norm", "attack_type_tag_norm", "attacker_category_tag_norm",
        "impact_indicator_tag_norm", "total_attack_severity_norm", "cyber_intensity_norm"
    ]]


# 📈 Plotar gráfico do cotovelo para avaliar o número ideal de clusters
def plot_elbow_method(data, max_k=10):
    distortions = []
    K_range = range(1, max_k + 1)

    for k in K_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(data)
        distortions.append(kmeans.inertia_)

    plt.figure(figsize=(8, 5))
    plt.plot(K_range, distortions, 'bo-')
    plt.xlabel('Número de Clusters (k)')
    plt.ylabel('Distortion (Inércia)')
    plt.title('Método do Cotovelo para Determinar o k Ideal')
    plt.xticks(K_range)
    plt.grid(True)
    plt.tight_layout()
    plt.show()


# 🤖 Aplicar K-Means
def apply_kmeans(data, n_clusters):
    model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = model.fit_predict(data)
    return labels, model


# 🏷️ Nomear clusters com base em atributos predominantes
def assign_cluster_descriptions(df, labels):
    df = df.copy()
    df["Cluster"] = labels
    descriptions = {}

    for c in sorted(df["Cluster"].unique()):
        group = df[df["Cluster"] == c]
        setor = group["sector_cleaned"].value_counts().idxmax()
        ataque = group["attack_type_cleaned"].value_counts().idxmax()
        atacante = group["attacker_category_cleaned"].value_counts().idxmax()
        media = group["impact_indicator_value"].mean()

        if media >= 7:
            severidade = "Alta"
        elif media >= 4:
            severidade = "Média"
        else:
            severidade = "Baixa"

        nome = f"{setor} + {ataque} | Atacante: {atacante} | Severidade: {severidade}"
        descriptions[c] = nome

    df["Cluster_Description"] = df["Cluster"].map(descriptions)
    return df, descriptions


# 📊 Visualizar 2D e 3D com legendas completas
def plot_clusters(df, features):
    pca = PCA(n_components=3)
    pca_data = pca.fit_transform(features)
    df["PCA1"], df["PCA2"], df["PCA3"] = pca_data[:, 0], pca_data[:, 1], pca_data[:, 2]

    # 📈 Gráfico 2D
    plt.figure(figsize=(12, 6))
    sns.scatterplot(x="PCA1", y="PCA2", hue="Cluster_Description", data=df, palette="Set2", s=70)
    plt.title("Visualização dos Clusters K-Means em 2D (PCA apenas para visualização)")
    plt.xlabel("PCA 1")
    plt.ylabel("PCA 2")
    plt.legend(title="Descrição do Cluster", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.show()

    # 📊 Gráfico 3D
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')
    cores = sns.color_palette("Set2", len(df["Cluster_Description"].unique()))

    for i, desc in enumerate(df["Cluster_Description"].unique()):
        dados = df[df["Cluster_Description"] == desc]
        ax.scatter(dados["PCA1"], dados["PCA2"], dados["PCA3"], label=desc, color=cores[i], s=60)

    ax.set_title("Visualização dos Clusters K-Means em 3D (PCA apenas para visualização)")
    ax.set_xlabel("PCA 1")
    ax.set_ylabel("PCA 2")
    ax.set_zlabel("PCA 3")
    ax.legend(title="Descrição do Cluster", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.show()


# 📋 Mostrar tabela resumo como imagem
def render_summary_table_multiline(df):
    summary = []
    for c in sorted(df["Cluster"].unique()):
        group = df[df["Cluster"] == c]
        count = len(group)
        setor = group["sector_cleaned"].value_counts().idxmax()
        ataque = group["attack_type_cleaned"].value_counts().idxmax()
        vitima = group["attacker_category_cleaned"].value_counts().idxmax()
        media = group["impact_indicator_value"].mean()

        if media >= 7:
            severidade = "Alta"
        elif media >= 4:
            severidade = "Média"
        else:
            severidade = "Baixa"

        setor = '\n'.join(setor.split(' / '))
        ataque = '\n'.join(ataque.split(' / '))
        vitima = '\n'.join(vitima.split(' / '))

        summary.append([
            f"Grupo {c + 1}", setor, ataque, vitima, round(media, 2), severidade, count
        ])

    columns = [
        "Cluster", "Setor Predominante", "Ataque Predominante",
        "Setor Vítima", "Severidade Média", "Nível de Severidade",
        "Total de Registros"
    ]

    fig, ax = plt.subplots(figsize=(15, 1.2 + 0.7 * len(summary)))
    ax.axis('off')
    table = ax.table(cellText=summary, colLabels=columns, loc='center', cellLoc='left')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 2.0)
    plt.title("Resumo dos Clusters K-Means", fontsize=14, pad=20)
    plt.tight_layout()
    plt.show()


# 📋 Mostrar tabela também no terminal
def print_summary_table(df):
    summary = []
    for c in sorted(df["Cluster"].unique()):
        group = df[df["Cluster"] == c]
        count = len(group)
        setor = group["sector_cleaned"].value_counts().idxmax()
        ataque = group["attack_type_cleaned"].value_counts().idxmax()
        vitima = group["attacker_category_cleaned"].value_counts().idxmax()
        media = group["impact_indicator_value"].mean()

        if media >= 7:
            severidade = "Alta"
        elif media >= 4:
            severidade = "Média"
        else:
            severidade = "Baixa"

        summary.append([
            f"Grupo {c + 1}", setor, ataque, vitima, round(media, 2), severidade, count
        ])

    columns = [
        "Cluster", "Setor Predominante", "Ataque Predominante",
        "Setor Vítima", "Severidade Média", "Nível de Severidade",
        "Total de Registros"
    ]

    summary_df = pd.DataFrame(summary, columns=columns)
    print("\n📋 Resumo dos Clusters:")
    print(summary_df.to_string(index=False))


# 💾 Salvar resultados
def save_results(df):
    conn = sqlite3.connect(DB_PATH)
    df.to_sql(KMEANS_TABLE, conn, if_exists="replace", index=False)
    conn.close()
    print(f"✅ Resultados salvos na tabela '{KMEANS_TABLE}'.")


# 🚀 Execução principal
if __name__ == "__main__":
    df = load_data()
    df_features = select_features(df)

    print("📈 Gerando gráfico do cotovelo para encontrar o número ideal de clusters...")
    plot_elbow_method(df_features)

    print("🤖 Aplicando K-Means...")
    labels, model = apply_kmeans(df_features, N_CLUSTERS)

    print("🏷️ Criando descrições dos clusters...")
    df_named, cluster_descriptions = assign_cluster_descriptions(df, labels)

    print("📊 Gerando visualizações...")
    plot_clusters(df_named, df_features)

    print("📋 Gerando tabela visual com quebras de linha...")
    render_summary_table_multiline(df_named)

    print("🖥️ Imprimindo resumo dos clusters no terminal...")
    print_summary_table(df_named)

    print("💾 Salvando no banco...")
    save_results(df_named)

    print("✅ Script K-Means finalizado com sucesso!")