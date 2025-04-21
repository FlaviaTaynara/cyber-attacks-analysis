
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import scipy.cluster.hierarchy as sch
from sklearn.cluster import AgglomerativeClustering

# 📂 Configurações do Banco
DB_PATH = "../database/cyber_attacks.db"
TABLE_NAME = "cyber_incidents_processed"
AGGLOMERATIVE_TABLE = "agglomerative_table"

# 🔠 Mapeamento de Abreviações
sector_abbreviations = {
    "Government": "GOV", "Military": "MIL", "Health": "HLT", "Finance": "FIN",
    "Energy": "ENG", "Telecom": "TEL", "Transport": "TRN", "Education": "EDU",
    "Critical infrastructure": "INF", "Media": "MED", "Manufacturing": "MRF"
}

attack_type_abbreviations = {
    "Data theft": "DT", "Disruption": "DIS", "Hijacking": "HIJ", "Ransomware": "RAN",
    "Phishing": "PHI", "DDoS": "DDoS", "Malware": "MAL"
}

country_abbreviations = {
    "Austria": "AUT", "Belgium": "BEL", "Bulgaria": "BGR", "Croatia": "HRV", "Cyprus": "CYP",
    "Czech Republic": "CZE", "Denmark": "DNK", "Estonia": "EST", "Finland": "FIN", "France": "FRA",
    "Germany": "DEU", "Greece": "GRC", "Hungary": "HUN", "Ireland": "IRL", "Italy": "ITA",
    "Latvia": "LVA", "Lithuania": "LTU", "Luxembourg": "LUX", "Malta": "MLT", "Netherlands": "NLD",
    "Poland": "POL", "Portugal": "PRT", "Romania": "ROU", "Slovakia": "SVK", "Slovenia": "SVN",
    "Spain": "ESP", "Sweden": "SWE"
}

# 📥 Carregar dados
def load_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(f"SELECT * FROM {TABLE_NAME}", conn)
    conn.close()
    print(f"📊 {len(df)} registros carregados.")
    return df

# 🔄 Dados para Setor + Tipo de Ataque
def prepare_sector_attack_data(df):
    df["sector_abbr"] = df["sector_cleaned"].map(sector_abbreviations)
    df["attack_abbr"] = df["attack_type_cleaned"].map(attack_type_abbreviations)
    df_filtered = df.dropna(subset=["sector_abbr", "attack_abbr"]).copy()
    df_filtered["cluster_key"] = df_filtered["sector_abbr"] + " - " + df_filtered["attack_abbr"]
    df_grouped = df_filtered.groupby("cluster_key")[["total_attack_severity_norm", "cyber_intensity_norm"]].mean()
    return df_grouped

# 🔄 Dados por País
def prepare_country_data(df):
    df["country_abbr"] = df["receiver_country"].map(country_abbreviations)
    df_filtered = df.dropna(subset=["country_abbr"]).copy()
    df_grouped = df_filtered.groupby("country_abbr")[["total_attack_severity_norm", "cyber_intensity_norm"]].mean()
    return df_grouped

# 🤖 Aplicar Agglomerative Clustering ajustado automaticamente
def apply_agglomerative(data, n_clusters=4):
    n_clusters = min(n_clusters, len(data))
    model = AgglomerativeClustering(n_clusters=n_clusters, linkage="ward")
    clusters = model.fit_predict(data)
    data = data.copy()
    data["Cluster"] = clusters
    return data

# 📈 Plotar dendrograma com legenda
def plot_dendrogram(data, title, legend_text=None):
    plt.figure(figsize=(12, 8))
    linkage_matrix = sch.linkage(data, method="ward")
    sch.dendrogram(
        linkage_matrix,
        labels=data.index.tolist(),
        leaf_rotation=0,
        leaf_font_size=10,
        orientation="right",
        color_threshold=0.5 * max(linkage_matrix[:, 2]),
    )
    plt.title(title, fontsize=14, weight='bold')
    plt.xlabel("Distância")
    plt.ylabel("Grupos")
    plt.grid(axis="x", linestyle="--", alpha=0.5)

    if legend_text:
        plt.figtext(0.7, 0.15, legend_text, fontsize=10,
                    bbox={"facecolor": "white", "alpha": 0.7, "pad": 5})

    plt.tight_layout()
    plt.show()

# 💾 Salvar resultados no banco
def save_results(df_sector, df_country):
    df_sector = df_sector.copy()
    df_country = df_country.copy()

    df_sector["data_type"] = "Sector & Attack"
    df_sector["cluster_key"] = df_sector.index
    df_country["data_type"] = "Country"
    df_country["cluster_key"] = df_country.index

    final = pd.concat([
        df_sector[["total_attack_severity_norm", "cyber_intensity_norm", "data_type", "cluster_key", "Cluster"]],
        df_country[["total_attack_severity_norm", "cyber_intensity_norm", "data_type", "cluster_key", "Cluster"]]
    ])
    final.reset_index(drop=True, inplace=True)

    conn = sqlite3.connect(DB_PATH)
    final.to_sql(AGGLOMERATIVE_TABLE, conn, if_exists="replace", index=False)
    conn.close()
    print(f"✅ Resultados salvos na tabela '{AGGLOMERATIVE_TABLE}'.")

# 🚀 Execução principal
if __name__ == "__main__":
    df = load_data()

    print("🔍 Preparando dados por Setor + Ataque...")
    df_sector = prepare_sector_attack_data(df)
    df_sector_clustered = apply_agglomerative(df_sector, n_clusters=4)

    print("📈 Plotando dendrograma: Setores + Ataques")
    sector_legend = "**Setores**:\n" + "\n".join(f"{v} - {k}" for k, v in sector_abbreviations.items()) + \
                    "\n\n**Tipos de Ataque**:\n" + "\n".join(f"{v} - {k}" for k, v in attack_type_abbreviations.items())
    plot_dendrogram(df_sector, "Dendrograma - Setores e Tipos de Ataque", sector_legend)

    print("🔍 Preparando dados por País...")
    df_country = prepare_country_data(df)
    df_country_clustered = apply_agglomerative(df_country, n_clusters=4)

    print("📈 Plotando dendrograma: Países Mais Atacados")
    country_legend = "**Países**:\n" + "\n".join(f"{v} - {k}" for k, v in country_abbreviations.items())
    plot_dendrogram(df_country, "Dendrograma - Países Mais Atacados", country_legend)

    print("💾 Salvando resultados no banco...")
    save_results(df_sector_clustered, df_country_clustered)

    print("✅ Script Agglomerative finalizado com sucesso!")