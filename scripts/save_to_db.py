import sqlite3

DB_PATH = "../database/vulnerabilities.db"


def save_to_db(vulnerabilities):
    """Salva vulnerabilidades no banco de dados."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for item in vulnerabilities:
        cve_id = item["cve"]["CVE_data_meta"]["ID"]
        pub_date = item.get("publishedDate", "N/A")
        mod_date = item.get("lastModifiedDate", "N/A")
        cvss_v3 = item.get("impact", {}).get("baseMetricV3", {}).get("cvssV3", {}).get("baseScore", None)
        cvss_severity = item.get("impact", {}).get("baseMetricV3", {}).get("cvssV3", {}).get("baseSeverity", "N/A")
        cwe = item.get("cve", {}).get("problemtype", {}).get("problemtype_data", [{}])[0].get("description", [{}])[
            0].get("value", "N/A")
        description = item.get("cve", {}).get("description", {}).get("description_data", [{}])[0].get("value", "N/A")
        references = ", ".join(
            [ref["url"] for ref in item.get("cve", {}).get("references", {}).get("reference_data", [])])
        cpe = ", ".join([match["cpe23Uri"] for node in item.get("configurations", {}).get("nodes", []) for match in
                         node.get("cpe_match", [])])

        cursor.execute('''
            INSERT OR IGNORE INTO vulnerabilities (id, pub_date, mod_date, cvss, cvss_severity, cwe, description, references, cpe)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (cve_id, pub_date, mod_date, cvss_v3, cvss_severity, cwe, description, references, cpe))

    conn.commit()
    conn.close()
    print(f"✅ {len(vulnerabilities)} CVEs salvos no banco de dados!")
