import tkinter as tk
from tkinter import ttk
from analyseur import AnalyseurTrafic, ErreurNoeudInexistant, ErreurVolumeInvalide


class InterfacePro:
    def __init__(self, root):
        self.root = root
        self.root.title("Analyseur Réseau PRO")
        self.root.geometry("950x650")
        self.root.configure(bg="#1e1e2f")

        self.analyseur = AnalyseurTrafic()

        # ================= STYLE =================
        style = ttk.Style()
        style.theme_use("default")

        style.configure("Treeview",
                        background="#2e2e3e",
                        foreground="white",
                        rowheight=25,
                        fieldbackground="#2e2e3e")

        style.configure("Treeview.Heading",
                        font=("Arial", 10, "bold"))

        # ================= TITRE =================
        tk.Label(root,
                 text="📡 Analyseur de Flux Réseau",
                 font=("Arial", 20, "bold"),
                 bg="#1e1e2f",
                 fg="#00d4ff").pack(pady=10)

        # ================= PARAMÈTRES =================
        frame_param = tk.LabelFrame(root,
                                    text="Paramètres utilisateur",
                                    bg="#1e1e2f",
                                    fg="white")
        frame_param.pack(pady=10, fill="x", padx=20)

        tk.Label(frame_param, text="Paquets :", bg="#1e1e2f", fg="white").grid(row=0, column=0, padx=5, pady=5)
        self.entree = tk.Entry(frame_param)
        self.entree.insert(0, "50")
        self.entree.grid(row=0, column=1)

        tk.Label(frame_param, text="Source :", bg="#1e1e2f", fg="white").grid(row=0, column=2)
        self.source_entry = tk.Entry(frame_param)
        self.source_entry.insert(0, "PC1")
        self.source_entry.grid(row=0, column=3)

        tk.Label(frame_param, text="Destination :", bg="#1e1e2f", fg="white").grid(row=0, column=4)
        self.dest_entry = tk.Entry(frame_param)
        self.dest_entry.insert(0, "SERVEUR_WEB")
        self.dest_entry.grid(row=0, column=5)

        # Nœuds valides affichés sous les champs
        noeuds = ", ".join(self.analyseur.noeuds_disponibles())
        tk.Label(frame_param,
                 text=f"Nœuds valides : {noeuds}",
                 bg="#1e1e2f",
                 fg="#aaaaaa",
                 font=("Arial", 8)).grid(row=1, column=0, columnspan=6, pady=(0, 5))

        # ================= BOUTONS =================
        frame_btn = tk.Frame(root, bg="#1e1e2f")
        frame_btn.pack(pady=10)

        tk.Button(frame_btn,
                  text="▶ Lancer Simulation",
                  bg="#00d4ff",
                  fg="black",
                  font=("Arial", 10, "bold"),
                  command=self.lancer).pack(side=tk.LEFT, padx=5)

        tk.Button(frame_btn,
                  text="📊 Voir Statistiques",
                  bg="#4caf50",
                  fg="white",
                  font=("Arial", 10, "bold"),
                  command=self.afficher_stats).pack(side=tk.LEFT, padx=5)

        tk.Button(frame_btn,
                  text="🧹 Reset",
                  bg="#f44336",
                  fg="white",
                  font=("Arial", 10, "bold"),
                  command=self.clear).pack(side=tk.LEFT, padx=5)

        # ================= TABLE =================
        frame_table = tk.Frame(root)
        frame_table.pack(pady=10)

        colonnes = ("Nom", "Type", "Recus", "Rejets", "Buffer")

        self.table = ttk.Treeview(frame_table,
                                  columns=colonnes,
                                  show="headings",
                                  height=8)

        for col in colonnes:
            self.table.heading(col, text=col)
            self.table.column(col, width=120, anchor="center")

        self.table.pack()

        # ================= ZONE TEXTE =================
        self.texte = tk.Text(root,
                             height=15,
                             width=110,
                             bg="#0f172a",
                             fg="white")
        self.texte.pack(pady=10)

        # Styles texte
        self.texte.tag_config("titre",   font=("Arial", 16, "bold"), foreground="cyan")
        self.texte.tag_config("section", font=("Arial", 12, "bold"), foreground="yellow")
        self.texte.tag_config("ok",      foreground="lightgreen")
        self.texte.tag_config("erreur",  foreground="#ff6b6b")
        self.texte.tag_config("warning", foreground="orange")

        # Affichage initial des stats vides
        self.afficher_stats()

    # ================= ACTIONS =================

    def lancer(self):
        self.texte.delete("1.0", tk.END)

        try:
            valeur = self.entree.get().strip()

            # Validation volume
            if not valeur or not valeur.lstrip("-").isdigit():
                raise ErreurVolumeInvalide(
                    "Le nombre de paquets doit être un entier positif (ex: 50, 100, 500)."
                )

            volume = int(valeur)

            source      = self.source_entry.get().strip().upper()
            destination = self.dest_entry.get().strip().upper()

            # Validation source/destination vides
            if not source:
                raise ErreurNoeudInexistant("(vide)", self.analyseur.noeuds_disponibles())
            if not destination:
                raise ErreurNoeudInexistant("(vide)", self.analyseur.noeuds_disponibles())

            # Lancement
            res = self.analyseur.lancer_analyse(volume, source, destination)

            self.afficher_resultats(res)
            self.afficher_stats()

        except ErreurVolumeInvalide as e:
            self.texte.insert(tk.END, f"❌ Volume invalide : {e}\n", "erreur")

        except ErreurNoeudInexistant as e:
            self.texte.insert(tk.END, f"❌ {e}\n", "erreur")

        except Exception as e:
            self.texte.insert(tk.END, f"❌ Erreur inattendue : {e}\n", "erreur")

    def afficher_resultats(self, res):
        self.texte.insert(tk.END, "🎯 RESULTAT FINAL\n", "titre")

        self.texte.insert(tk.END, "\n👉 Paramètres utilisateur\n", "section")
        self.texte.insert(tk.END, f"\n   Paquets     : {res['envoyes']}")
        self.texte.insert(tk.END, f"\n   Source      : {res['source']}")
        self.texte.insert(tk.END, f"\n   Destination : {res['destination']}\n")

        self.texte.insert(tk.END, "\n👉 Résultats simulation\n", "section")
        self.texte.insert(tk.END, f"\n   Envoyés : {res['envoyes']}")
        self.texte.insert(tk.END, f"\n   Reçus   : {res['recus']}")
        self.texte.insert(tk.END, f"\n   Perdus  : {res['perdus']}")
        self.texte.insert(tk.END, f"\n   Taux    : {res['taux']} %")
        self.texte.insert(tk.END, f"\n   Temps   : {res['temps']} ms\n")

        self.texte.insert(tk.END, "\n🚨 Analyse réseau\n", "section")

        if res["goulots"]:
            for g in res["goulots"]:
                self.texte.insert(tk.END, f"\n   ⚠  {g}", "warning")
        else:
            self.texte.insert(tk.END, "\n   ✅ Aucun goulot détecté", "ok")

        self.texte.insert(tk.END, "\n\n✔ Simulation terminée\n", "ok")

    def afficher_stats(self):
        # Vider la table
        for row in self.table.get_children():
            self.table.delete(row)

        # Remplir avec les stats actuelles
        stats = self.analyseur.statistiques()

        for s in stats:
            self.table.insert("", tk.END, values=(
                s["nom"],
                s["type"],
                s["total_recus"],
                s["rejets"],
                s["occupation"]
            ))

    def clear(self):
        self.texte.delete("1.0", tk.END)

        # Reset complet du réseau
        self.analyseur.reseau.reset()

        # Rafraîchir la table avec les zéros
        self.afficher_stats()

        self.texte.insert(tk.END, "✔ Réseau remis à zéro.\n", "ok")


# ================= LANCEMENT =================

if __name__ == "__main__":
    root = tk.Tk()
    app = InterfacePro(root)
    root.mainloop()