import os
import sqlite3

# Diretório base do projeto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "../database/cyber_attack.db")


def reset_database():
    """Remove e recria o banco de dados."""
    if os.path.exists(DB_PATH):
        confirm = input("⚠️ O banco de dados já existe. Deseja resetá-lo? (sim/não): ")
        if confirm.lower() != "sim":
            print("❌ Reset cancelado.")
            return
        print("🛑 Resetando banco de dados...")
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Criar tabela corretamente com todas as colunas necessárias
    cursor.execute('''
    CREATE TABLE vulnerabilities (
        id TEXT PRIMARY KEY,
        pub_date TEXT,
        mod_date TEXT,
        description TEXT,
        cwe TEXT,
        reference_links TEXT,  
        base_score FLOAT,
        base_severity TEXT,
        attack_vector TEXT,
        attack_complexity TEXT,
        privileges_required TEXT,
        user_interaction TEXT,
        scope TEXT,
        impact_confidentiality TEXT,
        impact_integrity TEXT,
        impact_availability TEXT
    )
    ''')

    conn.commit()
    conn.close()
    print("✅ Banco de dados recriado com sucesso!")


if __name__ == "__main__":
    reset_database()