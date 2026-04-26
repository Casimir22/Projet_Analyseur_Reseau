import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading
from analyseur import AnalyseurTrafic, ErreurVolumeInvalide


# =============================================================================
# INTERFACE GRAPHIQUE (TKINTER)


class InterfaceAnalyseur(tk.Tk):
    """Interface graphique du simulateur de trafic réseau."""

    def __init__(self):
        super().__init__()
        self.title("Analyseur de Trafic Réseau — Université de Parakou")
        self.geometry("700x600")
        self.resizable(False, False)
        self.configure(bg="#1e1e2e")
        self._construire_interface()

    def _construire_interface(self):
        """Construit tous les widgets de l'interface."""

        # --- TITRE ---
        titre = tk.Label(
            self,
            text="ANALYSEUR DE TRAFIC RÉSEAU SIMULÉ",
            font=("Courier", 14, "bold"),
            bg="#1e1e2e",
            fg="#00ff99"
        )
        titre.pack(pady=15)

        sous_titre = tk.Label(
            self,
            text="PROJET 10",
            font=("Courier", 9),
            bg="#1e1e2e",
            fg="#888888"
        )
        sous_titre.pack()

        # --- SÉPARATEUR ---
        tk.Frame(self, bg="#00ff99", height=1).pack(fill="x", padx=20, pady=10)

        # --- SCHÉMA DU RÉSEAU ---
        schema = tk.Label(
            self,
            text="PC_CLIENT  ──►  ROUTEUR_A  ──►  SERVEUR_WEB",
            font=("Courier", 10, "bold"),
            bg="#1e1e2e",
            fg="#ffaa00"
        )
        schema.pack(pady=5)

        # --- SÉPARATEUR ---
        tk.Frame(self, bg="#333355", height=1).pack(fill="x", padx=20, pady=8)

        # --- ZONE DE PARAMÈTRE ---
        frame_param = tk.Frame(self, bg="#1e1e2e")
        frame_param.pack(pady=5)

        tk.Label(
            frame_param,
            text="Nombre de paquets à envoyer :",
            font=("Courier", 10),
            bg="#1e1e2e",
            fg="#ffffff"
        ).grid(row=0, column=0, padx=10)

        self.champ_volume = tk.Entry(
            frame_param,
            font=("Courier", 11),
            width=10,
            bg="#2e2e3e",
            fg="#00ff99",
            insertbackground="#00ff99",
            justify="center"
        )
        self.champ_volume.insert(0, "100")
        self.champ_volume.grid(row=0, column=1, padx=10)

        # --- BOUTON LANCER ---
        self.bouton_lancer = tk.Button(
            self,
            text="LANCER LA SIMULATION",
            font=("Courier", 11, "bold"),
            bg="#00ff99",
            fg="#1e1e2e",
            activebackground="#00cc77",
            cursor="hand2",
            padx=20,
            pady=8,
            command=self._lancer_simulation
        )
        self.bouton_lancer.pack(pady=15)

        #ZONE D'AFFICHAGE 
        tk.Label(
            self,
            text="RAPPORT DE SIMULATION :",
            font=("Courier", 9, "bold"),
            bg="#1e1e2e",
            fg="#888888"
        ).pack(anchor="w", padx=25)

        self.zone_texte = scrolledtext.ScrolledText(
            self,
            font=("Courier", 9),
            bg="#0d0d1a",
            fg="#00ff99",
            insertbackground="#00ff99",
            width=80,
            height=16,
            state="disabled"
        )
        self.zone_texte.pack(padx=20, pady=5)

        # BOUTON EFFACER
        tk.Button(
            self,
            text="Effacer",
            font=("Courier", 9),
            bg="#2e2e3e",
            fg="#888888",
            cursor="hand2",
            command=self._effacer
        ).pack(pady=5)

    def _ecrire(self, texte):
        """Écrit du texte coloré dans la zone d'affichage."""
        self.zone_texte.configure(state="normal")

        # Coloration automatique selon le contenu
        if "REJET" in texte or "SATURÉ" in texte or "GOULOT" in texte:
            self.zone_texte.tag_config("orange", foreground="#ffaa00")
            self.zone_texte.insert(tk.END, texte + "\n", "orange")
        elif "ALERTE" in texte and "FALSE" not in texte:
            self.zone_texte.tag_config("rouge", foreground="#ff4444")
            self.zone_texte.insert(tk.END, texte + "\n", "rouge")
        elif "FALSE" in texte or "stable" in texte:
            self.zone_texte.tag_config("vert_clair", foreground="#00ff99")
            self.zone_texte.insert(tk.END, texte + "\n", "vert_clair")
        elif "PERTE" in texte and "5%" not in texte:
            self.zone_texte.tag_config("rouge", foreground="#ff4444")
            self.zone_texte.insert(tk.END, texte + "\n", "rouge")
        else:
            self.zone_texte.insert(tk.END, texte + "\n")

        self.zone_texte.configure(state="disabled")
        self.zone_texte.see(tk.END)

    def _effacer(self):
        """Efface la zone d'affichage."""
        self.zone_texte.configure(state="normal")
        self.zone_texte.delete(1.0, tk.END)
        self.zone_texte.configure(state="disabled")

    def _lancer_simulation(self):
        """Lance la simulation dans un thread séparé."""
        try:
            volume = int(self.champ_volume.get())
        except ValueError:
            messagebox.showerror(
                "Erreur",
                "Veuillez entrer un nombre entier valide."
            )
            return

        self._effacer()
        self.bouton_lancer.configure(
            state="disabled",
            text=" Simulation en cours..."
        )
        self._ecrire("=" * 55)
        self._ecrire("  Simulation lancée avec {} paquets...".format(volume))
        self._ecrire("=" * 55)

        thread = threading.Thread(
            target=self._executer_simulation,
            args=(volume,),
            daemon=True
        )
        thread.start()

    def _executer_simulation(self, volume):
        """Exécute la simulation et affiche les résultats."""
        import io
        import sys

        capture = io.StringIO()
        sys.stdout = capture

        try:
            analyseur = AnalyseurTrafic()
            analyseur.lancer_analyse(volume)
        except ErreurVolumeInvalide as e:
            sys.stdout = sys.__stdout__
            self.after(0, lambda: messagebox.showerror("Erreur", str(e)))
        except Exception as e:
            sys.stdout = sys.__stdout__
            self.after(0, lambda: messagebox.showerror("Erreur inattendue", str(e)))
        finally:
            sys.stdout = sys.__stdout__
            sortie = capture.getvalue()

            for ligne in sortie.splitlines():
                self.after(0, lambda l=ligne: self._ecrire(l))

            self.after(
                500,
                lambda: self.bouton_lancer.configure(
                    state="normal",
                    text="▶  LANCER LA SIMULATION"
                )
            )


# =============================================================================
# POINT D'ENTRÉE
# =============================================================================

if __name__ == "__main__":
    app = InterfaceAnalyseur()
    app.mainloop()