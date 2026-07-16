# ============================================================
#   ARNAUD METROIDVANIA — main_web.py
#   Version ADAPTÉE POUR PYGBAG (exécution dans le navigateur)
#
#   À UTILISER AVEC : state_manager_web.py (renommé state_manager.py)
#                     api_client_web.py    (renommé api_client.py)
#                     dans le dossier de build web uniquement.
#                     Gardez les fichiers originaux pour l'exécution locale.
#
#   CHANGEMENTS PAR RAPPORT À main.py :
#   1. Boucle principale devenue async (obligatoire pour pygbag)
#   2. Session (pseudo + token) lue depuis l'URL de la page plutôt
#      que depuis save/token.json (qui n'existe pas dans le navigateur)
#   3. Sauvegarde de progression (SQLite) neutralisée via
#      state_manager_web.py — le score envoyé au hub, lui, reste actif
#      via api_client_web.py (voir ce fichier pour le détail)
# ============================================================

import asyncio
import sys
import os
from settings import *
from facade import Facade


def lire_session_depuis_url():
    """
    Récupère pseudo + token depuis l'URL de la page, par ex :
    metroidvania.html?player=Alice&token=abcde
    C'est exactement ce que fabrique déjà index.html quand il fait :
        window.location.href = `${jeuId}.html?player=...&token=...`
    """
    pseudo, token = "Guest", None

    if sys.platform == "emscripten":
        try:
            import platform
            from urllib.parse import parse_qs, urlparse

            href = platform.window.location.href
            query = urlparse(href).query
            params = parse_qs(query)
            pseudo = params.get("player", [pseudo])[0]
            token = params.get("token", [None])[0]
        except Exception as e:
            print(f"[Metroidvania Web] Impossible de lire l'URL : {e}")
    else:
        pseudo, token = "TestLocal", None

    return pseudo, token


async def main():
    import pygame

    pygame.init()
    ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
    pygame.display.set_caption(TITRE)
    horloge = pygame.time.Clock()
    police = pygame.font.SysFont("monospace", 15, bold=True)
    police_gd = pygame.font.SysFont("monospace", 38, bold=True)
    police_m = pygame.font.SysFont("monospace", 20)
    # ⚠️ Comme pour le brawler, SysFont n'est pas fiable dans un navigateur
    # (pas de polices système). Si le texte ne s'affiche pas bien une fois
    # testé, remplacez ces 3 lignes par pygame.font.Font(chemin_ttf, taille)
    # avec une police .ttf embarquée dans les assets du jeu.

    # ── SESSION RÉCUPÉRÉE DEPUIS L'URL (au lieu de save/token.json) ──
    pseudo_joueur, token_joueur = lire_session_depuis_url()
    print(f"[Metroidvania Web] Session : {pseudo_joueur}")

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
        ecran.blit(ctrl, (LARGEUR // 2 - ctrl.get_width() // 2, HAUTEUR - 22))

        if jeu.game_over:
            import pygame as pg
            voile = pg.Surface((LARGEUR, HAUTEUR), pg.SRCALPHA)
            voile.fill((0, 0, 0, 170))
            ecran.blit(voile, (0, 0))
            t1 = police_gd.render("GAME OVER", True, ROUGE)
            t2 = police_m.render(f"{pseudo_joueur} n'a plus de vies...", True, BLANC)
            t3 = police_m.render("R pour recommencer", True, (180, 180, 180))
            ecran.blit(t1, (LARGEUR // 2 - t1.get_width() // 2, HAUTEUR // 2 - 60))
            ecran.blit(t2, (LARGEUR // 2 - t2.get_width() // 2, HAUTEUR // 2))
            ecran.blit(t3, (LARGEUR // 2 - t3.get_width() // 2, HAUTEUR // 2 + 40))

        pygame.display.flip()
        horloge.tick(FPS)

        # 🔁 CHANGEMENT CLÉ : indispensable pour pygbag, sinon la page se fige.
        await asyncio.sleep(0)

    # Score envoyé au hub via api_client_web.py (postMessage), même si la
    # progression SQLite est désactivée pour cette version web.
    jeu.calculer_et_envoyer_score()
    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
