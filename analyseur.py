import time
from collections import deque

# --- FOCUS POO : Modélisation des structures ---

class Paquet:
    """Représente l'unité de donnée circulant sur le réseau."""
    def __init__(self, id_paquet, source, destination):
        self.id = id_paquet
        self.source = source
        self.destination = destination
        self.temps_entree = time.time()

class Noeud:
    """Modélisation d'un nœud réseau (Routeur/Serveur)."""
    def __init__(self, nom, debit_max):
        self.nom = nom
        self.debit_max = debit_max  # Nombre de paquets traitables par cycle
        self.file_d_attente = deque() # File d'attente (Buffer)
        self.voisins = [] # Liens du Graphe

    def ajouter_lien(self, autre_noeud):
        """Construit le Graphe en reliant les nœuds."""
        if autre_noeud not in self.voisins:
            self.voisins.append(autre_noeud)
            autre_noeud.voisins.append(self)

    def recevoir_paquet(self, paquet):
        """Ajoute un paquet à la file d'attente."""
        self.file_d_attente.append(paquet)

    def traiter_cycle(self):
        """Simule le traitement des paquets selon le débit max."""
        traites = []
        # On ne traite que ce que le débit permet
        for _ in range(self.debit_max):
            if self.file_d_attente:
                traites.append(self.file_d_attente.popleft())
        
        # --- IDENTIFICATION DES GOULOTS D'ÉTRANGLEMENT ---
        if len(self.file_d_attente) > 3:
            print(f"!!! GOULOT D'ÉTRANGLEMENT sur {self.nom} : {len(self.file_d_attente)} paquets bloqués.")
        
        return traites

class SimulateurReseau:
    """Gère l'ensemble de la simulation et du flux de données."""
    def __init__(self):
        self.noeuds = {}

    def creer_topologie(self):
        """Crée une structure de graphe spécifique."""
        # Création des objets Noeud
        self.noeuds['PC_CLIENT'] = Noeud("PC_CLIENT", 10)
        self.noeuds['ROUTEUR_A'] = Noeud("ROUTEUR_A", 2) # Débit faible volontaire
        self.noeuds['SERVEUR_WEB'] = Noeud("SERVEUR_WEB", 10)

        # Création des liens (Graphe)
        self.noeuds['PC_CLIENT'].ajouter_lien(self.noeuds['ROUTEUR_A'])
        self.noeuds['ROUTEUR_A'].ajouter_lien(self.noeuds['SERVEUR_WEB'])

    def lancer_flux(self, nb_paquets):
        """Simule l'envoi massif de paquets du client vers le serveur."""
        print(f"--- Simulation : Envoi de {nb_paquets} paquets via ROUTEUR_A ---")
        
        for i in range(nb_paquets):
            p = Paquet(i, "PC_CLIENT", "SERVEUR_WEB")
            # Le paquet arrive au premier routeur
            self.noeuds['ROUTEUR_A'].recevoir_paquet(p)
            
            # Traitement à chaque étape
            traites = self.noeuds['ROUTEUR_A'].traiter_cycle()
            
            for p_fini in traites:
                self.noeuds['SERVEUR_WEB'].recevoir_paquet(p_fini)
                print(f"Paquet {p_fini.id} arrivé au Serveur.")

            time.sleep(0.1) # Simule le temps réel

# --- EXÉCUTION ---
if __name__ == "__main__":
    sim = SimulateurReseau()
    sim.creer_topologie()
    # On envoie 15 paquets alors que le routeur ne peut en traiter que 2 par cycle
    sim.lancer_flux(15)