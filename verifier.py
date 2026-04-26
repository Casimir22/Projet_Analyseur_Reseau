import sqlite3
conn = sqlite3.connect("analyseur_reseau.db")
cur = conn.cursor()
cur.execute("SELECT * FROM rapports")
for ligne in cur.fetchall():
    print(ligne)
conn.close()