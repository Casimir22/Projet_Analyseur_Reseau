import sqlite3
import time
from collections import deque


# =============================================================================
# BLOC 5 — EXCEPTIONS PERSONNALISÉES
# =============================================================================

class ErreurVolumeInvalide(ValueError):
    """Levée quand le volume de paquets est invalide (<=0)."""
    pass


class ErreurBufferSature(Exception):
    """Levée quand le buffer d'un nœud est totalement saturé."""
    pass


class ErreurBaseDeDonnees(Exception):
    """Levée en cas d'échec lors de l'archivage SQLite."""
    pass


# =============================================================================
# MODÉLISATION DU RÉSEAU (POO)
# =============================================================================

class Paquet:
    """Représente l'unité de donnée circulant sur le réseau."""

    def __init__(self, id_p, source, destination):
        self.id = id_p
        self.source = source
        self.destination = destination
        self.horodatage = time.time()


class Lien:
    """Connexion entre deux nœuds avec capacité maximale."""

    def __init__(self, noeud_a, noeud_b, capacite_max):
        self.noeud_a = noeud_a
        self.noeud_b = noeud_b
        self.capacite_max = capacite_max
        self.charge_actuelle = 0

    def taux_utilisation(self):
        if self.capacite_max == 0:
            return 0.0
        return (self.charge_actuelle / self.capacite_max) * 100

    def est_sature(self):
        return self.taux_utilisation() > 90

    def transmettre(self, paquet):
        if self.charge_actuelle >= self.capacite_max:
            return False
        self.charge_actuelle += 1
        self.noeud_b.recevoir_flux(paquet)
        return True

    def reinitialiser_charge(self):
        self.charge_actuelle = 0


class NoeudReseau:
    """Modélise un nœud réseau. Gère un buffer FIFO."""

    def __init__(self, nom, debit_max, capacite_buffer):
        self.nom = nom
        self.debit_max = debit_max
        self.capacite_buffer = capacite_buffer
        self.file_attente = deque()
        self.rejets = 0
        self.total_recus = 0

    def recevoir_flux(self, paquet):
        if len(self.file_attente) >= self.capacite_buffer:
            self.rejets += 1
            raise ErreurBufferSature(
                f"Buffer de '{self.nom}' saturé "
                f"({self.capacite_buffer}/{self.capacite_buffer} paquets)."
            )
        self.file_attente.append(paquet)
        self.total_recus += 1
        return True

    def taux_occupation_buffer(self):
        return (len(self.file_attente) / self.capacite_buffer) * 100

    def est_deborde(self):
        return self.taux_occupation_buffer() > 80

    def traiter_cycle(self):
        flux_sortant = []
        for _ in range(self.debit_max):
            if self.file_attente:
                flux_sortant.append(self.file_attente.popleft())

        if self.est_deborde():
            print(
                f"  !!! GOULOT D'ÉTRANGLEMENT sur {self.nom} : "
                f"{len(self.file_attente)} paquets bloqués "
                f"({self.taux_occupation_buffer():.1f}% du buffer)."
            )
        return flux_sortant


# =============================================================================
# SIMULATEUR PRINCIPAL
# =============================================================================

class AnalyseurTrafic:
    """Orchestre la simulation complète du trafic réseau."""

    def __init__(self):
        self.pc_client = NoeudReseau("PC_CLIENT", debit_max=10, capacite_buffer=50)
        self.routeur = NoeudReseau("ROUTEUR_A", debit_max=2, capacite_buffer=20)
        self.serveur = NoeudReseau("SERVEUR_WEB", debit_max=10, capacite_buffer=50)

        self.lien_client_routeur = Lien(self.pc_client, self.routeur, capacite_max=5)
        self.lien_routeur_serveur = Lien(self.routeur, self.serveur, capacite_max=5)

        self.paquets_envoyes = 0
        self.temps_transmission = []

    def lancer_analyse(self, volume_flux):
        if not isinstance(volume_flux, int) or volume_flux <= 0:
            raise ErreurVolumeInvalide(
                f"Le volume doit être un entier > 0. Reçu : {volume_flux!r}"
            )

        self.paquets_envoyes = volume_flux
        print(f"\n  Simulation : Envoi de {volume_flux} paquets "
              f"PC_CLIENT → ROUTEUR_A → SERVEUR_WEB\n")

        # 1. Injection du flux
        for i in range(volume_flux):
            paquet = Paquet(i, "PC_CLIENT", "SERVEUR_WEB")
            try:
                transmis = self.lien_client_routeur.transmettre(paquet)
                if not transmis:
                    print(f"  [LIEN SATURÉ] Paquet {i} bloqué sur le lien.")
                    self.routeur.rejets += 1
            except ErreurBufferSature as e:
                print(f"  [REJET] Paquet {i} perdu — {e}")

        # 2. Traitement cycle par cycle
        while len(self.routeur.file_attente) > 0:
            self.lien_client_routeur.reinitialiser_charge()
            paquets_traites = self.routeur.traiter_cycle()

            for p in paquets_traites:
                try:
                    transmis = self.lien_routeur_serveur.transmettre(p)
                    if transmis:
                        duree = time.time() - p.horodatage
                        self.temps_transmission.append(duree)
                        print(f"  Paquet {p.id} arrivé au SERVEUR_WEB.")
                except ErreurBufferSature as e:
                    print(f"  [REJET SERVEUR] Paquet {p.id} perdu — {e}")

            self.lien_routeur_serveur.reinitialiser_charge()
            time.sleep(0.02)

        # 3. Métriques finales
        nb_recus = self.serveur.total_recus
        taux_perte = ((volume_flux - nb_recus) / volume_flux) * 100
        temps_moyen = (
            sum(self.temps_transmission) / len(self.temps_transmission)
            if self.temps_transmission else 0.0
        )
        self.archiver_et_presenter(volume_flux, nb_recus, taux_perte, temps_moyen)

    def archiver_et_presenter(self, env, rec, perte, temps_moyen):
        alerte_statut = "true" if perte > 5 else "false"

        try:
            conn = sqlite3.connect("analyseur_reseau.db")
            cur = conn.cursor()
            cur.execute(
                '''CREATE TABLE IF NOT EXISTS rapports
                   (id INTEGER PRIMARY KEY, date TEXT, env INTEGER,
                    rec INTEGER, perte REAL, temps_moyen REAL, alerte TEXT)'''
            )
            cur.execute(
                "INSERT INTO rapports "
                "(date, env, rec, perte, temps_moyen, alerte) VALUES (?,?,?,?,?,?)",
                (time.strftime('%H:%M:%S'), env, rec, perte,
                 temps_moyen, alerte_statut)
            )
            conn.commit()
        except sqlite3.Error as e:
            raise ErreurBaseDeDonnees(
                f"Échec de l'archivage SQLite : {e}"
            ) from e
        finally:
            conn.close()

        # Détection des problèmes
        alertes = []
        if self.lien_client_routeur.est_sature():
            alertes.append(
                f"   CÂBLE SATURÉ : Lien PC→Routeur à "
                f"{self.lien_client_routeur.taux_utilisation():.1f}% (seuil 90%)"
            )
        if self.lien_routeur_serveur.est_sature():
            alertes.append(
                f"   CÂBLE SATURÉ : Lien Routeur→Serveur à "
                f"{self.lien_routeur_serveur.taux_utilisation():.1f}% (seuil 90%)"
            )
        if self.routeur.est_deborde():
            alertes.append(
                f"    MACHINE DÉBORDÉE : ROUTEUR_A à "
                f"{self.routeur.taux_occupation_buffer():.1f}% (seuil 80%)"
            )
        if perte > 5:
            alertes.append(
                f"   PERTE ÉLEVÉE : {perte:.2f}% de paquets perdus (seuil 5%)"
            )

        # Affichage rapport
        print("\n" + "="*55)
        print(" " * 12 + "RAPPORT D'ANALYSE DE FLUX RÉSEAU")
        print("="*55)
        print(f"  HORODATAGE          : {time.strftime('%d/%m/%Y | %H:%M:%S')}")
        print(f"  NB_PAQUETS_ENVOYES  : {env}")
        print(f"  NB_PAQUETS_RECUS    : {rec}")
        print(f"  TAUX_PERTE          : {perte:.2f}%")
        print(f"  TEMPS_MOYEN_TRANS   : {temps_moyen:.4f}s")
        print("-" * 55)

        if alertes:
            print("  ALERTES DÉTECTÉES :")
            for alerte in alertes:
                print(alerte)
        else:
            print("  ALERTE_CRITIQUE : FALSE ✓ (Flux stable)")

        print("="*55 + "\n")


# =============================================================================
# POINT D'ENTRÉE
# =============================================================================

if __name__ == "__main__":
    analyseur = AnalyseurTrafic()
    analyseur.lancer_analyse(100)