# Arnaud — Metroidvania
> Projet personnel — Platformer Metroidvania en pixel art, thème urbain/banlieue  
> Développé en Python avec Pygame

---

## Lancer le jeu

```bash
cd ~/Portfolio-Project-Holberton/metroidvania
python3 main.py
```

**Dépendances :**
```bash
pip install pygame
```

---

## Contrôles

| Touche | Action |
|---|---|
| Q / ← | Aller à gauche |
| D / → | Aller à droite |
| Z / ↑ / ESPACE | Sauter |
| S / ↓ | S'accroupir |
| SHIFT gauche | Esquiver (dash) |
| X / K | Attaquer (épée) |
| C / L | Légo Blast (si débloqué) |
| ECHAP | Quitter |

**Debug uniquement :**

| Touche | Action |
|---|---|
| F1 | Débloquer double saut |
| F2 | Débloquer toutes les capacités |
| F3 | Toggle debug (hitbox, infos physique) |
| F4 | Zone suivante |
| F5 | Zone précédente |
| R | Recommencer (game over) |

---

## Structure du projet

```
metroidvania/
│
├── main.py          — Boucle pygame + events (ne contient que ça)
├── facade.py        — Façade globale : logique de jeu, caméra, transitions
├── player.py        — Arnaud : physique, moveset complet, UI
├── settings.py      — Toutes les constantes (vitesse, gravité, couleurs...)
│
└── map/
    ├── __init__.py  — Façade des zones + GestionnaireZones
    ├── world.py     — Niveau + Caméra
    ├── zone_a.py    — Zone tutoriel (COMPLÈTE)
    ├── zone_1.py    — Zone 1 — grande verticale (squelette)
    ├── zone_2.py    — Zone 2 (squelette)
    ├── ...
    ├── zone_16.py   — Zone 16 (squelette)
    ├── zone_b.py    — Fin du jeu (squelette)
    └── zone_boss.py — Boss final (squelette)
```

---

## Architecture — comment les fichiers se parlent

```
main.py
  └── Facade (facade.py)
        ├── GestionnaireZones (map/__init__.py)
        │     └── ZoneX (map/zone_x.py)
        │           ├── Plateformes, Murs
        │           ├── Ennemis, Tourelles
        │           ├── Checkpoints, Légos
        │           └── Sorties (transitions)
        └── Arnaud (player.py)
              ├── Physique (gravité, collisions)
              ├── Moveset (saut, esquive, attaque...)
              └── UI (cœurs, vies, missiles)
```

---

## Moveset d'Arnaud

### Capacités de base (innées)
| Capacité | Touche | Description |
|---|---|---|
| Déplacement | Q / D | Marche horizontale avec friction |
| Saut | Z / ESPACE | Saut depuis le sol |
| Esquive | SHIFT | Dash horizontal avec invincibilité |
| Accroupissement | S | Réduit la hitbox, passe sous obstacles |
| Attaque épée | X / K | Coup directionnel avec recul |

### Capacités déblocables
| Capacité | Description |
|---|---|
| Double saut | Saut supplémentaire en l'air |
| Glissade | Flèche bas + esquive |
| Missiles | Projectile puissant (stock limité) |
| Légo Blast | Projectile directionnel (C / L) |
| Légo Sword | Améliore les dégâts de l'épée |

### Système de dégâts
- Dégâts de base : `1.0`
- +0.25 dégâts tous les 2 Légos collectés
- Cap maximum : `3.0` (avec 8 Légos + Légo Sword)

### Système de vie
- **3 vies** — chaque vie a **5 cœurs**
- Invincibilité de 1.5s après un coup reçu
- Invincibilité pendant l'esquive

---

## Map — structure générale

```
[Zone A]  — Tutoriel horizontal (spawn gauche → droite)
    ↓
[Zone 1]  — Grande zone verticale
    ↓
[Zone 2 à 16] — Zones interconnectées
    ↓
[Zone B]  — Fin du jeu
```

**Légende des zones :**
- **S** = Checkpoint / sauvegarde
- **Hachures** = Zone secrète (accessible avec certaines capacités)
- **Porte** = Transition vers la zone suivante (style Metroid)

### Zone A — tutoriel implicite
Le level design enseigne sans texte dans cet ordre :
1. **Bordure haute** → apprend le saut
2. **Ennemi basique** → apprend l'attaque  
3. **Tourelle** (1 balle / 1.5s) → apprend l'esquive
4. **Checkpoint S** → sauvegarde
5. **Porte** → transition vers Zone 1

---

## Système de zones

Chaque zone expose :
```python
zone.spawns   # dict des points d'entrée : "defaut", "haut", "gauche", "droite"
zone.sorties  # list des sorties : {"rect": ..., "destination": "zone_x", "spawn": "..."}
```

Ajouter une transition dans une zone :
```python
self.sorties.append({
    "rect"        : pygame.Rect(x, y, largeur, hauteur),
    "destination" : "zone_1",
    "spawn"       : "gauche",
})
```

---

## Ce qui reste à faire

- [ ] Inverser le sens de la Zone A (spawn gauche → droite)
- [ ] Ajouter les portes de transition dans toutes les zones
- [ ] Remplir les zones 1 à 16 (plateformes, ennemis, secrets)
- [ ] Implémenter les zones secrètes (hachures)
- [ ] Système de sauvegarde (checkpoints fonctionnels)
- [ ] Sons et musique (pygame.mixer)
- [ ] Sprites PNG (remplacer le pixel art codé)
- [ ] Boss final (Zone B)
- [ ] Écran titre et menu

---

## Notes de dev

- **FPS cible :** 60
- **Taille tuile :** 32x32 px
- **Résolution :** 960x576 px
- **Coyote time :** 8 frames (aide au saut en bord de plateforme)
- Pour modifier les constantes du jeu : `settings.py`
- Pour ajouter une zone : créer `map/zone_x.py` + l'enregistrer dans `map/__init__.py`
