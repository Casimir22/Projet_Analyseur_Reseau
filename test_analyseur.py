import pytest
from analyseur import (
    Paquet,
    Lien,
    NoeudReseau,
    AnalyseurTrafic,
    ErreurVolumeInvalide,
    ErreurBufferSature,
)


# =============================================================================
# TESTS DE LA CLASSE Paquet
# =============================================================================

def test_paquet_creation():
    """Un paquet doit avoir un id, une source et une destination."""
    p = Paquet(1, "PC_CLIENT", "SERVEUR_WEB")
    assert p.id == 1
    assert p.source == "PC_CLIENT"
    assert p.destination == "SERVEUR_WEB"


# =============================================================================
# TESTS DE LA CLASSE NoeudReseau
# =============================================================================

def test_noeud_reception_normale():
    """Un nœud doit accepter un paquet si le buffer n'est pas plein."""
    noeud = NoeudReseau("TEST", debit_max=2, capacite_buffer=5)
    p = Paquet(1, "A", "B")
    resultat = noeud.recevoir_flux(p)
    assert resultat is True
    assert len(noeud.file_attente) == 1


def test_noeud_buffer_sature():
    """Un nœud plein doit lever ErreurBufferSature."""
    noeud = NoeudReseau("TEST", debit_max=2, capacite_buffer=2)
    noeud.recevoir_flux(Paquet(1, "A", "B"))
    noeud.recevoir_flux(Paquet(2, "A", "B"))
    with pytest.raises(ErreurBufferSature):
        noeud.recevoir_flux(Paquet(3, "A", "B"))


def test_noeud_traiter_cycle():
    """traiter_cycle doit retourner les paquets selon le débit max."""
    noeud = NoeudReseau("TEST", debit_max=2, capacite_buffer=10)
    noeud.recevoir_flux(Paquet(1, "A", "B"))
    noeud.recevoir_flux(Paquet(2, "A", "B"))
    noeud.recevoir_flux(Paquet(3, "A", "B"))
    traites = noeud.traiter_cycle()
    assert len(traites) == 2
    assert len(noeud.file_attente) == 1


def test_noeud_taux_occupation():
    """Le taux d'occupation doit être calculé correctement."""
    noeud = NoeudReseau("TEST", debit_max=2, capacite_buffer=10)
    noeud.recevoir_flux(Paquet(1, "A", "B"))
    noeud.recevoir_flux(Paquet(2, "A", "B"))
    assert noeud.taux_occupation_buffer() == 20.0


def test_noeud_est_deborde():
    """Un nœud est débordé si son buffer dépasse 80%."""
    noeud = NoeudReseau("TEST", debit_max=2, capacite_buffer=10)
    for i in range(9):
        noeud.recevoir_flux(Paquet(i, "A", "B"))
    assert noeud.est_deborde() is True


# =============================================================================
# TESTS DE LA CLASSE Lien
# =============================================================================

def test_lien_transmission_normale():
    """Un lien doit transmettre un paquet vers le nœud destination."""
    source = NoeudReseau("SOURCE", debit_max=5, capacite_buffer=10)
    dest = NoeudReseau("DEST", debit_max=5, capacite_buffer=10)
    lien = Lien(source, dest, capacite_max=3)
    p = Paquet(1, "SOURCE", "DEST")
    resultat = lien.transmettre(p)
    assert resultat is True
    assert len(dest.file_attente) == 1


def test_lien_sature():
    """Un lien saturé doit retourner False."""
    source = NoeudReseau("SOURCE", debit_max=5, capacite_buffer=10)
    dest = NoeudReseau("DEST", debit_max=5, capacite_buffer=10)
    lien = Lien(source, dest, capacite_max=1)
    lien.transmettre(Paquet(1, "SOURCE", "DEST"))
    resultat = lien.transmettre(Paquet(2, "SOURCE", "DEST"))
    assert resultat is False


def test_lien_taux_utilisation():
    """Le taux d'utilisation doit être calculé correctement."""
    source = NoeudReseau("SOURCE", debit_max=5, capacite_buffer=10)
    dest = NoeudReseau("DEST", debit_max=5, capacite_buffer=10)
    lien = Lien(source, dest, capacite_max=4)
    lien.transmettre(Paquet(1, "SOURCE", "DEST"))
    lien.transmettre(Paquet(2, "SOURCE", "DEST"))
    assert lien.taux_utilisation() == 50.0


# =============================================================================
# TESTS DE LA CLASSE AnalyseurTrafic
# =============================================================================

def test_volume_invalide_zero():
    """lancer_analyse(0) doit lever ErreurVolumeInvalide."""
    analyseur = AnalyseurTrafic()
    with pytest.raises(ErreurVolumeInvalide):
        analyseur.lancer_analyse(0)


def test_volume_invalide_negatif():
    """lancer_analyse(-5) doit lever ErreurVolumeInvalide."""
    analyseur = AnalyseurTrafic()
    with pytest.raises(ErreurVolumeInvalide):
        analyseur.lancer_analyse(-5)


def test_volume_invalide_string():
    """lancer_analyse('abc') doit lever ErreurVolumeInvalide."""
    analyseur = AnalyseurTrafic()
    with pytest.raises(ErreurVolumeInvalide):
        analyseur.lancer_analyse("abc")