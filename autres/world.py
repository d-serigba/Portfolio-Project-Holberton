# ============================================================
#  ARNO'S BIZARRE ADVENTURE — world.py
#  Le monde du jeu : tuiles, obstacles, caméra, niveau
# ============================================================

import pygame
from settings import *
from enemy import Ennemi


# ============================================================
#  TUILES — les cases qui composent la carte
# ============================================================

class Tuile(pygame.sprite.Sprite):
    """Une tuile de décor (sol, mur...) dessinée en pixel art."""

    def __init__(self, x, y, type_tuile):
        super().__init__()
        self.image = self._dessiner(type_tuile)
        self.rect  = self.image.get_rect(topleft=(x, y))

    def _dessiner(self, t):
        surf = pygame.Surface((TAILLE_TUILE, TAILLE_TUILE))
        if t == "sol_asphalte":
            surf.fill(ASPHALTE)
            # Lignes de route
            pygame.draw.line(surf, (60, 60, 65), (0, 0), (32, 0), 1)
            pygame.draw.line(surf, (60, 60, 65), (0, 0), (0, 32), 1)
        elif t == "trottoir":
            surf.fill(TROTTOIR)
            pygame.draw.rect(surf, (100, 100, 105), (0, 0, 32, 2))
            pygame.draw.rect(surf, (80, 80, 85), (0, 30, 32, 2))
        elif t == "herbe":
            surf.fill(HERBE_URBAINE)
            # petits détails végétaux
            pygame.draw.rect(surf, (50, 80, 30), (4, 8, 2, 6))
            pygame.draw.rect(surf, (50, 80, 30), (12, 4, 2, 8))
            pygame.draw.rect(surf, (50, 80, 30), (22, 10, 2, 5))
        elif t == "mur_beton":
            surf.fill(MUR_BETON)
            # Joints
            for i in range(0, 32, 8):
                pygame.draw.line(surf, (100, 95, 90), (0, i), (32, i), 1)
            for j in range(0, 32, 16):
                pygame.draw.line(surf, (100, 95, 90), (j, 0), (j, 32), 1)
        elif t == "mur_brique":
            surf.fill(MUR_BRIQUE)
            for row in range(4):
                offset = 8 if row % 2 else 0
                for col in range(-1, 3):
                    pygame.draw.rect(surf, (120, 60, 40),
                                     (col*16 + offset, row*8, 14, 6))
                    pygame.draw.rect(surf, (160, 90, 70),
                                     (col*16 + offset + 1, row*8 + 1, 12, 4))
        elif t == "fenetre":
            surf.fill(MUR_BETON)
            pygame.draw.rect(surf, FENETRE, (6, 6, 20, 20))
            pygame.draw.rect(surf, (120, 170, 210), (8, 8, 8, 8))
            pygame.draw.rect(surf, (60, 100, 150), (18, 8, 8, 8))
            pygame.draw.rect(surf, (60, 100, 150), (8, 18, 8, 8))
            pygame.draw.rect(surf, (120, 170, 210), (18, 18, 8, 8))
        elif t == "graffiti":
            surf.fill(MUR_BRIQUE)
            # Un tag coloré
            pygame.draw.rect(surf, GRAFFITI_ROUGE,  (4, 10, 8, 12))
            pygame.draw.rect(surf, GRAFFITI_JAUNE,  (12, 6, 6, 16))
            pygame.draw.rect(surf, GRAFFITI_BLEU,   (20, 10, 8, 12))
        elif t == "porte":
            surf.fill(MUR_BETON)
            pygame.draw.rect(surf, PORTE, (8, 8, 16, 24))
            pygame.draw.rect(surf, (80, 60, 45), (10, 10, 12, 20))
            pygame.draw.circle(surf, (180, 150, 50), (20, 20), 2)
        else:
            surf.fill(ASPHALTE)
        return surf


class TuileObstacle(Tuile):
    """Tuile solide — bloque le joueur et les ennemis."""
    pass


class TuileDeco(Tuile):
    """Tuile de décor — traversable (sol, herbe...)."""
    pass


# ============================================================
#  CAMÉRA — fait suivre Arno
# ============================================================

class Camera:
    """
    Décale toutes les positions pour centrer Arno à l'écran.
    Utilisation : camera.appliquer(sprite) → rect décalé
    """

    def __init__(self, largeur_monde, hauteur_monde):
        self.decalage = pygame.math.Vector2(0, 0)
        self.largeur_monde  = largeur_monde
        self.hauteur_monde  = hauteur_monde

    def appliquer(self, entite):
        """Retourne le rect de l'entité décalé par la caméra."""
        return entite.rect.move(self.decalage)

    def appliquer_rect(self, rect):
        return rect.move(self.decalage)

    def mettre_a_jour(self, cible):
        """Centre la caméra sur la cible (Arno)."""
        x = LARGEUR  // 2 - cible.rect.centerx
        y = HAUTEUR  // 2 - cible.rect.centery

        # Limites : la caméra ne sort pas du monde
        x = min(0, x)
        y = min(0, y)
        x = max(LARGEUR  - self.largeur_monde,  x)
        y = max(HAUTEUR - self.hauteur_monde, y)

        self.decalage.x = x
        self.decalage.y = y


# ============================================================
#  NIVEAU — carte du premier niveau (banlieue)
# ============================================================

# Carte en ASCII — chaque caractère = une tuile 32x32
# . = asphalte (sol route)
# T = trottoir
# H = herbe
# M = mur béton (obstacle)
# B = mur brique (obstacle)
# F = fenêtre (obstacle)
# G = graffiti (obstacle)
# P = porte (obstacle)
# E = spawn ennemi (remplacé par asphalte)
# A = spawn Arno  (remplacé par asphalte)

CARTE_NIVEAU_1 = [
    "MMMMMMMMMMMMMMMMMMMMMMMMMMMMMM",
    "M............................M",
    "M..BBBFBBF..........BBBFBBF..M",
    "M..B........E......B.........M",
    "M..B........................B.M",
    "M..BBBFBBF..........BBBFBBF..M",
    "M............................M",
    "M....TTTTTTTTTTTTTTTTTTT.....M",
    "M....T...................T....M",
    "M....T......MMPMM........T....M",
    "M....T......M...M........T....M",
    "M....T.E....M...M....E...T....M",
    "M....T......M...M........T....M",
    "M....T......MMMMM........T....M",
    "M....T...................T....M",
    "M....TTTTTTTTTTTTTTTTTTT.....M",
    "M..A.........................M",
    "M............................M",
    "M..GGGBBB..........BBBGGG....M",
    "M..G....B..........B....G....M",
    "M..G....B...E......B....G....M",
    "M..GGGBBB..........BBBGGG....M",
    "M............................M",
    "MMMMMMMMMMMMMMMMMMMMMMMMMMMMMM",
]


class Niveau:
    """
    Charge la carte, crée les tuiles, les ennemis,
    et fournit le point de départ d'Arno.
    """

    def __init__(self):
        self.tuiles_sol      = pygame.sprite.Group()
        self.tuiles_obstacle = pygame.sprite.Group()
        self.ennemis         = pygame.sprite.Group()
        self.spawn_joueur    = (0, 0)

        self._charger_carte(CARTE_NIVEAU_1)

        # Dimensions du monde en pixels
        colonnes = len(CARTE_NIVEAU_1[0])
        lignes   = len(CARTE_NIVEAU_1)
        self.largeur_monde  = colonnes * TAILLE_TUILE
        self.hauteur_monde  = lignes   * TAILLE_TUILE

        self.camera = Camera(self.largeur_monde, self.hauteur_monde)

    def _charger_carte(self, carte):
        OBSTACLES = {"M", "B", "F", "G", "P"}

        # On garde une liste des zones de patrouille des ennemis
        spawns_ennemis = []

        for ligne_idx, ligne in enumerate(carte):
            for col_idx, char in enumerate(ligne):
                x = col_idx * TAILLE_TUILE
                y = ligne_idx * TAILLE_TUILE

                if char == "A":
                    self.spawn_joueur = (x, y)
                    TuileDeco(x, y, "sol_asphalte").add(self.tuiles_sol)

                elif char == "E":
                    spawns_ennemis.append((x, y, col_idx, ligne_idx))
                    TuileDeco(x, y, "sol_asphalte").add(self.tuiles_sol)

                elif char in OBSTACLES:
                    type_map = {
                        "M": "mur_beton",
                        "B": "mur_brique",
                        "F": "fenetre",
                        "G": "graffiti",
                        "P": "porte",
                    }
                    TuileObstacle(x, y, type_map[char]).add(self.tuiles_obstacle)

                elif char == "T":
                    TuileDeco(x, y, "trottoir").add(self.tuiles_sol)
                elif char == "H":
                    TuileDeco(x, y, "herbe").add(self.tuiles_sol)
                else:
                    TuileDeco(x, y, "sol_asphalte").add(self.tuiles_sol)

        # Créer les ennemis avec zones de patrouille
        for (x, y, col, lig) in spawns_ennemis:
            pat_x1 = max(0,  (col - 4) * TAILLE_TUILE)
            pat_x2 = min(len(CARTE_NIVEAU_1[0]) * TAILLE_TUILE, (col + 4) * TAILLE_TUILE)
            e = Ennemi(x, y, pat_x1, pat_x2)
            self.ennemis.add(e)

    def dessiner(self, ecran, camera):
        """Dessine toutes les tuiles et ennemis avec le décalage caméra."""
        for tuile in self.tuiles_sol:
            ecran.blit(tuile.image, camera.appliquer(tuile))
        for tuile in self.tuiles_obstacle:
            ecran.blit(tuile.image, camera.appliquer(tuile))
        for ennemi in self.ennemis:
            ecran.blit(ennemi.image, camera.appliquer(ennemi))

    def supprimer_ennemis_morts(self):
        for ennemi in list(self.ennemis):
            if ennemi.est_mort():
                ennemi.kill()
