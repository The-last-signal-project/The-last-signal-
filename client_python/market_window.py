"""
Fenêtre du marché (touche S).

Deux onglets :

    Acheter : liste des ventes des autres joueurs, avec recherche
              (nom, type, rareté, rang, prix, durabilité, enchantement,
              caractéristiques de potion) ; on sélectionne une vente, on
              choisit la quantité puis on confirme l'achat.

    Vendre  : inventaire du joueur avec un bouton « Sélectionner » par
              objet ; les objets choisis passent dans « Objets à vendre »
              (quantité et prix modifiables) ; « Valider la vente »
              demande une confirmation avant l'envoi. En dessous, les
              ventes en cours, que l'on peut annuler.

Réseau : la fenêtre ne connaît pas le socket. Elle reçoit une fonction
`send(dict)` qui envoie un MARKET_REQUEST, et la fenêtre de jeu lui remet
chaque MARKET_RESPONSE décodé via `handle_response(dict)`.

Les requêtes et réponses sont décrites dans `network/market_api.rs`.
"""

from __future__ import annotations

from typing import Callable

from PySide6.QtCore import QRegularExpression, Qt, QTimer
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)


# =================================================================
# OUTILS D'AFFICHAGE (sans Qt, faciles à tester)
# =================================================================

TYPES_OBJET = [
    ("Tous les types", None),
    ("Armes", "armes"),
    ("Équipements", "equipment"),
    ("Livres enchantés", "enchanted_book"),
    ("Potions", "potion"),
    ("Minerais", "mineral"),
    ("Matériaux", "material"),
    ("Consommables", "consumable"),
    ("Objets basiques", "basic"),
    ("Munitions", "muni"),
]

TRIS = [
    ("Prix croissant", "prix_asc"),
    ("Prix décroissant", "prix_desc"),
    ("Nom", "nom"),
    ("Durabilité décroissante", "durabilite_desc"),
]

# Réponse attendue du serveur (en secondes) avant d'abandonner l'attente
DELAI_REPONSE_MS = 10_000


def format_nombre(valeur) -> str:
    """12345678 -> '12 345 678'."""

    try:
        return f"{int(valeur):,}".replace(",", " ")
    except (TypeError, ValueError):
        return "?"


def entier_ou_none(texte: str) -> int | None:
    """Champ numérique vide ou invalide = pas de filtre."""

    texte = (texte or "").strip().replace(" ", "")

    if not texte:
        return None

    try:
        return int(texte)
    except ValueError:
        return None


def texte_ou_none(texte: str) -> str | None:

    texte = (texte or "").strip()

    return texte or None


def prix_conseille(objet: dict) -> int:
    """Prix du marché si le serveur le connaît, sinon prix du catalogue."""

    valeur = objet.get("prix_conseille")

    if valeur is None:
        valeur = objet.get("prix_base", 0)

    try:
        return int(valeur)
    except (TypeError, ValueError):
        return 0


def durabilite_texte(objet: dict) -> str:

    courante = objet.get("durabilite")

    if courante is None:
        return ""

    maximale = objet.get("durabilite_max")

    if maximale is None:
        return str(courante)

    return f"{courante} / {maximale}"


def details_objet(objet: dict) -> str:
    """Rareté, rang, niveau de livre, potion et enchantements sur une ligne."""

    morceaux: list[str] = []

    rarete = objet.get("rarete")
    rang = objet.get("rang")

    if rarete or rang:
        morceaux.append(
            "[" + " - ".join(str(x) for x in (rarete, rang) if x) + "]"
        )

    if objet.get("niveau_livre") is not None:
        morceaux.append(f"Livre niv. {objet['niveau_livre']}")

    if objet.get("effet"):
        morceaux.append(str(objet["effet"]))

    if objet.get("puissance") is not None and objet.get("effet"):
        morceaux.append(f"puissance {objet['puissance']}")

    if objet.get("duree") is not None and objet.get("effet"):
        morceaux.append(f"durée {objet['duree']}")

    enchantements = objet.get("enchantements") or []

    if enchantements:
        morceaux.append(", ".join(enchantements))

    return "  ".join(morceaux)


def _cellule(texte: str, droite: bool = False) -> QTableWidgetItem:

    cellule = QTableWidgetItem(texte)

    cellule.setFlags(cellule.flags() & ~Qt.ItemIsEditable)

    if droite:
        cellule.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

    return cellule


def _champ_entier(placeholder: str, largeur: int = 90) -> QLineEdit:
    """Champ qui n'accepte que des chiffres (les prix peuvent dépasser 32 bits)."""

    champ = QLineEdit()

    champ.setPlaceholderText(placeholder)
    champ.setMaximumWidth(largeur)
    champ.setValidator(
        QRegularExpressionValidator(QRegularExpression(r"\d{0,18}"))
    )

    return champ


def _table(colonnes: list[str]) -> QTableWidget:

    table = QTableWidget(0, len(colonnes))

    table.setHorizontalHeaderLabels(colonnes)
    table.setSelectionBehavior(QAbstractItemView.SelectRows)
    table.setSelectionMode(QAbstractItemView.SingleSelection)
    table.setEditTriggers(QAbstractItemView.NoEditTriggers)
    table.verticalHeader().setVisible(False)
    table.horizontalHeader().setStretchLastSection(False)
    table.horizontalHeader().setSectionResizeMode(
        QHeaderView.ResizeToContents
    )

    return table


# =================================================================
# FENÊTRE
# =================================================================

class MarketDialog(QDialog):
    """Fenêtre du marché : onglets Acheter et Vendre."""

    ACTIONS_QUI_MODIFIENT = ("buy", "sell", "cancel_sale")

    def __init__(self, send: Callable[[dict], None], parent=None) -> None:
        super().__init__(parent)

        self.send = send

        self.setWindowTitle("Marché  (Échap pour fermer)")
        self.setWindowModality(Qt.ApplicationModal)
        self.resize(980, 660)

        # Données reçues
        self._ventes: list[dict] = []
        self._inventaire: list[dict] = []
        self._mes_ventes: list[dict] = []

        # Objets choisis dans l'onglet Vendre : stuff_id -> widgets
        self._selection: dict[int, dict] = {}
        self._boutons_inventaire: dict[int, QPushButton] = {}

        # Requêtes envoyées dont on attend la réponse
        self._en_attente: set[str] = set()

        self._delai = QTimer(self)
        self._delai.setSingleShot(True)
        self._delai.timeout.connect(self._delai_depasse)

        self._construire()
        self._maj_boutons()

    # -------------------------------------------------------------
    # MESSAGES (remplaçables dans les tests)
    # -------------------------------------------------------------

    def confirmer(self, titre: str, texte: str) -> bool:

        reponse = QMessageBox.question(
            self,
            titre,
            texte,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        return reponse == QMessageBox.Yes

    def informer(self, titre: str, texte: str) -> None:

        QMessageBox.information(self, titre, texte)

    def avertir(self, titre: str, texte: str) -> None:

        QMessageBox.warning(self, titre, texte)

    # -------------------------------------------------------------
    # CONSTRUCTION
    # -------------------------------------------------------------

    def _construire(self) -> None:

        racine = QVBoxLayout(self)

        haut = QHBoxLayout()

        self.lbl_argent = QLabel("Argent : ...")
        self.lbl_statut = QLabel("")

        haut.addWidget(self.lbl_argent)
        haut.addStretch(1)
        haut.addWidget(self.lbl_statut)

        racine.addLayout(haut)

        self.onglets = QTabWidget()

        self.onglets.addTab(self._construire_acheter(), "Acheter")
        self.onglets.addTab(self._construire_vendre(), "Vendre")
        self.onglets.currentChanged.connect(self._onglet_change)

        racine.addWidget(self.onglets)

    # --- Onglet Acheter -------------------------------------------

    def _construire_acheter(self) -> QWidget:

        page = QWidget()
        disposition = QVBoxLayout(page)

        filtres = QGroupBox("Rechercher")
        grille = QGridLayout(filtres)

        self.e_nom = QLineEdit()
        self.e_nom.setPlaceholderText("nom de l'objet")

        self.c_type = QComboBox()
        for libelle, valeur in TYPES_OBJET:
            self.c_type.addItem(libelle, valeur)

        self.c_tri = QComboBox()
        for libelle, valeur in TRIS:
            self.c_tri.addItem(libelle, valeur)

        self.e_rarete = QLineEdit()
        self.e_rarete.setPlaceholderText("ex. Rare")
        self.e_rang = QLineEdit()
        self.e_rang.setPlaceholderText("ex. B")
        self.e_enchantement = QLineEdit()
        self.e_enchantement.setPlaceholderText("nom d'enchantement")

        self.e_prix_min = _champ_entier("min")
        self.e_prix_max = _champ_entier("max")
        self.e_dura_min = _champ_entier("min")
        self.e_dura_max = _champ_entier("max")

        self.e_effet = QLineEdit()
        self.e_effet.setPlaceholderText("effet de potion")
        self.e_puissance = _champ_entier("min")
        self.e_duree = _champ_entier("min")

        grille.addWidget(QLabel("Nom"), 0, 0)
        grille.addWidget(self.e_nom, 0, 1)
        grille.addWidget(QLabel("Type"), 0, 2)
        grille.addWidget(self.c_type, 0, 3)
        grille.addWidget(QLabel("Trier par"), 0, 4)
        grille.addWidget(self.c_tri, 0, 5)

        grille.addWidget(QLabel("Rareté"), 1, 0)
        grille.addWidget(self.e_rarete, 1, 1)
        grille.addWidget(QLabel("Rang"), 1, 2)
        grille.addWidget(self.e_rang, 1, 3)
        grille.addWidget(QLabel("Enchantement"), 1, 4)
        grille.addWidget(self.e_enchantement, 1, 5)

        grille.addWidget(QLabel("Prix"), 2, 0)
        grille.addLayout(self._paire(self.e_prix_min, self.e_prix_max), 2, 1)
        grille.addWidget(QLabel("Durabilité"), 2, 2)
        grille.addLayout(self._paire(self.e_dura_min, self.e_dura_max), 2, 3)

        grille.addWidget(QLabel("Potion : effet"), 3, 0)
        grille.addWidget(self.e_effet, 3, 1)
        grille.addWidget(QLabel("Puissance"), 3, 2)
        grille.addLayout(self._paire(self.e_puissance), 3, 3)
        grille.addWidget(QLabel("Durée"), 3, 4)
        grille.addLayout(self._paire(self.e_duree), 3, 5)

        boutons = QHBoxLayout()

        self.btn_rechercher = QPushButton("Rechercher")
        self.btn_reinit = QPushButton("Réinitialiser")

        boutons.addStretch(1)
        boutons.addWidget(self.btn_reinit)
        boutons.addWidget(self.btn_rechercher)

        grille.addLayout(boutons, 4, 0, 1, 6)

        for champ in (
            self.e_nom, self.e_rarete, self.e_rang, self.e_enchantement,
            self.e_prix_min, self.e_prix_max, self.e_dura_min,
            self.e_dura_max, self.e_effet, self.e_puissance, self.e_duree,
        ):
            champ.returnPressed.connect(self.rechercher)

        self.btn_rechercher.clicked.connect(self.rechercher)
        self.btn_reinit.clicked.connect(self.reinitialiser_filtres)

        disposition.addWidget(filtres)

        self.table_ventes = _table(
            ["Objet", "Détails", "Durabilité", "Quantité",
             "Prix unitaire", "Prix du marché", "Vendeur"]
        )
        self.table_ventes.itemSelectionChanged.connect(
            self._vente_selectionnee_change
        )

        disposition.addWidget(self.table_ventes, 1)

        achat = QHBoxLayout()

        self.lbl_vente = QLabel("Sélectionnez une vente.")
        self.spin_achat = QSpinBox()
        self.spin_achat.setRange(1, 1)
        self.lbl_total_achat = QLabel("")
        self.btn_acheter = QPushButton("Acheter")

        self.spin_achat.valueChanged.connect(self._maj_total_achat)
        self.btn_acheter.clicked.connect(self.acheter)

        achat.addWidget(self.lbl_vente, 1)
        achat.addWidget(QLabel("Quantité"))
        achat.addWidget(self.spin_achat)
        achat.addWidget(self.lbl_total_achat)
        achat.addWidget(self.btn_acheter)

        disposition.addLayout(achat)

        return page

    @staticmethod
    def _paire(*champs: QLineEdit) -> QHBoxLayout:

        ligne = QHBoxLayout()

        for index, champ in enumerate(champs):
            if index:
                ligne.addWidget(QLabel("à"))
            ligne.addWidget(champ)

        ligne.addStretch(1)

        return ligne

    # --- Onglet Vendre --------------------------------------------

    def _construire_vendre(self) -> QWidget:

        separateur = QSplitter(Qt.Vertical)

        # Inventaire
        boite_inv = QGroupBox("Mon inventaire")
        v_inv = QVBoxLayout(boite_inv)

        self.table_inv = _table(
            ["", "Objet", "Détails", "Durabilité", "Quantité",
             "Prix du marché"]
        )
        v_inv.addWidget(self.table_inv)

        separateur.addWidget(boite_inv)

        # Sélection
        boite_sel = QGroupBox("Objets à vendre")
        v_sel = QVBoxLayout(boite_sel)

        self.table_sel = _table(
            ["Objet", "Quantité", "Prix unitaire", "Total", ""]
        )
        v_sel.addWidget(self.table_sel)

        ligne = QHBoxLayout()

        self.lbl_total_vente = QLabel("Aucun objet sélectionné.")
        self.btn_valider = QPushButton("Valider la vente")
        self.btn_valider.clicked.connect(self.valider_vente)

        ligne.addWidget(self.lbl_total_vente, 1)
        ligne.addWidget(self.btn_valider)

        v_sel.addLayout(ligne)

        separateur.addWidget(boite_sel)

        # Mes ventes
        boite_mes = QGroupBox("Mes ventes en cours")
        v_mes = QVBoxLayout(boite_mes)

        self.table_mes = _table(
            ["Objet", "Détails", "Durabilité", "Quantité restante",
             "Prix unitaire"]
        )
        self.table_mes.itemSelectionChanged.connect(self._maj_boutons)
        v_mes.addWidget(self.table_mes)

        self.btn_annuler = QPushButton("Annuler la vente sélectionnée")
        self.btn_annuler.clicked.connect(self.annuler_vente)

        v_mes.addWidget(self.btn_annuler)

        separateur.addWidget(boite_mes)

        separateur.setSizes([220, 160, 140])

        return separateur

    # -------------------------------------------------------------
    # ENVOI
    # -------------------------------------------------------------

    def _envoyer(self, requete: dict) -> None:

        action = requete["action"]

        self._en_attente.add(action)
        self.lbl_statut.setText("En attente du serveur...")
        self._delai.start(DELAI_REPONSE_MS)

        try:
            self.send(requete)
        except Exception as exc:  # réseau coupé : on ne bloque pas l'écran
            self._en_attente.discard(action)
            self.lbl_statut.setText(f"Envoi impossible : {exc}")

        self._maj_boutons()

    def _delai_depasse(self) -> None:

        self._en_attente.clear()
        self.lbl_statut.setText("Pas de réponse du serveur.")
        self._maj_boutons()

    def demander_donnees_initiales(self) -> None:
        """À l'ouverture : première recherche (sans filtre) et solde."""

        self.rechercher()

    # -------------------------------------------------------------
    # RÉPONSES DU SERVEUR
    # -------------------------------------------------------------

    def handle_response(self, data: dict) -> None:

        action = data.get("action", "")

        self._en_attente.discard(action)

        if not self._en_attente:
            self._delai.stop()
            self.lbl_statut.setText("")

        if data.get("balance") is not None:
            self.lbl_argent.setText(
                f"Argent : {format_nombre(data['balance'])}"
            )

        if not data.get("ok"):
            self._echec(action, data.get("message", "Erreur"))
            self._maj_boutons()
            return

        if action == "search":
            self._ventes = data.get("ventes") or []
            self._remplir_ventes()

        elif action == "inventory":
            self._inventaire = data.get("items") or []
            self._remplir_inventaire()

        elif action == "my_sales":
            self._mes_ventes = data.get("ventes") or []
            self._remplir_mes_ventes()

        elif action == "buy":
            self.informer("Achat", data.get("message", "Achat effectué"))
            self.rechercher()

        elif action == "sell":
            self.informer("Vente", data.get("message", "Mis en vente"))
            self._vider_selection()
            self._demander_vente()

        elif action == "cancel_sale":
            self.informer("Vente", data.get("message", "Vente annulée"))
            self._demander_vente()

        self._maj_boutons()

    def _echec(self, action: str, message: str) -> None:

        if action in self.ACTIONS_QUI_MODIFIENT:

            self.avertir("Marché", message)

            # L'état a pu changer (vente prise, objet déplacé) : on recharge.
            if action == "buy":
                self.rechercher()
            else:
                self._demander_vente()

        else:
            self.lbl_statut.setText(message)

    # -------------------------------------------------------------
    # ACHETER
    # -------------------------------------------------------------

    def construire_filtres(self) -> dict:
        """Filtres du formulaire ; un champ vide n'est pas envoyé."""

        filtres = {
            "nom": texte_ou_none(self.e_nom.text()),
            "type": self.c_type.currentData(),
            "rarete": texte_ou_none(self.e_rarete.text()),
            "rang": texte_ou_none(self.e_rang.text()),
            "enchantement": texte_ou_none(self.e_enchantement.text()),
            "effet": texte_ou_none(self.e_effet.text()),
            "prix_min": entier_ou_none(self.e_prix_min.text()),
            "prix_max": entier_ou_none(self.e_prix_max.text()),
            "durabilite_min": entier_ou_none(self.e_dura_min.text()),
            "durabilite_max": entier_ou_none(self.e_dura_max.text()),
            "puissance_min": entier_ou_none(self.e_puissance.text()),
            "duree_min": entier_ou_none(self.e_duree.text()),
            "tri": self.c_tri.currentData(),
        }

        return {cle: valeur for cle, valeur in filtres.items()
                if valeur is not None}

    def rechercher(self) -> None:

        self._envoyer(
            {"action": "search", "filtres": self.construire_filtres()}
        )

    def reinitialiser_filtres(self) -> None:

        for champ in (
            self.e_nom, self.e_rarete, self.e_rang, self.e_enchantement,
            self.e_prix_min, self.e_prix_max, self.e_dura_min,
            self.e_dura_max, self.e_effet, self.e_puissance, self.e_duree,
        ):
            champ.clear()

        self.c_type.setCurrentIndex(0)
        self.c_tri.setCurrentIndex(0)

        self.rechercher()

    def _remplir_ventes(self) -> None:

        self.table_ventes.setRowCount(0)

        for vente in self._ventes:

            ligne = self.table_ventes.rowCount()
            self.table_ventes.insertRow(ligne)

            cellules = [
                _cellule(str(vente.get("nom", "?"))),
                _cellule(details_objet(vente)),
                _cellule(durabilite_texte(vente), droite=True),
                _cellule(format_nombre(vente.get("quantite", 0)), droite=True),
                _cellule(
                    format_nombre(vente.get("prix_unitaire", 0)), droite=True
                ),
                # Prix du marché de CET exemplaire (rareté, rang, durabilité)
                _cellule(
                    format_nombre(vente["valeur_estimee"])
                    if vente.get("valeur_estimee") is not None
                    else "",
                    droite=True,
                ),
                _cellule(str(vente.get("vendeur", ""))),
            ]

            for colonne, cellule in enumerate(cellules):
                self.table_ventes.setItem(ligne, colonne, cellule)

        if not self._ventes:
            self.lbl_statut.setText("Aucune vente ne correspond.")

        self._vente_selectionnee_change()

    def vente_selectionnee(self) -> dict | None:

        ligne = self.table_ventes.currentRow()

        if 0 <= ligne < len(self._ventes) and self.table_ventes.selectedItems():
            return self._ventes[ligne]

        return None

    def _vente_selectionnee_change(self) -> None:

        vente = self.vente_selectionnee()

        if vente is None:
            self.lbl_vente.setText("Sélectionnez une vente.")
            self.spin_achat.setRange(1, 1)
        else:
            self.lbl_vente.setText(
                f"{vente.get('nom', '?')}  {details_objet(vente)}"
            )
            self.spin_achat.setRange(1, max(1, int(vente.get("quantite", 1))))

        self._maj_total_achat()
        self._maj_boutons()

    def _maj_total_achat(self) -> None:

        vente = self.vente_selectionnee()

        if vente is None:
            self.lbl_total_achat.setText("")
            return

        total = self.spin_achat.value() * int(vente.get("prix_unitaire", 0))

        self.lbl_total_achat.setText(f"Total max. : {format_nombre(total)}")

    def acheter(self) -> None:

        vente = self.vente_selectionnee()

        if vente is None:
            self.avertir("Acheter", "Sélectionnez d'abord une vente.")
            return

        quantite = self.spin_achat.value()
        prix = int(vente.get("prix_unitaire", 0))

        texte = (
            f"Acheter {quantite} × {vente.get('nom', '?')} ?\n\n"
            f"Prix unitaire maximum : {format_nombre(prix)}\n"
            f"Total maximum : {format_nombre(quantite * prix)}\n\n"
            "Si un exemplaire moins cher correspond, vous le payez moins."
        )

        if not self.confirmer("Confirmer l'achat", texte):
            return

        self._envoyer(
            {
                "action": "buy",
                "ligne_vente_id": vente["ligne_vente_id"],
                "quantite": quantite,
            }
        )

    # -------------------------------------------------------------
    # VENDRE
    # -------------------------------------------------------------

    def _onglet_change(self, index: int) -> None:

        if index == 1:
            self._demander_vente()

    def _demander_vente(self) -> None:
        """Recharge l'inventaire vendable et les ventes en cours."""

        self._envoyer({"action": "inventory"})
        self._envoyer({"action": "my_sales"})

    def _remplir_inventaire(self) -> None:

        presents = {objet["stuff_id"] for objet in self._inventaire}

        # Un objet qui n'est plus là ne reste pas sélectionné.
        for stuff_id in list(self._selection):
            if stuff_id not in presents:
                self._retirer_selection(stuff_id)

        self.table_inv.setRowCount(0)
        self._boutons_inventaire.clear()

        for objet in self._inventaire:

            ligne = self.table_inv.rowCount()
            self.table_inv.insertRow(ligne)

            stuff_id = objet["stuff_id"]

            bouton = QPushButton("Sélectionner")
            bouton.clicked.connect(
                lambda _=False, sid=stuff_id: self._basculer_selection(sid)
            )

            self._boutons_inventaire[stuff_id] = bouton

            self.table_inv.setCellWidget(ligne, 0, bouton)

            cellules = [
                _cellule(str(objet.get("nom", "?"))),
                _cellule(details_objet(objet)),
                _cellule(durabilite_texte(objet), droite=True),
                _cellule(format_nombre(objet.get("quantite", 1)), droite=True),
                _cellule(format_nombre(prix_conseille(objet)), droite=True),
            ]

            for colonne, cellule in enumerate(cellules, start=1):
                self.table_inv.setItem(ligne, colonne, cellule)

            if stuff_id in self._selection:
                bouton.setText("Retirer")
                self._maj_quantite_max(stuff_id, objet)

        self._maj_total_vente()

    def _objet_inventaire(self, stuff_id: int) -> dict | None:

        for objet in self._inventaire:
            if objet["stuff_id"] == stuff_id:
                return objet

        return None

    def _basculer_selection(self, stuff_id: int) -> None:

        if stuff_id in self._selection:
            self._retirer_selection(stuff_id)
        else:
            self._ajouter_selection(stuff_id)

    def _ajouter_selection(self, stuff_id: int) -> None:

        objet = self._objet_inventaire(stuff_id)

        if objet is None or stuff_id in self._selection:
            return

        ligne = self.table_sel.rowCount()
        self.table_sel.insertRow(ligne)

        nom = _cellule(str(objet.get("nom", "?")))
        nom.setData(Qt.UserRole, stuff_id)
        self.table_sel.setItem(ligne, 0, nom)

        quantite = QSpinBox()
        quantite.setRange(1, max(1, int(objet.get("quantite", 1))))
        quantite.valueChanged.connect(self._maj_total_vente)
        self.table_sel.setCellWidget(ligne, 1, quantite)

        prix = _champ_entier("prix", largeur=140)
        prix.setText(str(prix_conseille(objet) or ""))
        prix.textChanged.connect(self._maj_total_vente)
        self.table_sel.setCellWidget(ligne, 2, prix)

        self.table_sel.setItem(ligne, 3, _cellule("", droite=True))

        retirer = QPushButton("Retirer")
        retirer.clicked.connect(
            lambda _=False, sid=stuff_id: self._basculer_selection(sid)
        )
        self.table_sel.setCellWidget(ligne, 4, retirer)

        self._selection[stuff_id] = {"quantite": quantite, "prix": prix}

        bouton = self._boutons_inventaire.get(stuff_id)

        if bouton is not None:
            bouton.setText("Retirer")

        self._maj_total_vente()
        self._maj_boutons()

    def _retirer_selection(self, stuff_id: int) -> None:

        self._selection.pop(stuff_id, None)

        for ligne in range(self.table_sel.rowCount()):

            cellule = self.table_sel.item(ligne, 0)

            if cellule is not None and cellule.data(Qt.UserRole) == stuff_id:
                self.table_sel.removeRow(ligne)
                break

        bouton = self._boutons_inventaire.get(stuff_id)

        if bouton is not None:
            bouton.setText("Sélectionner")

        self._maj_total_vente()
        self._maj_boutons()

    def _vider_selection(self) -> None:

        for stuff_id in list(self._selection):
            self._retirer_selection(stuff_id)

    def _maj_quantite_max(self, stuff_id: int, objet: dict) -> None:

        widgets = self._selection.get(stuff_id)

        if widgets is not None:
            widgets["quantite"].setMaximum(
                max(1, int(objet.get("quantite", 1)))
            )

    def lignes_selection(self) -> list[dict]:
        """Lignes à vendre : stuff_id, quantité, prix (None si invalide)."""

        lignes = []

        for stuff_id, widgets in self._selection.items():

            objet = self._objet_inventaire(stuff_id) or {}

            lignes.append(
                {
                    "stuff_id": stuff_id,
                    "nom": objet.get("nom", "?"),
                    "quantite": widgets["quantite"].value(),
                    "prix": entier_ou_none(widgets["prix"].text()),
                }
            )

        return lignes

    def _maj_total_vente(self) -> None:

        total = 0
        nombre = 0

        for ligne in range(self.table_sel.rowCount()):

            cellule = self.table_sel.item(ligne, 0)

            if cellule is None:
                continue

            widgets = self._selection.get(cellule.data(Qt.UserRole))

            if widgets is None:
                continue

            quantite = widgets["quantite"].value()
            prix = entier_ou_none(widgets["prix"].text())

            nombre += 1

            if prix:
                sous_total = quantite * prix
                total += sous_total
                self.table_sel.item(ligne, 3).setText(
                    format_nombre(sous_total)
                )
            else:
                self.table_sel.item(ligne, 3).setText("")

        if nombre == 0:
            self.lbl_total_vente.setText("Aucun objet sélectionné.")
        else:
            self.lbl_total_vente.setText(
                f"{nombre} ligne(s) - total attendu : {format_nombre(total)}"
            )

    def valider_vente(self) -> None:

        lignes = self.lignes_selection()

        if not lignes:
            self.avertir("Vendre", "Sélectionnez d'abord des objets.")
            return

        for ligne in lignes:
            if not ligne["prix"] or ligne["prix"] <= 0:
                self.avertir(
                    "Vendre",
                    f"Indiquez un prix valide pour {ligne['nom']}.",
                )
                return

        total = sum(ligne["quantite"] * ligne["prix"] for ligne in lignes)

        detail = "\n".join(
            f"  • {ligne['quantite']} × {ligne['nom']} à "
            f"{format_nombre(ligne['prix'])} l'unité"
            for ligne in lignes
        )

        texte = (
            f"Mettre en vente :\n{detail}\n\n"
            f"Total attendu : {format_nombre(total)}\n\n"
            "Ces objets ne seront plus utilisables tant qu'ils ne sont pas "
            "vendus ou que la vente n'est pas annulée."
        )

        if not self.confirmer("Confirmer la vente", texte):
            return

        self._envoyer(
            {
                "action": "sell",
                "lignes": [
                    {
                        "stuff_id": ligne["stuff_id"],
                        "quantite": ligne["quantite"],
                        "prix": ligne["prix"],
                    }
                    for ligne in lignes
                ],
            }
        )

    # --- Mes ventes -----------------------------------------------

    def _remplir_mes_ventes(self) -> None:

        self.table_mes.setRowCount(0)

        for vente in self._mes_ventes:

            ligne = self.table_mes.rowCount()
            self.table_mes.insertRow(ligne)

            cellules = [
                _cellule(str(vente.get("nom", "?"))),
                _cellule(details_objet(vente)),
                _cellule(durabilite_texte(vente), droite=True),
                _cellule(format_nombre(vente.get("quantite", 0)), droite=True),
                _cellule(
                    format_nombre(vente.get("prix_unitaire", 0)), droite=True
                ),
            ]

            for colonne, cellule in enumerate(cellules):
                self.table_mes.setItem(ligne, colonne, cellule)

    def vente_en_cours_selectionnee(self) -> dict | None:

        ligne = self.table_mes.currentRow()

        if 0 <= ligne < len(self._mes_ventes) and self.table_mes.selectedItems():
            return self._mes_ventes[ligne]

        return None

    def annuler_vente(self) -> None:

        vente = self.vente_en_cours_selectionnee()

        if vente is None:
            self.avertir("Annuler", "Sélectionnez d'abord une de vos ventes.")
            return

        texte = (
            f"Annuler la vente de {vente.get('quantite', '?')} × "
            f"{vente.get('nom', '?')} ?\n\n"
            "L'objet vous sera rendu."
        )

        if not self.confirmer("Annuler la vente", texte):
            return

        self._envoyer(
            {
                "action": "cancel_sale",
                "ligne_vente_id": vente["ligne_vente_id"],
            }
        )

    # -------------------------------------------------------------
    # ÉTAT DES BOUTONS
    # -------------------------------------------------------------

    def _maj_boutons(self) -> None:
        """Pas de double envoi : une action en cours bloque son bouton."""

        occupe = any(a in self._en_attente for a in self.ACTIONS_QUI_MODIFIENT)

        self.btn_acheter.setEnabled(
            self.vente_selectionnee() is not None and not occupe
        )
        self.btn_valider.setEnabled(bool(self._selection) and not occupe)
        self.btn_annuler.setEnabled(
            self.vente_en_cours_selectionnee() is not None and not occupe
        )

    def closeEvent(self, event) -> None:

        self._delai.stop()

        super().closeEvent(event)
