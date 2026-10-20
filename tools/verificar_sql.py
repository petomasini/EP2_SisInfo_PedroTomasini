"""Executa consultas SQL no db.sqlite3 e salva resultados reproduziveis."""
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUERIES = ROOT / "docs" / "sql" / "consultas.sql"
OUTPUT = ROOT / "docs" / "sql" / "resultados.json"


def read_queries():
    lines = QUERIES.read_text(encoding="utf-8").splitlines()
    queries = []
    current = []
    for line in lines:
        if not line.strip() or line.lstrip().startswith("--"):
            continue
        current.append(line)
        if ";" in line:
            queries.append("\n".join(current).strip())
            current = []
    if current:
        raise ValueError("Consulta SQL sem ponto e virgula")
    return queries


def execute():
    con = sqlite3.connect(ROOT / "db.sqlite3")
    results = []
    try:
        for i, sql in enumerate(read_queries(), 1):
            cursor = con.execute(sql)
            rows = cursor.fetchall()
            results.append({"id": i, "sql": sql, "columns": [d[0] for d in cursor.description], "rows": rows, "total": len(rows)})
        assert [r["total"] for r in results] == [3, 2, 2, 3, 1], [r["total"] for r in results]
        assert con.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        assert not con.execute("PRAGMA foreign_key_check").fetchall()
        return results
    finally:
        con.close()


if __name__ == "__main__":
    results = execute()
    OUTPUT.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    for r in results:
        print(f"Consulta {r['id']}: {r['total']} linha(s). Colunas: {', '.join(r['columns'])}")
    print(f"Resultado completo: {OUTPUT}")
