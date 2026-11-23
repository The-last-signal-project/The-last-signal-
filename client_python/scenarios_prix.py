from verify import *

RS2 = open("src/gameplay/market_manager.rs", encoding="utf-8").read().replace("\r\n", "\n")
SQL_INV = re.search(r'const SQL_INVENTAIRE_VENDABLE: &str = r#"(.*?)"#;', RS2, re.S).group(1)
SQL_VENTES = re.search(r'const SQL_VENTES: &str = r#"(.*?)"#;', RS2, re.S).group(1)

def inventaire(acc):
    """SQL de l'inventaire + calcul de prix_conseille, comme `inventaire_vendable`."""
    cur = con.execute(SQL_INV, {"1": acc}); cols = [d[0] for d in cur.description]
    lignes = [dict(zip(cols, r)) for r in cur.fetchall()]
    for l in lignes:
        l["prix_conseille"] = prix_exemplaire(l["type_objet"], l["rarete"], l["rang"], l["durabilite"], l["durabilite_max"], l["prix_base"], l["prix_marche"])
    return lignes
def prix_de(acc, sid): return [i["prix_conseille"] for i in inventaire(acc) if i["stuff_id"] == sid][0]
def ventes(acc):
    """SQL_VENTES (mode marché) + valeur estimée comme `lister_ventes`."""
    sql = SQL_VENTES + "\nORDER BY lv.prix_unitaire ASC\nLIMIT ?15"
    cur = con.execute(sql, {str(i + 1): v for i, v in enumerate([acc, 0] + [None] * 12 + [200])})
    cols = [d[0] for d in cur.description]
    rows = [dict(zip(cols, r)) for r in cur.fetchall()]
    for v in rows:
        v["valeur_estimee"] = prix_exemplaire(v["type_objet"], v["rarete"], v["rang"], v["durabilite"], v["durabilite_max"], v["prix_base"], v["prix_marche"])
    return rows

print("== constantes lues dans le code Rust")
print("   rareté :", MULT_RARETE); print("   rang   :", MULT_RANG)
assert MULT_RARETE["Commun"] == 1.0 and MULT_RANG["E"] == 1.0 and MULT_RANG["G"] == 0.5 and MULT_RANG["SSS"] == 10.0
ok("rang = multiplicateurs de Rank (G 0,5 ... SSS 10) ; rareté = table de prix.rs")

BASE = q1("SELECT prix_base FROM objets_dispo WHERE nom='épée de pierre'")
assert q1("SELECT prix_marche FROM objets_dispo WHERE nom='épée de pierre'") == 0
print("== 1. prix initiaux (aucune vente) : prix de base =", BASE)
cas = [
    ("Commun", "E", 100, 100, 1.0),
    ("Commun", "G", 50, 50, 0.5),
    ("Rare", "C", 200, 200, 3.0),
    ("Rare", "C", 80, 200, 1.2),        # 40 % de durabilité
    ("Mythique", "SSS", 1000, 1000, 80.0),
]
for rar, rang, d, dm, attendu in cas:
    sid = obtenir_unique(A, "épée de pierre", rar, rang, d, dm)
    p = prix_de(A, sid)
    assert p == max(arrondi(BASE * attendu), 1), (rar, rang, d, dm, p, BASE * attendu)
    print(f"   {rar:9s} {rang:3s} {d:4d}/{dm:<4d} x{attendu:<5} -> {p}")
ok("la rareté et le rang s'appliquent dès le premier prix ; la durabilité perdue le baisse")
sid = obtenir_unique(A, "épée de pierre", "Rare", "C", 200, 200)
p0 = prix_de(A, sid)
con.execute("UPDATE equipment SET durability=100 WHERE stuff_id=?", (sid,))
assert prix_de(A, sid) == arrondi(p0 / 2)
con.execute("UPDATE equipment SET durability=0 WHERE stuff_id=?", (sid,))
assert prix_de(A, sid) == 1
ok("usure en direct : moitié de durabilité = moitié du prix ; cassé = 1 (jamais 0)")
obtenir_base(A, "Fe", 5); fe = q1("SELECT stuff_id FROM stuff WHERE account_id=? AND objet_id=?", (A, OBJ["Fe"]))
con.execute("UPDATE stuff SET rarete='Mythique', rang='SSS' WHERE stuff_id=?", (fe,))
assert prix_de(A, fe) == q1("SELECT prix_base FROM objets_dispo WHERE nom='Fe'")
con.execute("UPDATE stuff SET rarete=NULL, rang=NULL WHERE stuff_id=?", (fe,))
pot = obtenir_potion(A, "potion de mana", "mana", potency=5, duration=10)
assert prix_de(A, pot) == q1("SELECT prix_base FROM objets_dispo WHERE nom='potion de mana'")
ok("objets de base (même avec une marque résiduelle) et potions : pas de multiplicateur")

print("== 2. prix du marché : ramené à un exemplaire standard")
for acc in (B, C):
    con.execute("UPDATE wallets SET balance = balance + 10000000 WHERE account_id=?", (acc,))
ARG = total_argent()
def vendre_et_acheter(rar, rang, d, dm, prix, acheteur=B):
    sid = obtenir_unique(A, "épée de pierre", rar, rang, d, dm)
    creer_vente(A, [(sid, 1, prix)])
    vid = q1("SELECT variante_id FROM variantes_marche WHERE objet_id=? AND rarete=? AND rang=?", (OBJ["épée de pierre"], rar, rang))
    _, _, n = creer_achat(acheteur, [dict(objet_id=OBJ["épée de pierre"], variante_id=vid, quantite=1, prix_max=prix, dura_min=d, dura_max=d)])
    assert n == 1
    return sid
pm = lambda: q1("SELECT prix_marche FROM objets_dispo WHERE nom='épée de pierre'")
f9 = MULT_RARETE["Rare"] * MULT_RANG["S"]
vendre_et_acheter("Rare", "S", 600, 600, round(100 * f9))
assert pm() == 100, pm()
ok(f"épée Rare rang S neuve vendue {round(100*f9)} -> prix de référence 100 (facteur {f9})")
vendre_et_acheter("Rare", "S", 300, 600, round(100 * f9 / 2))
assert pm() == 100, pm()
ok("la même épée à moitié usée vendue moitié prix : le prix du marché ne bouge pas")
vendre_et_acheter("Commun", "G", 50, 50, 40)
assert pm() == round((100 + 100 + 40 / 0.5) / 3), pm()
ok(f"épée Commun rang G vendue 40 : référence {40 / 0.5} ; moyenne des 3 ventes = {pm()}")
ref = pm()
for rar, rang, d, dm in [("Commun", "E", 100, 100), ("Rare", "C", 200, 200), ("Rare", "S", 300, 600)]:
    sid = obtenir_unique(A, "épée de pierre", rar, rang, d, dm)
    assert prix_de(A, sid) == max(arrondi(ref * facteur_qualite("armes", rar, rang, d, dm)), 1)
ok("un nouvel exemplaire est estimé avec ce prix de référence x sa propre qualité")
liste = [v for v in ventes(C) if v["nom"] == "épée de pierre"]
sid_l = obtenir_unique(A, "épée de pierre", "Rare", "B", 150, 300)
creer_vente(A, [(sid_l, 1, 999)])
v = [x for x in ventes(C) if x["ligne_vente_id"] == q1("SELECT MAX(ligne_vente_id) FROM lignes_vente")][0]
assert v["valeur_estimee"] == max(arrondi(ref * facteur_qualite("armes", "Rare", "B", 150, 300)), 1) and v["prix_marche"] == ref
ok("la liste des ventes affiche la valeur estimée de l'exemplaire (rareté, rang, durabilité)")
assert total_argent() == ARG
ok("argent total conservé")
print("\nTESTS PRIX OK")
