# ============================================================
#  ARNO'S BIZARRE ADVENTURE — main.py
#  Point d'entrée : lance le jeu
#
#  COMMENT JOUER :
#    Z / Flèche haut    → monter
#    S / Flèche bas     → descendre
#    Q / Flèche gauche  → aller à gauche
#    D / Flèche droite  → aller à droite
#    ESPACE / J         → attaquer
#    ECHAP              → quitter
# ============================================================

import pygame
import sys
from settings import *
from player  import Joueur
from world   import Niveau


def main():
    # --- Initialisation Pygame ---
    pygame.init()
    ecran  = pygame.display.set_mode((LARGEUR, HAUTEUR))
    pygame.display.set_caption(TITRE)
    horloge = pygame.time.Clock()

    # --- Chargement du niveau ---
    niveau = Niveau()
    spawn_x, spawn_y = niveau.spawn_joueur
    arno = Joueur(spawn_x, spawn_y)

    # --- Groupe de sprites joueur ---
    groupe_joueur = pygame.sprite.GroupSingle(arno)

    # --- État du jeu ---
    en_cours     = True
    game_over    = False
    victoire     = False

    # --- Police pour les textes UI ---
    police       = pygame.font.SysFont("monospace", 18, bold=True)
    police_titre = pygame.font.SysFont("monospace", 42, bold=True)
    police_sous  = pygame.font.SysFont("monospace", 22)

    # ============================================================
    #  BOUCLE PRINCIPALE
    # ============================================================
    while en_cours:

        # --- Événements ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                en_cours = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    en_cours = False
                # Recommencer après game over ou victoire
                if (game_over or victoire) and event.key == pygame.K_r:
                    main()   # relancer
                    return

        if not game_over and not victoire:

            # --- Mise à jour ---
            touches = pygame.key.get_pressed()
            obstacles = niveau.tuiles_obstacle.sprites()
            ennemis   = niveau.ennemis.sprites()

            arno.update(touches, obstacles, ennemis)

            for ennemi in ennemis:
                ennemi.update(arno, obstacles)

            niveau.supprimer_ennemis_morts()
            niveau.camera.mettre_a_jour(arno)

            # --- Conditions de fin ---
            if arno.est_mort():
                game_over = True
            if len(niveau.ennemis) == 0:
                victoire = True

        # ============================================================
        #  DESSIN
        # ============================================================
        ecran.fill(ASPHALTE)   # fond par défaut

        # Monde + ennemis
        niveau.dessiner(ecran, niveau.camera)

        # Joueur
        ecran.blit(arno.image, niveau.camera.appliquer(arno))

        # --- UI : cœurs de vie ---
        arno.dessiner_ui(ecran)

        # --- UI : compteur ennemis ---
        txt_ennemis = police.render(
            f"Ennemis : {len(niveau.ennemis)}", True, BLANC
        )
        ecran.blit(txt_ennemis, (LARGEUR - txt_ennemis.get_width() - 16, 16))

        # --- UI : contrôles (en bas) ---
        txt_ctrl = police.render("Z/Q/S/D : se déplacer   ESPACE : attaquer   ECHAP : quitter", True, (150, 150, 150))
        ecran.blit(txt_ctrl, (LARGEUR // 2 - txt_ctrl.get_width() // 2, HAUTEUR - 30))

        # --- Écran GAME OVER ---
        if game_over:
            _afficher_ecran_fin(ecran, police_titre, police_sous,
                                "GAME OVER", "Arno est tombé...",
                                (200, 40, 40))

        # --- Écran VICTOIRE ---
        if victoire:
            _afficher_ecran_fin(ecran, police_titre, police_sous,
                                "VICTOIRE !", "Le quartier est libre !",
                                (50, 200, 80))

        pygame.display.flip()
        horloge.tick(FPS)

    pygame.quit()
    sys.exit()


def _afficher_ecran_fin(ecran, police_titre, police_sous, titre, sous_titre, couleur):
    """Affiche un écran de fin semi-transparent."""
    # Voile sombre
    voile = pygame.Surface((LARGEUR, HAUTEUR), pygame.SRCALPHA)
    voile.fill((0, 0, 0, 170))
    ecran.blit(voile, (0, 0))

    # Titre
    txt_titre = police_titre.render(titre, True, couleur)
    ecran.blit(txt_titre, (LARGEUR // 2 - txt_titre.get_width() // 2,
                           HAUTEUR // 2 - 60))

    # Sous-titre
    txt_sous = police_sous.render(sous_titre, True, BLANC)
    ecran.blit(txt_sous, (LARGEUR // 2 - txt_sous.get_width() // 2,
                          HAUTEUR // 2))

    # Instruction
    txt_r = police_sous.render("Appuie sur R pour recommencer", True, (180, 180, 180))
    ecran.blit(txt_r, (LARGEUR // 2 - txt_r.get_width() // 2,
                       HAUTEUR // 2 + 50))


if __name__ == "__main__":
    main()
