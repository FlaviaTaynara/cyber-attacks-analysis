import os
import sqlite3

DB_PATH = "database/vulnerabilities.db"

# Lista de scripts
scripts = [
    "scripts/1_load_data.py",
    "scripts/2_preprocess_data.py",
    "scripts/3_pca_reduction.py",
    "scripts/4_clustering.py",
    "scripts/5.1_evaluate_kmeans.py",
    "scripts/6_visualization.py"
]


def is_database_empty():
    """Verifica se o banco de dados já está populado."""
    if not os.path.exists(DB_PATH):
        return True  # O banco de dados ainda não existe

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM vulnerabilities")
    count = cursor.fetchone()[0]
    conn.close()

    return count == 0  # Se for 0, significa que ainda está vazio


def run_script(script_name):
    """Executa um script Python e exibe o status."""
    print(f"\n🚀 Executando {script_name}...\n" + "-" * 50)
    exit_code = os.system(f"python {script_name}")

    if exit_code == 0:
        print(f"✅ {script_name} concluído com sucesso!\n" + "-" * 50)
    else:
        print(f"❌ ERRO ao executar {script_name}!\n" + "-" * 50)
        exit(1)  # Interrompe a execução se houver erro


if __name__ == "__main__":
    print("\n🔄 INICIANDO O PIPELINE DE ANÁLISE DE VULNERABILIDADES...\n" + "=" * 50)

    if is_database_empty():
        print("📡 O banco de dados está vazio. Executando `1_load_data.py` para carregar os dados...")
        run_script("scripts/1_load_data.py")
    else:
        print("✅ O banco de dados já está populado. Pulando `1_load_data.py`.")

    for script in scripts[1:]:  # Ignorando `1_load_data.py`
        run_script(script)

    print("\n🎉 PIPELINE FINALIZADO COM SUCESSO! 🎉")