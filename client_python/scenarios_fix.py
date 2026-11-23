import sqlite3
from verify import *

RS2 = open("src/gameplay/market_manager.rs", encoding="utf-8").read().replace("\r\n", "\n")
SQL_INV = re.search(r'const SQL_INVENTAIRE_VENDABLE: &str = r#"(.*?)"#;', RS2, re.S).group(1)
def inventaire(acc):
    cur = con.execute(SQL_INV, {"1": acc}); cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]
def piles(acc, nom):
    return q("SELECT quantity, visible, stack_key FROM stuff WHERE account_id=? AND objet_id=? ORDER BY stuff_id", (acc, OBJ[nom]))

for acc in (B, C):
    con.execute("UPDATE wallets SET balance = balance + 1000000 WHERE account_id=?", (acc,))
ARGENT_INITIAL = total_argent()

print("== 1. UNIQUE stock_marche.stuff_id : remise en vente après annulation / vente")
w = obtenir_unique(A, "épée de bois", "Commun", "G", 50)
pt = obtenir_unique(A, "plastron", "Rare", "B", 80)
po = obtenir_potion(A, "potion de mana", "mana", potency=3, duration=10)
obtenir_base(A, "Fe", 6); fe = q1("SELECT stuff_id FROM stuff WHERE account_id=? AND objet_id=? AND stack_key='base'", (A, OBJ["Fe"]))
lignes = [(w, 1, 200000), (pt, 1, 400000), (po, 1, 100000), (fe, 1, 100000)]
ov, ids, _ = creer_vente(A, lignes)
assert len(ids) == 4
annuler_vente(A, ov)
assert all(q1("SELECT visible FROM stuff WHERE stuff_id=?", (s,)) == 1 for s in (w, pt, po))
ov, ids, _ = creer_vente(A, [(w, 1, 200000), (pt, 1, 400000), (po, 1, 100000)] + [(q1("SELECT stuff_id FROM stuff WHERE account_id=? AND objet_id=? AND stack_key='base'", (A, OBJ["Fe"])), 1, 100000)])
assert len(ids) == 4
ok("4 objets (arme, équipement, potion, pile) : mis en vente, annulés, remis en vente dans le même ordre")
annuler_vente(A, ov)
ov, ids, _ = creer_vente(A, [(w, 1, 50)])
annuler_vente(A, ov)
ov, ids, _ = creer_vente(A, [(w, 1, 50)])
ok("plusieurs cycles vente / annulation sur le même exemplaire")
assert q1("SELECT count(*) FROM stock_marche WHERE stuff_id=? AND statut IN ('disponible','partiel')", (w,)) == 1
assert q1("SELECT count(*) FROM stock_marche WHERE stuff_id=?", (w,)) == 4
ok("une seule ligne active à la fois ; l'historique est conservé (4 dépôts)")
try:
    with Tx():
        con.execute("INSERT INTO stock_marche (stuff_id,vendeur_id,quantite_deposee,quantite_restante) VALUES (?,?,1,1)", (w, A))
    raise SystemExit("double dépôt simultané accepté !")
except sqlite3.IntegrityError:
    ok("double dépôt simultané du même exemplaire : toujours refusé")
except Exception as e:
    assert "UNIQUE" in str(e); ok("double dépôt simultané du même exemplaire : toujours refusé")
annuler_vente(A, ov)

print("== 2. exemplaire acheté puis remis en vente par l'acheteur")
vw = q1("SELECT variante_id FROM variantes_marche WHERE objet_id=?", (OBJ["épée de bois"],))
ov, _, _ = creer_vente(A, [(w, 1, 90)])
_, _, n = creer_achat(B, [dict(objet_id=OBJ["épée de bois"], variante_id=vw, quantite=1, prix_max=90, dura_min=50, dura_max=50)])
assert n == 1 and q1("SELECT account_id FROM stuff WHERE stuff_id=?", (w,)) == B
ov2, ids2, _ = creer_vente(B, [(w, 1, 120)])
_, _, n = creer_achat(C, [dict(objet_id=OBJ["épée de bois"], variante_id=vw, quantite=1, prix_max=120, dura_min=50, dura_max=50)])
assert n == 1 and q1("SELECT account_id FROM stuff WHERE stuff_id=?", (w,)) == C
assert q1("SELECT count(*) FROM stock_marche WHERE stuff_id=?", (w,)) == 6
ok("A -> B -> C : le même exemplaire traverse trois propriétaires sans erreur")

print("== 3. objets de base : les achats se rangent dans la pile")
obtenir_base(A, "Au", 20); au = q1("SELECT stuff_id FROM stuff WHERE account_id=? AND objet_id=?", (A, OBJ["Au"]))
ov, _, _ = creer_vente(A, [(au, 10, 10)])
creer_achat(B, [dict(objet_id=OBJ["Au"], quantite=3, prix_max=10)])
assert piles(B, "Au") == [(3, 1, "base")], piles(B, "Au")
ok("1er achat (vente partielle) : une pile 'base' de 3")
creer_achat(B, [dict(objet_id=OBJ["Au"], quantite=2, prix_max=10)])
assert piles(B, "Au") == [(5, 1, "base")], piles(B, "Au")
ok("2e achat : la même pile passe à 5, pas de ligne en plus")
creer_achat(B, [dict(objet_id=OBJ["Au"], quantite=5, prix_max=10)])
assert piles(B, "Au") == [(10, 1, "base")], piles(B, "Au")
ok("achat qui vide la vente (transfert complet) : pile à 10")
obtenir_base(C, "Au", 7)
ov, _, _ = creer_vente(A, [(au, 4, 11)])
creer_achat(C, [dict(objet_id=OBJ["Au"], quantite=4, prix_max=11)])
assert piles(C, "Au") == [(11, 1, "base")], piles(C, "Au")
ok("l'acheteur avait déjà une pile obtenue normalement : tout fusionne (7 + 4 = 11)")
assert [r for r in piles(B, "Au") if r[2] != "base"] == []
# objet de base non empilable, et type militaire
obtenir_base(A, "trousse", 3); tr = q1("SELECT stuff_id FROM stuff WHERE account_id=? AND objet_id=?", (A, OBJ["trousse"]))
con.execute("UPDATE objets_dispo SET est_empilable=0 WHERE nom='trousse'")
creer_vente(A, [(tr, 3, 35)])
creer_achat(B, [dict(objet_id=OBJ["trousse"], quantite=3, prix_max=35)])
assert piles(B, "trousse") == [(3, 1, "base")], piles(B, "trousse")
ok("objet non empilable (3 dépôts unitaires) : l'acheteur a une pile de 3")
obtenir_base(A, "matos", 5); mt = q1("SELECT stuff_id FROM stuff WHERE account_id=? AND objet_id=?", (A, OBJ["matos"]))
assert q1("SELECT type FROM objets_dispo WHERE nom='matos'") == "military_equipment"
creer_vente(A, [(mt, 5, 500)])
creer_achat(B, [dict(objet_id=OBJ["matos"], quantite=2, prix_max=500)]); creer_achat(B, [dict(objet_id=OBJ["matos"], quantite=3, prix_max=500)])
assert piles(B, "matos") == [(5, 1, "base")], piles(B, "matos")
ok("military_equipment (objet de base) : se range aussi dans la pile")
# annulation : l'objet retourne dans la pile du vendeur
ov, _, _ = creer_vente(A, [(au, 6, 12)])
obtenir_base(A, "Au", 1)    # nouvelle pile 'base' pendant que 6 sont en séquestre
creer_achat(C, [dict(objet_id=OBJ["Au"], quantite=2, prix_max=12)])
annuler_vente(A, ov)
assert piles(A, "Au") == [(5, 1, "base")], piles(A, "Au")
ok("annulation après vente partielle : les 4 restants rejoignent la pile du vendeur (1 + 4)")
# pile masquée : jamais alimentée
con.execute("UPDATE stuff SET visible=0 WHERE account_id=? AND objet_id=? AND stack_key='base'", (B, OBJ["Au"]))
creer_vente(A, [(q1("SELECT stuff_id FROM stuff WHERE account_id=? AND objet_id=?", (A, OBJ["Au"])), 3, 10)])
creer_achat(B, [dict(objet_id=OBJ["Au"], quantite=3, prix_max=10)])
rows = piles(B, "Au")
assert (10, 0, "base") in rows and any(r[0] == 3 and r[1] == 1 and r[2].startswith("market-tx-") for r in rows), rows
ok("pile de l'acheteur masquée (visible=0) : non alimentée, l'achat reste visible à part")

print("== 4. prix du marché")
obtenir_base(A, "Lapiz", 50); ag = q1("SELECT stuff_id FROM stuff WHERE account_id=? AND objet_id=?", (A, OBJ["Lapiz"]))
assert q1("SELECT prix_marche FROM objets_dispo WHERE nom='Lapiz'") == 0
base_ag = q1("SELECT prix_base FROM objets_dispo WHERE nom='Lapiz'")
assert [i["prix_conseille"] for i in inventaire(A) if i["nom"] == "Lapiz"] == [base_ag]
ok("avant toute vente : prix_marche = 0, prix conseillé = prix de base du catalogue")
creer_vente(A, [(ag, 3, 10)]); creer_achat(B, [dict(objet_id=OBJ["Lapiz"], quantite=3, prix_max=10)])
assert q1("SELECT prix_marche FROM objets_dispo WHERE nom='Lapiz'") == 10
ok("1re vente de 3 à 10 : prix_marche = 10")
creer_vente(A, [(ag, 1, 20)]); creer_achat(B, [dict(objet_id=OBJ["Lapiz"], quantite=1, prix_max=20)])
assert q1("SELECT prix_marche FROM objets_dispo WHERE nom='Lapiz'") == 13     # (30 + 20) / 4 = 12,5 -> 13
ok("2e vente de 1 à 20 : moyenne pondérée (3×10 + 1×20) / 4 = 12,5 -> 13")
assert [i["prix_conseille"] for i in inventaire(A) if i["nom"] == "Lapiz"] == [13]
ok("le prix conseillé de l'onglet Vendre suit le prix du marché")
for k in range(25):
    creer_vente(A, [(ag, 1, 100)]); creer_achat(C, [dict(objet_id=OBJ["Lapiz"], quantite=1, prix_max=100)])
assert q1("SELECT prix_marche FROM objets_dispo WHERE nom='Lapiz'") == 100
ok("fenêtre glissante : les 20 dernières transactions seulement")
assert total_argent() == ARGENT_INITIAL
ok("argent total conservé")
print("\nTESTS CORRECTIONS OK")
