# ============================================================
#  ARNO'S BIZARRE ADVENTURE — settings.py
#  Toutes les constantes du jeu ici. Modifie librement !
# ============================================================

# --- Fenêtre ---
TITRE        = "Arno's Bizarre Adventure"
LARGEUR      = 800          # pixels
HAUTEUR      = 600          # pixels
FPS          = 60

# --- Taille des tuiles (tiles) ---
TAILLE_TUILE = 32           # chaque case du monde = 32x32 pixels

# --- Vitesses ---
VITESSE_JOUEUR  = 3         # pixels par frame
VITESSE_ENNEMI  = 1         # pixels par frame

# --- Combat ---
PV_JOUEUR_MAX   = 5         # points de vie d'Arno
PV_ENNEMI       = 2         # points de vie d'un ennemi de base
DEGATS_JOUEUR   = 1         # dégâts infligés par Arno
DEGATS_ENNEMI   = 1         # dégâts infligés par un ennemi
COOLDOWN_ATTAQUE      = 30  # frames entre deux attaques joueur
COOLDOWN_INVINCIBLE   = 60  # frames d'invincibilité après avoir reçu un coup
PORTEE_ATTAQUE  = 40        # pixels — portée du coup d'Arno

# --- Caméra ---
# La caméra suit Arno et centre le monde autour de lui

# ============================================================
#  PALETTE DE COULEURS — style pixel art banlieue
# ============================================================
NOIR          = (  0,   0,   0)
BLANC         = (255, 255, 255)

# Sol
ASPHALTE      = ( 45,  45,  50)   # route grise foncée
TROTTOIR      = ( 90,  90,  95)   # trottoir
HERBE_URBAINE = ( 60,  90,  40)   # petite bande verte
TERRE         = (100,  75,  50)

# Bâtiments
MUR_BETON     = (120, 115, 110)   # mur d'immeuble
MUR_BRIQUE    = (140,  80,  60)   # immeuble en brique
FENETRE       = ( 80, 120, 160)   # fenêtre bleue
PORTE         = ( 60,  45,  35)   # porte en bois

# Tags / graffitis
GRAFFITI_ROUGE  = (220,  50,  50)
GRAFFITI_JAUNE  = (230, 200,  40)
GRAFFITI_BLEU   = ( 40, 100, 220)

# Joueur
COULEUR_ARNO      = ( 30, 100, 200)   # veste bleue
COULEUR_ARNO_SKIN = (220, 170, 120)   # peau

# Ennemis
COULEUR_ENNEMI    = (180,  40,  40)   # rouge

# UI
COULEUR_PV_PLEIN  = (220,  50,  50)
COULEUR_PV_VIDE   = ( 60,  30,  30)
COULEUR_UI_FOND   = (  0,   0,   0, 160)  # semi-transparent

# Attaque (flash)
COULEUR_ATTAQUE   = (255, 220,  50)
