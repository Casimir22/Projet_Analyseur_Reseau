from flask import Flask, render_template, request
from analyseur import AnalyseurTrafic
import sqlite3

app = Flask(__name__)
analyseur = AnalyseurTrafic()


@app.route("/", methods=["GET", "POST"])
def index():
    message = ""
    stats = None
    historique = []

    if request.method == "POST":
        volume = int(request.form["volume"])
        analyseur.lancer_analyse(volume)
        message = f"Simulation de {volume} paquets terminée ✔️"

    # Lire historique SQLite
    try:
        conn = sqlite3.connect("analyseur_reseau.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM rapports ORDER BY id DESC LIMIT 5")
        historique = cur.fetchall()
        conn.close()
    except:
        pass

    return render_template("index.html",
                           message=message,
                           historique=historique)


if __name__ == "__main__":
    app.run(debug=True)