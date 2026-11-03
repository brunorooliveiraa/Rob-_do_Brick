import sqlite3

conn = sqlite3.connect("bric_hunter.db")
c = conn.cursor()
c.execute("SELECT id, titulo_bruto, url_anuncio, eh_oportunidade FROM tabela_processados WHERE url_anuncio LIKE '%999999%'")
rows = c.fetchall()
print("Registros de teste encontrados:", rows)

if rows:
    c.execute("DELETE FROM tabela_processados WHERE url_anuncio LIKE '%999999%'")
    conn.commit()
    print("Registros de teste removidos com sucesso!")

conn.close()
