import sqlite3
import pandas as pd

conn = sqlite3.connect("database/cyber_attacks.db")
cursor = conn.cursor()

# 📋 Mostrar todas as tabelas do banco de dados
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("📋 Tabelas encontradas no banco:")
for t in tables:
    print(f"- {t[0]}")

# 📋 Analisando a tabela 'kmeans_named_clusters'
print("\n📋 Colunas da tabela 'kmeans_named_clusters':")
cursor.execute("PRAGMA table_info(kmeans_named_clusters);")
columns_kmeans = cursor.fetchall()
for col in columns_kmeans:
    print(f"- {col[1]}")

# 🔍 Primeiras linhas da tabela 'kmeans_named_clusters'
print("\n🔍 Primeiras linhas da tabela 'kmeans_named_clusters':")
df_kmeans = pd.read_sql("SELECT * FROM kmeans_named_clusters LIMIT 10;", conn)
print(df_kmeans.head(10))

# 📋 Analisando a tabela 'agglomerative_table'
print("\n📋 Colunas da tabela 'agglomerative_table':")
cursor.execute("PRAGMA table_info(agglomerative_table);")
columns_agglo = cursor.fetchall()
for col in columns_agglo:
    print(f"- {col[1]}")

# 🔍 Primeiras linhas da tabela 'agglomerative_table'
print("\n🔍 Primeiras linhas da tabela 'agglomerative_table':")
df_agglo = pd.read_sql("SELECT * FROM agglomerative_table LIMIT 10;", conn)
print(df_agglo.head(10))

conn.close()