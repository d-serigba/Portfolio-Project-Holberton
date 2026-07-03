# ============================================================
#   ARNAUD METROIDVANIA — main.py
# ============================================================

import pygame
import sys
import os
import json
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

    # ── RÉCUPÉRATION AUTOMATIQUE DE LA SESSION DU HUB ───────────
    pseudo_joueur = "Guest"
    token_joueur = None
    token_path = os.path.join(os.path.dirname(__file__), "save", "token.json")
    
    if os.path.exists(token_path):
        try:
            with open(token_path) as f:
                data = json.load(f)
                pseudo_joueur = data.get("user", "Guest")
                token_joueur = data.get("token")
                print(f"[Metroidvania] Session Hub chargée : {pseudo_joueur}")
        except:
            pass

    # ── LOGIQUE DU JEU ──────────────────────────────────────────
    jeu = Facade()
    jeu.token_joueur = token_joueur
    jeu.pseudo_joueur = pseudo_joueur

    en_cours = True

    while en_cours:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                en_cours = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    en_cours = False
                if not jeu.game_over:
                    if event.key in (pygame.K_z, pygame.K_UP, pygame.K_SPACE):
                        jeu.arnaud.trigger_saut()
                    if event.key == pygame.K_LSHIFT:
                        jeu.arnaud.trigger_esquive()
                    if event.key in (pygame.K_c, pygame.K_l):
                        if jeu.arnaud.capacites["lego_blast"]:
                            proj = jeu.arnaud.trigger_lego_blast()
                            if proj:
                                from map.zone_a import MissileTourelle
                                m = MissileTourelle(proj["x"], proj["y"], proj["dx"])
                                jeu.projectiles.add(m)
                    if event.key == pygame.K_F1:
                        jeu.arnaud.debloquer("double_saut")
                    if event.key == pygame.K_F2:
                        jeu.debug_debloquer_tout()
                    if event.key == pygame.K_F3:
                        jeu.debug_mode = not jeu.debug_mode
                    if event.key == pygame.K_F4:
                        jeu.debug_zone_suivante()
                    if event.key == pygame.K_F5:
                        jeu.debug_zone_precedente()
                if jeu.game_over and event.key == pygame.K_r:
                    jeu.recommencer()

        touches = pygame.key.get_pressed()
        jeu.update(touches, None)

        ecran.fill(BLEU_FOND)
        jeu.dessiner(ecran)

        if jeu.debug_mode:
            jeu.dessiner_debug(ecran, police)

        draw_player_info = police.render(f"Joueur: {pseudo_joueur}", True, (255, 255, 255))
        ecran.blit(draw_player_info, (15, 15))

        ctrl = police.render("Z:saut  SHIFT:esquive  S:accroupir  X:épée  C:blast  ECHAP:quitter", True, (80, 80, 100))
        ecran.blit(ctrl, (LARGEUR//2 - ctrl.get_width()//2, HAUTEUR - 22))

        if jeu.game_over:
            voile = pygame.Surface((LARGEUR, HAUTEUR), pygame.SRCALPHA)
            voile.fill((0, 0, 0, 170))
            ecran.blit(voile, (0, 0))
            t1 = police_gd.render("GAME OVER", True, ROUGE)
            t2 = police_m.render(f"{pseudo_joueur} n'a plus de vies...", True, BLANC)
            t3 = police_m.render("R pour recommencer", True, (180, 180, 180))
            ecran.blit(t1, (LARGEUR//2 - t1.get_width()//2, HAUTEUR//2 - 60))
            ecran.blit(t2, (LARGEUR//2 - t2.get_width()//2, HAUTEUR//2))
            ecran.blit(t3, (LARGEUR//2 - t3.get_width()//2, HAUTEUR//2 + 40))

        pygame.display.flip()
        horloge.tick(FPS)

    jeu.calculer_et_envoyer_score()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
