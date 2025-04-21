#
# import sqlite3
# import pandas as pd
# import numpy as np
# import re
# from sklearn.preprocessing import StandardScaler
#
# # 📂 Caminho do banco de dados
# DB_PATH = "../database/cyber_attacks.db"
# TABLE_NAME = "cyber_incidents_processed"
#
# # 📊 Lista de países da União Europeia para filtragem
# EU_COUNTRIES = {
#     "Austria", "Belgium", "Bulgaria", "Croatia", "Cyprus", "Czech Republic", "Denmark",
#     "Estonia", "Finland", "France", "Germany", "Greece", "Hungary", "Ireland", "Italy",
#     "Latvia", "Lithuania", "Luxembourg", "Malta", "Netherlands", "Poland", "Portugal",
#     "Romania", "Slovakia", "Slovenia", "Spain", "Sweden"
# }
#
# # 🔄 Mapas de mapeamento para tags numéricas
# sector_mapping = {
#     "Government": 1, "Military": 2, "Health": 3, "Finance": 4,
#     "Energy": 5, "Telecom": 6, "Transport": 7, "Education": 8,
#     "Critical infrastructure": 9, "Other": 10
# }
#
# attack_type_mapping = {
#     "Data theft": 1, "Disruption": 2, "Hijacking": 3, "Ransomware": 4,
#     "Phishing": 5, "DDoS": 6, "Malware": 7, "Unknown": 8
# }
#
# attacker_category_mapping = {
#     "Hacktivists": 1, "State-sponsored": 2, "Cybercriminals": 3,
#     "Insiders": 4, "Terrorists": 5, "Unknown": 6, "Other": 7
# }
#
#
# # 📥 Carregar dados do banco de dados
# def load_data():
#     conn = sqlite3.connect(DB_PATH)
#     df = pd.read_sql("SELECT * FROM cyber_incidents", conn)
#     conn.close()
#     print(f"📊 Loaded {len(df)} records from database.")
#     return df
#
#
# # 🔍 Filtrar apenas países da União Europeia
# def filter_eu_countries(df):
#     df["is_eu"] = df["receiver_country"].apply(lambda x: any(country in EU_COUNTRIES for country in str(x).split("; ")))
#     df = df[df["is_eu"]]
#     print(f"✅ Filtered {len(df)} records from EU countries.")
#     return df
#
#
# # 🔄 Limpar e corrigir receiver_category_subcode
# def clean_receiver_category(df):
#     print("\n🔍 Limpando receiver_category_subcode...")
#
#     regex_letters = re.compile(r"[a-zA-Z]")
#
#     def clean_category(row):
#         subcode = str(row["receiver_category_subcode"]).strip() if pd.notna(row["receiver_category_subcode"]) else ""
#         category = str(row["receiver_category"]).strip() if pd.notna(row["receiver_category"]) else ""
#
#         if not regex_letters.search(subcode):
#             return category.split(";")[0].strip() if ";" in category else category
#         else:
#             return subcode.split(";")[0].strip() if ";" in subcode else subcode
#
#     df["receiver_category_final"] = df.apply(clean_category, axis=1)
#
#     print("✅ receiver_category_subcode limpo e corrigido!")
#     return df
#
#
# # 🔄 Separar múltiplos valores e contar ocorrências
# def split_multiple_values(df):
#     print("\n🔍 Separando múltiplos valores...")
#
#     for col in ["sector_cleaned", "attack_type_cleaned", "attacker_category_cleaned", "receiver_category_final"]:
#         df[f"{col}_primary"] = df[col].str.split(" - ").str[0]  # Pega o primeiro valor
#         df[f"{col}_count"] = df[col].str.count(" - ") + 1
#
#     print("✅ Valores separados e contagem adicionada!")
#     return df
#
#
# # 🔄 Criar tags numéricas para impact_indicator
# def create_impact_tag(df):
#     print("\n🔍 Criando tags para impact_indicator...")
#
#     impact_mapping = {
#         "Not available": -1, "none": -1, "Blanks": -1,
#         "Low": 1, "Minor": 1, "Medium": 2
#     }
#
#     if "impact_indicator" not in df.columns:
#         df["impact_indicator"] = "Not available"
#
#     df["impact_indicator_tag"] = df["impact_indicator"].map(impact_mapping).fillna(0).astype(int)
#
#     print("✅ Criadas tags numéricas para impact_indicator!")
#     return df
#
#
# # 🔄 Criar colunas de tags numéricas
# def create_tags(df):
#     print("\n🔍 Criando tags numéricas...")
#
#     df["sector_tag"] = df["sector_cleaned_primary"].map(sector_mapping).fillna(0).astype(int)
#     df["attack_type_tag"] = df["attack_type_cleaned_primary"].map(attack_type_mapping).fillna(0).astype(int)
#     df["attacker_category_tag"] = df["attacker_category_cleaned_primary"].map(attacker_category_mapping).fillna(
#         0).astype(int)
#
#     print("✅ Tags numéricas criadas!")
#     return df
#
#
# # 🔄 Criar atributos compostos
# def create_composite_attributes(df):
#     df["cyber_intensity"] = df["unweighted_cyber_intensity"].fillna(0) * df["weighted_cyber_intensity"].fillna(0)
#     df["total_attack_severity"] = df["impact_indicator_value"].fillna(0) * df["impact_indicator_tag"].fillna(0)
#
#     print("✅ Criados atributos compostos!")
#     return df
#
#
# # 🔄 Normalizar os valores numéricos
# def normalize_data(df):
#     print("\n🔍 Normalizando dados...")
#
#     required_columns = ["sector_tag", "attack_type_tag", "attacker_category_tag"]
#
#     # Verificando se as colunas necessárias estão presentes
#     missing_columns = [col for col in required_columns if col not in df.columns]
#     if missing_columns:
#         raise KeyError(f"As seguintes colunas estão faltando antes da normalização: {missing_columns}")
#
#     num_cols = ["impact_indicator_value", "unweighted_cyber_intensity",
#                 "weighted_cyber_intensity", "sector_tag", "attack_type_tag",
#                 "attacker_category_tag", "impact_indicator_tag",
#                 "total_attack_severity", "cyber_intensity"]
#
#     scaler = StandardScaler()
#     df[[col + "_norm" for col in num_cols]] = scaler.fit_transform(df[num_cols])
#
#     print("✅ Normalização concluída!")
#     return df
#
#
# # 💾 Salvar no banco de dados
# def save_to_db(df):
#     conn = sqlite3.connect(DB_PATH)
#     df.to_sql(TABLE_NAME, conn, if_exists="replace", index=False)
#     conn.close()
#     print(f"✅ {len(df)} incidents processed and saved!")
#
#
# # 🚀 Executar pipeline
# if __name__ == "__main__":
#     print("📊 Carregando dados...")
#     df = load_data()
#
#     print("🔄 Filtrando países da UE...")
#     df = filter_eu_countries(df)
#
#     print("🔄 Limpando receiver_category_subcode...")
#     df = clean_receiver_category(df)
#
#     print("🔄 Separando valores compostos...")
#     df = split_multiple_values(df)
#
#     print("🔄 Criando tags para impact_indicator...")
#     df = create_impact_tag(df)
#
#     print("🔄 Criando colunas de tags numéricas...")
#     df = create_tags(df)  # ✅ Agora é chamado corretamente!
#
#     print("🔄 Criando atributos compostos...")
#     df = create_composite_attributes(df)
#
#     print("🔄 Normalizando dados...")
#     df = normalize_data(df)
#
#     print("💾 Salvando os dados processados no banco...")
#     save_to_db(df)
#
#

import sqlite3
import pandas as pd
import numpy as np
import re
from sklearn.preprocessing import StandardScaler

# 💂 Caminho do banco de dados
DB_PATH = "../database/cyber_attacks.db"
TABLE_NAME = "cyber_incidents_processed"

# 📊 Lista de países da União Europeia para filtragem
EU_COUNTRIES = {
    "Austria", "Belgium", "Bulgaria", "Croatia", "Cyprus", "Czech Republic", "Denmark",
    "Estonia", "Finland", "France", "Germany", "Greece", "Hungary", "Ireland", "Italy",
    "Latvia", "Lithuania", "Luxembourg", "Malta", "Netherlands", "Poland", "Portugal",
    "Romania", "Slovakia", "Slovenia", "Spain", "Sweden"
}

# 🔄 Mapas de mapeamento para tags numéricas
sector_mapping = {
    "Government": 1, "Military": 2, "Health": 3, "Finance": 4,
    "Energy": 5, "Telecom": 6, "Transport": 7, "Education": 8,
    "Critical infrastructure": 9, "Other": 10
}

attack_type_mapping = {
    "Data theft": 1, "Disruption": 2, "Hijacking": 3, "Ransomware": 4,
    "Phishing": 5, "DDoS": 6, "Malware": 7, "Unknown": 8
}

attacker_category_mapping = {
    "Hacktivists": 1, "State-sponsored": 2, "Cybercriminals": 3,
    "Insiders": 4, "Terrorists": 5, "Unknown": 6, "Other": 7
}

# 📅 Carregar dados do banco de dados
def load_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM cyber_incidents", conn)
    conn.close()
    print(f"📊 {len(df)} registros carregados do banco de dados.")
    return df

# 🔍 Filtrar apenas países da União Europeia
def filter_eu_countries(df):
    df["is_eu"] = df["receiver_country"].apply(lambda x: any(country in EU_COUNTRIES for country in str(x).split("; ")))
    df = df[df["is_eu"]]
    print(f"✅ {len(df)} registros filtrados para países da UE.")
    return df

# 🔄 Criar tags numéricas para impact_indicator
def create_impact_tag(df):
    impact_mapping = {
        "Not available": -1, "none": -1, "Blanks": -1,
        "Low": 1, "Minor": 1, "Medium": 2
    }
    df["impact_indicator_tag"] = df["impact_indicator"].map(impact_mapping).fillna(0).astype(int)
    print("✅ Criadas tags numéricas para impact_indicator!")
    return df

# 🔄 Criar colunas de tags numéricas
def create_tags(df):
    df["sector_tag"] = df["sector_cleaned"].map(sector_mapping).fillna(0).astype(int)
    df["attack_type_tag"] = df["attack_type_cleaned"].map(attack_type_mapping).fillna(0).astype(int)
    df["attacker_category_tag"] = df["attacker_category_cleaned"].map(attacker_category_mapping).fillna(0).astype(int)
    print("✅ Tags numéricas criadas!")
    return df

# 🔄 Criar atributos compostos
def create_composite_attributes(df):
    df["cyber_intensity"] = df["unweighted_cyber_intensity"].fillna(0) * df["weighted_cyber_intensity"].fillna(0)
    df["total_attack_severity"] = df["impact_indicator_value"].fillna(0) * df["impact_indicator_tag"].fillna(0)
    print("✅ Criados atributos compostos!")
    return df

# 🔄 Normalizar os valores numéricos
def normalize_data(df):
    num_cols = ["impact_indicator_value", "unweighted_cyber_intensity", "weighted_cyber_intensity",
                "sector_tag", "attack_type_tag", "attacker_category_tag", "impact_indicator_tag",
                "total_attack_severity", "cyber_intensity"]
    scaler = StandardScaler()
    df[[col + "_norm" for col in num_cols]] = scaler.fit_transform(df[num_cols])
    print("✅ Normalização concluída!")
    return df

# 📂 Salvar no banco de dados
def save_to_db(df):
    conn = sqlite3.connect(DB_PATH)
    df.to_sql(TABLE_NAME, conn, if_exists="replace", index=False)
    conn.close()
    print(f"✅ {len(df)} incidents processados e salvos!")

# ⚡ Executar pipeline
if __name__ == "__main__":
    print("📊 Carregando dados...")
    df = load_data()

    print("🔄 Filtrando países da UE...")
    df = filter_eu_countries(df)

    print("🔄 Criando tags para impact_indicator...")
    df = create_impact_tag(df)

    print("🔄 Criando colunas de tags numéricas...")
    df = create_tags(df)

    print("🔄 Criando atributos compostos...")
    df = create_composite_attributes(df)

    print("🔄 Normalizando dados...")
    df = normalize_data(df)

    print("💾 Salvando os dados processados no banco...")
    save_to_db(df)
