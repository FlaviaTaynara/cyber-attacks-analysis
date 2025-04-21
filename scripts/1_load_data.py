
import os
import sqlite3
import pandas as pd

# 📂 Definir caminhos do arquivo e banco de dados
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "../data/eurepoc.csv")
DB_PATH = os.path.join(BASE_DIR, "../database/cyber_attacks.db")

# 🔄 Colunas relevantes
COLUMNS_TO_KEEP = [
    "ID", "start_date", "incident_type", "receiver_country", "receiver_category", "receiver_category_subcode",
    "MITRE_impact", "unweighted_cyber_intensity", "target_multiplier",
    "weighted_cyber_intensity", "impact_indicator", "impact_indicator_value"
]


# 🛠️ Criar estrutura do banco de dados
def create_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cyber_incidents (
        ID INTEGER PRIMARY KEY,
        start_date TEXT,
        year INTEGER,
        incident_type TEXT,
        receiver_country TEXT,
        receiver_category TEXT,
        receiver_category_subcode TEXT,
        MITRE_impact TEXT,
        unweighted_cyber_intensity REAL,
        target_multiplier TEXT,
        weighted_cyber_intensity REAL,
        impact_indicator TEXT,
        impact_indicator_value REAL,
        sector_cleaned TEXT,
        attack_type_cleaned TEXT,
        attacker_category_cleaned TEXT
    )
    ''')

    conn.commit()
    conn.close()

# 📥 Carregar e limpar os dados
def load_data():
    print("📂 Carregando dados do arquivo CSV...")

    try:
        df = pd.read_csv(DATA_PATH, usecols=COLUMNS_TO_KEEP, encoding="utf-8")

        # 📅 Criar coluna para o ano
        df["start_date"] = pd.to_datetime(df["start_date"], errors="coerce")
        df["year"] = df["start_date"].dt.year

        # 🏷️ Criar colunas limpas para categorização
        df["sector_cleaned"] = df["receiver_category"].str.split(";").str[0].str.strip()
        df["attack_type_cleaned"] = df["incident_type"].str.split(";").str[0].str.strip()
        df["attacker_category_cleaned"] = df["receiver_category_subcode"].str.split(";").str[0].str.strip()

        # 💾 Salvar no banco de dados
        conn = sqlite3.connect(DB_PATH)
        df.to_sql("cyber_incidents", conn, if_exists="replace", index=False)
        conn.close()

        print(f"✅ {len(df)} incidentes carregados e salvos no banco!")

    except Exception as e:
        print(f"❌ ERRO ao carregar CSV: {e}")

# 🚀 Executar
if __name__ == "__main__":
    create_database()
    load_data()