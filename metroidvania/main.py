# ============================================================
#  ARNAUD METROIDVANIA — main.py
#
#  Rôle unique : boucle pygame + events.
#  Toute la logique est dans facade.py.
#
#  CONTRÔLES :
#    Q / ←          → gauche
#    D / →          → droite
#    S / ↓          → accroupir
#    Z / ↑ / ESPACE → sauter
#    SHIFT gauche   → esquiver
#    X / K          → attaquer
#    C / L          → Légo Blast (si débloqué)
#    F1             → débloquer double saut
#    F2             → débloquer tout
#    F3             → toggle debug
#    F4             → zone suivante (debug)
#    F5             → zone précédente (debug)
#    R              → recommencer (game over)
#    ECHAP          → quitter
# ============================================================

import pygame
import sys
from settings import *
from facade   import Facade


def main():
    pygame.init()
    ecran    = pygame.display.set_mode((LARGEUR, HAUTEUR))
    pygame.display.set_caption(TITRE)
    horloge  = pygame.time.Clock()
    police   = pygame.font.SysFont("monospace", 15, bold=True)
    police_gd = pygame.font.SysFont("monospace", 38, bold=True)
    police_m  = pygame.font.SysFont("monospace", 20)

    # ── Toute la logique du jeu est dans la façade ────────────
    jeu = Facade()

    en_cours = True

    while en_cours:

        # ── ÉVÉNEMENTS ────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                en_cours = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    en_cours = False

                if not jeu.game_over:
                    # Saut (avec coyote time via la façade)
                    if event.key in (pygame.K_z, pygame.K_UP, pygame.K_SPACE):
                        jeu.trigger_saut()

                    # Esquive
                    if event.key == pygame.K_LSHIFT:
                        jeu.arnaud.trigger_esquive()

                    # Légo Blast
                    if event.key in (pygame.K_c, pygame.K_l):
                        if jeu.arnaud.capacites["lego_blast"]:
                            jeu.arnaud.trigger_lego_blast()

                    # Debug
                    if event.key == pygame.K_F1:
                        jeu.arnaud.debloquer("double_saut")
                        print("[DEBUG] Double saut débloqué")
                    if event.key == pygame.K_F2:
                        jeu.debug_debloquer_tout()
                    if event.key == pygame.K_F3:
                        jeu.debug_mode = not jeu.debug_mode
                    if event.key == pygame.K_F4:
                        jeu.debug_zone_suivante()
                    if event.key == pygame.K_F5:
                        jeu.debug_zone_precedente()

                # Recommencer après game over
                if jeu.game_over and event.key == pygame.K_r:
                    jeu.recommencer()

        # ── MISE À JOUR ───────────────────────────────────────
        touches = pygame.key.get_pressed()
        jeu.update(touches, None)

        # ── DESSIN ────────────────────────────────────────────
        ecran.fill(BLEU_FOND)
        jeu.dessiner(ecran)

        if jeu.debug_mode:
            jeu.dessiner_debug(ecran, police)

        # Contrôles bas d'écran
        ctrl = police.render(
            "Z:saut  SHIFT:esquive  S:accroupir  X:épée  C:blast  F4/F5:zones  ECHAP:quitter",
            True, (80, 80, 100)
        )
        ecran.blit(ctrl, (LARGEUR//2 - ctrl.get_width()//2, HAUTEUR - 22))

        # Game Over
        if jeu.game_over:
            voile = pygame.Surface((LARGEUR, HAUTEUR), pygame.SRCALPHA)
            voile.fill((0, 0, 0, 170))
            ecran.blit(voile, (0, 0))
            t1 = police_gd.render("GAME OVER", True, ROUGE)
            t2 = police_m.render("Arnaud n'a plus de vies...", True, BLANC)
            t3 = police_m.render("R pour recommencer", True, (180, 180, 180))
            ecran.blit(t1, (LARGEUR//2 - t1.get_width()//2, HAUTEUR//2 - 60))
            ecran.blit(t2, (LARGEUR//2 - t2.get_width()//2, HAUTEUR//2))
            ecran.blit(t3, (LARGEUR//2 - t3.get_width()//2, HAUTEUR//2 + 40))

        pygame.display.flip()
        horloge.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
