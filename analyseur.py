import time
from scapy.all import sniff

# 1. Classe Paquet : Structure des données
class Paquet:
    def __init__(self, source, destination):
        self.source = source
        self.destination = destination
        self.temps_creation = time.time()

    def __str__(self):
        return f"Paquet IP : {self.source} ---> {self.destination}"

# 2. Classe Reseau : Gestion du trafic et FIFO
class Reseau:
    def __init__(self):
        self.file_d_attente = []
        self.capacite_max = 15
        self.paquets_recus = 0
        self.paquets_perdus = 0

    def analyser(self, pkt):
        if pkt.haslayer("IP"):
            source = pkt["IP"].src
            destination = pkt["IP"].dst
            nouveau_paquet = Paquet(source, destination)
            print(f" Traitement : {nouveau_paquet}") 
            
            self.paquets_recus += 1
            self.paquets_recus += 1

            # Vérification de la capacité (FIFO)
            if len(self.file_d_attente) < self.capacite_max:
                self.file_d_attente.append(nouveau_paquet)
                
                # Alerte de congestion à 80% (exigence cahier de charge)
                if len(self.file_d_attente) >= (self.capacite_max * 0.8):
                    print(f"  Machine débordée ({len(self.file_d_attente)}/50)")
                
                # Traitement FIFO : on retire le premier arrivé
                self.file_d_attente.pop(0)
            else:
                self.paquets_perdus += 1
                print(" Perte de données : File saturée")

# 3. Classe Simulation : Pilotage et Bilan
class Simulation:
    def __init__(self):
        self.mon_reseau = Reseau()

    def lancer(self, limite=20):
        print(" DEMARRAGE DE LA SIMULATION (BLOC 3)")
        # Capture du trafic avec Scapy
        sniff(prn=self.mon_reseau.analyser, store=False, count=limite)
        self.affichage_resultats()

    def affichage_resultats(self):
        total = self.mon_reseau.paquets_recus
        perdus = self.mon_reseau.paquets_perdus
        taux = (perdus / total * 100) if total > 0 else 0
        
        print("\n" + "="*30)
        print("      BILAN FINAL")
        print("="*30)
        print(f"Paquets totaux  : {total}")
        print(f"Paquets perdus  : {perdus}")
        print(f"Taux de perte   : {taux:.2f}%")
        print("="*30)

# Bloc principal d'exécution
if __name__ == "__main__":
    ma_simu = Simulation()
    ma_simu.lancer(limite=20)