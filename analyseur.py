import sqlite3
import time
from collections import deque

# --- MODÉLISATION DU RÉSEAU (POO) ---

class Paquet:
    def __init__(self, id_p):
        self.id = id_p
        self.horodatage = time.time()

class NoeudReseau:
    def __init__(self, nom, debit_max, capacite_buffer):
        self.nom = nom
        self.debit_max = debit_max
        self.capacite_buffer = capacite_buffer
        self.file_attente = deque()
        self.rejets = 0

    def recevoir_flux(self, paquet):
        """Gestion du buffer : Référence réelle à la saturation mémoire."""
        if len(self.file_attente) < self.capacite_buffer:
            self.file_attente.append(paquet)
            return True
        self.rejets += 1
        return False

    def traiter_cycle(self):
        flux_sortant = []
        for _ in range(self.debit_max):
            if self.file_attente:
                flux_sortant.append(self.file_attente.popleft())
        
        # Détection de goulot d'étranglement
        if len(self.file_attente) > 5:
            print(f" !!! GOULOT D'ÉTRANGLEMENT sur {self.nom} : {len(self.file_attente)} paquets bloqués.")
        
        return flux_sortant

class AnalyseurTrafic:
    def __init__(self):
        # Configuration technique du routeur cible
        self.routeur = NoeudReseau("ROUTEUR_A", debit_max=2, capacite_buffer=20)
        self.serveur_final = []

    def lancer_analyse(self, volume_flux):
        # 1. Injection du flux
        for i in range(volume_flux):
            p = Paquet(i)
            self.routeur.recevoir_flux(p)
        
        # 2. Traitement cycle par cycle
        while len(self.routeur.file_attente) > 0:
            paquets_traites = self.routeur.traiter_cycle()
            for p in paquets_traites:
                self.serveur_final.append(p)
                print(f" Paquet {p.id} arrive au Serveur.")
            time.sleep(0.02)

        # 3. Calcul des métriques finales
        nb_recus = len(self.serveur_final)
        taux_perte = ((volume_flux - nb_recus) / volume_flux) * 100
        self.archiver_et_presenter(volume_flux, nb_recus, taux_perte)

    def archiver_et_presenter(self, env, rec, perte):
        # --- PERSISTANCE SQLITE (BLOC 4) ---
        conn = sqlite3.connect("analyseur_reseau.db")
        cur = conn.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS rapports 
                      (id INTEGER PRIMARY KEY, date TEXT, env INTEGER, rec INTEGER, perte REAL, alerte TEXT)''')
        
        alerte_statut = "true" if perte > 5 else "false"
        cur.execute("INSERT INTO rapports (date, env, rec, perte, alerte) VALUES (?,?,?,?,?)",
                    (time.strftime('%H:%M:%S'), env, rec, perte, alerte_statut))
        conn.commit()
        conn.close()

        # AFFICHAGE
        print("\n" + "═"*55)
        print(" " * 12 + "RAPPORT D'ANALYSE DE FLUX RÉSEAU")
        print("═"*55)
        print(f" HORODATAGE           : {time.strftime('%d/%m/%Y | %H:%M:%S')}")
        print(f" NB_PAQUETS_ENVOYES   : {env}")
        print(f" NB_PAQUETS_RECUS     : {rec}")
        print(f" TAUX_PERTE           : {perte:.2f}%")
        print("-" * 55)
        
        if alerte_statut == "true":
            print(f" ALERTE_CRITIQUE      : {alerte_statut.upper()} (Surcharge détectée)")
        else:
            print(f" ALERTE_CRITIQUE      : {alerte_statut.upper()} (Flux stable)")
            
        
if __name__ == "__main__":
    analyseur = AnalyseurTrafic()
    # Test  à 100 paquets pour démontrer l'alerte critique
    analyseur.lancer_analyse(100)