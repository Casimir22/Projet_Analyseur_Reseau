import time
import random
import json
from collections import deque

class ErreurVolumeInvalide(ValueError):
    pass

class ErreurBufferSature(Exception):
    pass

class ErreurNoeudInexistant(Exception):
    def __init__(self, nom="", noeuds_valides=None):
        self.nom = nom
        self.noeuds_valides = noeuds_valides or []
        if self.noeuds_valides:
            msg = (f"Nœud invalide : '{nom}'. "
                    f"Nœuds disponibles : {', '.join(self.noeuds_valides)}")
        else:
            msg = f"Nœud invalide : '{nom}'"
        super().__init__(msg)


class Paquet:
    def __init__(self, id_p, source, destination):
        self.id = id_p
        self.source = source
        self.destination = destination
        self.chemin = []
        self.arrive = False


class NoeudReseau:
    def __init__(self, nom, type_noeud_ou_debit=None, debit_max=None, capacite_buffer=None):
        self.nom = nom

        if isinstance(type_noeud_ou_debit, str):
            self.type_noeud      = type_noeud_ou_debit
            self.debit_max       = debit_max
            self.capacite_buffer = capacite_buffer
        else:
            self.type_noeud      = "PC"
            self.debit_max       = type_noeud_ou_debit if type_noeud_ou_debit is not None else debit_max
            self.capacite_buffer = capacite_buffer if capacite_buffer is not None else 30

        self.file_attente = deque()
        self.rejets       = 0
        self.total_recus  = 0
        self.voisins      = []

    def reset(self):
        self.file_attente = deque()
        self.rejets       = 0
        self.total_recus  = 0

    def ajouter_voisin(self, lien):
        self.voisins.append(lien)

    def recevoir_flux(self, paquet):
        if len(self.file_attente) >= self.capacite_buffer:
            self.rejets += 1
            raise ErreurBufferSature()
        self.file_attente.append(paquet)
        self.total_recus += 1
        return True

    def traiter(self):
        return self.traiter_cycle()

    def traiter_cycle(self):
        flux = []
        for _ in range(self.debit_max):
            if self.file_attente:
                flux.append(self.file_attente.popleft())
        return flux

    def taux_occupation_buffer(self):
        return (len(self.file_attente) / self.capacite_buffer) * 100

    def est_deborde(self):
        return len(self.file_attente) >= self.capacite_buffer * 0.8


class Lien:
    def __init__(self, noeud_a, noeud_b, capacite_max):
        self.noeud_a         = noeud_a
        self.noeud_b         = noeud_b
        self.capacite_max    = capacite_max
        self.charge_actuelle = 0
        self.total_transmis  = 0

    def reset(self):
        self.charge_actuelle = 0
        self.total_transmis  = 0

    def transmettre(self, paquet):
        if random.random() < 0.00005:
            return False
        if self.charge_actuelle >= self.capacite_max:
            return False

        self.charge_actuelle += 1
        self.total_transmis  += 1
        paquet.chemin.append(self.noeud_b.nom)

        try:
            self.noeud_b.recevoir_flux(paquet)
        except ErreurBufferSature:
            self.charge_actuelle -= 1
            return False

        return True

    def taux_utilisation(self):
        return (self.charge_actuelle / self.capacite_max) * 100

    def est_sature(self):
        return self.charge_actuelle >= self.capacite_max * 0.8


class ReseauGraphe:
    def __init__(self):
        self.noeuds = {}
        self.liens  = []

    def ajouter_noeud(self, noeud):
        self.noeuds[noeud.nom] = noeud

    def ajouter_lien(self, a, b, cap):
        if a not in self.noeuds:
            raise ErreurNoeudInexistant(a, list(self.noeuds.keys()))
        if b not in self.noeuds:
            raise ErreurNoeudInexistant(b, list(self.noeuds.keys()))
        lien = Lien(self.noeuds[a], self.noeuds[b], cap)
        self.noeuds[a].ajouter_voisin(lien)
        self.liens.append(lien)

    def get_noeud(self, nom):
        if nom not in self.noeuds:
            raise ErreurNoeudInexistant(nom, list(self.noeuds.keys()))
        return self.noeuds[nom]

    def reset(self):
        for n in self.noeuds.values():
            n.reset()
        for l in self.liens:
            l.reset()

    def statistiques(self):
        stats = []
        for n in self.noeuds.values():
            stats.append({
                "nom":         n.nom,
                "type":        n.type_noeud,
                "total_recus": n.total_recus,
                "rejets":      n.rejets,
                "occupation":  f"{n.taux_occupation_buffer():.1f}%"
            })
        return stats


SEUIL_GOULOT = 200


class AnalyseurTrafic:

    def __init__(self):
        self._build()

    def _build(self):
        self.reseau = ReseauGraphe()

        for n in [
            NoeudReseau("PC1",         "PC",      50,  500),
            NoeudReseau("PC2",         "PC",      50,  500),
            NoeudReseau("PC3",         "PC",      50,  500),
            NoeudReseau("WIFI",        "WIFI",    50,  500),
            NoeudReseau("ROUTEUR_A",   "ROUTEUR", 100, 1000),
            NoeudReseau("ROUTEUR_B",   "ROUTEUR", 100, 1000),
            NoeudReseau("SERVEUR_WEB", "SERVEUR", 500, 5000),
        ]:
            self.reseau.ajouter_noeud(n)

        self.reseau.ajouter_lien("PC1",       "ROUTEUR_A",    500)
        self.reseau.ajouter_lien("PC2",       "ROUTEUR_A",    500)
        self.reseau.ajouter_lien("ROUTEUR_A", "SERVEUR_WEB",  1000)
        self.reseau.ajouter_lien("PC3",       "WIFI",         300)
        self.reseau.ajouter_lien("WIFI",      "ROUTEUR_B",    300)
        self.reseau.ajouter_lien("ROUTEUR_B", "SERVEUR_WEB",  500)

    def lancer_analyse(self, volume_flux, source="PC1", destination="SERVEUR_WEB"):

        if not isinstance(volume_flux, int) or isinstance(volume_flux, bool) or volume_flux <= 0:
            raise ErreurVolumeInvalide(
                "Le nombre de paquets doit être un entier positif (ex: 50, 100, 500)."
            )

        noeuds_valides = list(self.reseau.noeuds.keys())

        if source not in self.reseau.noeuds:
            raise ErreurNoeudInexistant(source, noeuds_valides)

        if destination not in self.reseau.noeuds:
            raise ErreurNoeudInexistant(destination, noeuds_valides)

        if source == destination:
            raise ErreurVolumeInvalide(
                "La source et la destination doivent être différentes."
            )

        # Reset avant chaque simulation
        self.reseau.reset()

        noeud_source = self.reseau.get_noeud(source)
        debut = time.time()

        # ── PHASE 1 : ENVOI 
        for i in range(volume_flux):
            paquet = Paquet(i, source, destination)
            paquet.chemin.append(source)
            if noeud_source.voisins:
                lien = random.choice(noeud_source.voisins)
                lien.transmettre(paquet)

        # ── VÉRIFICATION GOULOTS AU PIC DE CHARGE 
        goulots = []
        if volume_flux >= SEUIL_GOULOT:
            for n in self.reseau.noeuds.values():
                if n.est_deborde():
                    goulots.append(n.nom)
            for l in self.reseau.liens:
                if l.est_sature():
                    goulots.append(f"{l.noeud_a.nom}->{l.noeud_b.nom}")

        # ── PHASE 2 : PROPAGATION 
        for _ in range(volume_flux // 2 + 50):
            for noeud in self.reseau.noeuds.values():
                flux = noeud.traiter_cycle()
                for p in flux:
                    if p.chemin and p.chemin[-1] == destination:
                        p.arrive = True
                        continue
                    if noeud.voisins:
                        lien = min(noeud.voisins, key=lambda l: l.charge_actuelle)
                        lien.transmettre(p)
            time.sleep(0.001)

        temps_total = round((time.time() - debut) * 1000, 2)

        # ── RÉSULTATS 
        dest   = self.reseau.get_noeud(destination)
        recus  = dest.total_recus
        perdus = max(0, volume_flux - recus)
        taux   = (perdus / volume_flux) * 100

        resultats = {
            "envoyes":      volume_flux,
            "recus":        recus,
            "perdus":       perdus,
            "taux":         round(taux, 2),
            "source":       source,
            "destination":  destination,
            "temps":        temps_total,
            "goulots":      goulots,
            "seuil_goulot": SEUIL_GOULOT,
            "statistiques": self.reseau.statistiques(),
        }

        try:
            with open("resultats_simulation.json", "w", encoding="utf-8") as f:
                json.dump(resultats, f, ensure_ascii=False, indent=2)
        except OSError:
            pass

        return resultats

    def statistiques(self):
        return self.reseau.statistiques()

    def noeuds_disponibles(self):
        return list(self.reseau.noeuds.keys())



def lancer_analyse():
    print("\n╔══════════════════════════════════════╗")
    print("║    Analyseur de Flux Réseau      ║")
    print("╚══════════════════════════════════════╝\n")

    analyseur = AnalyseurTrafic()
    print(f"Nœuds disponibles : {', '.join(analyseur.noeuds_disponibles())}\n")
    print(f"ℹ️  Détection des goulots active à partir de {SEUIL_GOULOT} paquets.\n")

    try:
        volume      = int(input("Nombre de paquets à envoyer : "))
        source      = input("Source      : ").strip().upper()
        destination = input("Destination : ").strip().upper()

        print("\n⏳ Simulation en cours...\n")
        r = analyseur.lancer_analyse(volume, source, destination)

        print("╔══════════════════════════════════════╗")
        print("║        Résultats simulation          ║")
        print("╚══════════════════════════════════════╝")
        print(f"  Envoyés  : {r['envoyes']}")
        print(f"  Reçus    : {r['recus']}")
        print(f"  Perdus   : {r['perdus']}")
        print(f"  Taux     : {r['taux']} %")
        print(f"  Temps    : {r['temps']} ms")

        if volume < SEUIL_GOULOT:
            print(f"\nℹ️  Augmentez à {SEUIL_GOULOT}+ paquets pour détecter les goulots.")
        elif r["goulots"]:
            print("\n⚠  Goulots détectés :")
            for g in r["goulots"]:
                print(f"   ▲  {g}")
        else:
            print("\n✔  Aucun goulot détecté.")

        print("\n── Statistiques par nœud ──")
        for s in r["statistiques"]:
            print(f"  {s['nom']:15} | Reçus: {s['total_recus']:4} | "
                  f"Rejets: {s['rejets']:3} | Buffer: {s['occupation']}")

        print("\n✔  Simulation terminée.")
        

    except ErreurVolumeInvalide as e:
        print(f"❌ Erreur volume : {e}")
    except ErreurNoeudInexistant as e:
        print(f"❌ {e}")
    except ValueError:
        print("❌ Erreur : veuillez entrer un nombre entier valide.")


if __name__ == "__main__":
    lancer_analyse()