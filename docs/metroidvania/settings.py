# ============================================================
#  ARNAUD METROIDVANIA — settings.py
# ============================================================

TITRE        = "Arnaud — Metroidvania"
LARGEUR      = 960
HAUTEUR      = 576
FPS          = 60

TAILLE_TUILE = 32

# --- Physique ---
GRAVITE          = 0.6    # accélération vers le bas chaque frame
VITESSE_MAX_CHUTE = 18    # vitesse de chute maximale (évite de traverser les sols)
VITESSE_JOUEUR   = 4      # déplacement horizontal
FORCE_SAUT       = -14    # vitesse verticale au moment du saut (négatif = vers le haut)
FORCE_DOUBLE_SAUT = -12   # légèrement moins puissant que le 1er saut

# --- Esquive ---
VITESSE_ESQUIVE   = 10    # pixels/frame pendant l'esquive
DUREE_ESQUIVE     = 12    # frames (0.2 secondes à 60fps)
COOLDOWN_ESQUIVE  = 40    # frames avant de pouvoir esquiver à nouveau

# --- Combat ---
DEGATS_BASE       = 1.0   # dégâts épée de base
DEGATS_MAX_BONUS  = 2.0   # bonus max si 8 légos collectés
PORTEE_EPEE       = 48    # pixels

# Légo Sword
DEGATS_LEGO_SWORD_BASE = 1.5
# Légo Blast
DEGATS_LEGO_BLAST = 0.5   # 1/2 des dégâts de base

# Missiles
MISSILES_DEPART  = 0    # 0 au départ — débloqué via énigme/mini-boss
MISSILES_MAX     = 15   # max après avoir trouvé les réserves cachées

# --- Héros ---
VIES_MAX         = 3
COEURS_MAX       = 5
COOLDOWN_INVINCIBLE = 90  # frames (~1.5 sec)

# --- Couleurs ---
NOIR          = (  0,   0,   0)
BLANC         = (255, 255, 255)
ROUGE         = (200,  40,  40)
GRIS_FONCE    = ( 30,  30,  35)
GRIS_MUR      = ( 70,  70,  80)
GRIS_PLATEFORME = ( 90,  90, 100)
BLEU_FOND     = ( 15,  15,  30)  # fond du niveau — nuit urbaine

# Héros
COULEUR_ARNAUD      = (220, 220, 240)  # cheveux blancs / vêtement clair
COULEUR_ARNAUD_SKIN = (220, 170, 120)

# UI
COULEUR_COEUR_PLEIN = (220,  50,  50)
COULEUR_COEUR_VIDE  = ( 60,  20,  20)
COULEUR_VIE_PLEIN   = ( 50, 200,  80)
COULEUR_VIE_VIDE    = ( 30,  60,  30)
COULEUR_MISSILE     = ( 50, 180, 220)

# Légos — spectre visible + noir/blanc/multicolore
COULEURS_LEGO = [
    (220,  40,  40),   # rouge
    (230, 130,  30),   # orange
    (230, 220,  40),   # jaune
    ( 50, 200,  60),   # vert
    ( 40, 100, 220),   # bleu
    ( 80,  40, 180),   # indigo
    (160,  40, 200),   # violet
    ( 20,  20,  20),   # noir
    (240, 240, 240),   # blanc
    None,              # multicolore — géré spécialement
]
