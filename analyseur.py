from scapy.all import sniff, conf 
#Configuration pour Windows(évite les  erreur de socket)
conf.L3socket = conf.L3socket
#1. Classe Paquet : Definit la structure des donnée capturées 
class Paquet :
    def __init__(self,source,destination):
      self.source = source
      self.destination = destination
    def __str__(self):
            # Cette ligne transforme l'objet en texte lisible
        return f"Paquet IP : {self.source} ---> {self.destination}"
class Reseau :
    def __init__(self):
        self.compteur = 0  
    def analyser(self,pkt):
        if pkt.haslayer("IP"):
                  # On crée un objet de notre classe Paquet 
                    nouveau_p = Paquet(pkt["IP"].src, pkt["IP"].dst)
                    print(f"[POO] {nouveau_p}")
                    self.compteur +=1
#3. Classe Simulation : Pilote l'exécution du programme 
class Simulation:
    def __init__(self):
        self.mon_reseau = Reseau()

    def lancer(self, limite=30):   
         print("DEMARRAGE DE LA SIMULATION")
        
         sniff(prn=self.mon_reseau.analyser, store=False, count=limite)
if __name__ == "__main__":
    ma_simu = Simulation()
    ma_simu.lancer()
                             
                                                        