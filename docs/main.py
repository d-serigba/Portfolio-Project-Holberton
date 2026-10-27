# ============================================================
#   GAME HUB PORTFOLIO — main.py (Launcher Central)
#   Gère l'authentification unique et la distribution des jeux
# ============================================================

import pygame
import sys
import subprocess
import os
import json
from login_screen import run_login

# Dimensions standardisées pour le Hub
LARGEUR, HAUTEUR = 800, 600

# Chemins absolus (indépendants du dossier de lancement)
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE = os.path.join(BASE_DIR, "token.json")   # même fichier que les api_client.py

JEUX = {
    "brawler": {
        "label": "1. FIGHTING GAME (Brawler)",
        "touche": pygame.K_1,
        "couleur": (241, 196, 15),
        "dossier": os.path.join(BASE_DIR, "fighter_games"),
        "script": "main.py",
    },
    "metroidvania": {
        "label": "2. METROIDVANIA (Arnaud)",
        "touche": pygame.K_2,
        "couleur": (155, 89, 182),
        "dossier": os.path.join(BASE_DIR, "metroidvania"),
        "script": "main.py",
    },
    "zelda": {
        "label": "3. ARNO'S BIZARRE ADVENTURE",
        "touche": pygame.K_3,
        "couleur": (52, 152, 219),
        "dossier": os.path.join(BASE_DIR, "zelda-like", "arnaud_bizarre_adventure"),
        "script": "main.py",
    },
}


def ecran_hub(ecran, pseudo):
    """Affiche le sélecteur graphique des jeux."""
    font = pygame.font.SysFont("monospace", 26, bold=True)
    small_font = pygame.font.SysFont("monospace", 18)
    horloge = pygame.time.Clock()

    while True:
        ecran.fill((20, 24, 35))

        txt_title = font.render("=== PORTFOLIO GAME HUB ===", True, (255, 255, 255))
        txt_user  = small_font.render(f"Joueur connecté : {pseudo}", True, (46, 204, 113))
        txt_esc   = small_font.render("ECHAP : quitter  |  D : se déconnecter", True, (149, 165, 166))

        ecran.blit(txt_title, (LARGEUR // 2 - txt_title.get_width() // 2, 60))
        ecran.blit(txt_user, (30, 20))

        y = 200
        for jeu in JEUX.values():
            ecran.blit(font.render(jeu["label"], True, jeu["couleur"]), (80, y))
            y += 80

        ecran.blit(txt_esc, (80, 500))
        pygame.display.flip()
        horloge.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_d:
                    return "deconnexion"
                for cle, jeu in JEUX.items():
                    if event.key == jeu["touche"]:
                        return cle


def sauvegarder_token(token, pseudo):
    """Écrit la session dans le fichier partagé par tous les jeux."""
    with open(TOKEN_FILE, "w") as f:
        json.dump({"token": token, "user": pseudo}, f)
    print(f"[Hub] Session enregistrée dans {TOKEN_FILE}")


def supprimer_token():
    """Déconnexion : efface la session partagée."""
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)
    print("[Hub] Session supprimée")


def lancer_jeu(cle):
    jeu = JEUX[cle]
    chemin = os.path.join(jeu["dossier"], jeu["script"])
    if not os.path.exists(chemin):
        print(f"[Hub] Jeu introuvable : {chemin}")
        return
    print(f"[Hub] Lancement de {cle}...")
    subprocess.run([sys.executable, jeu["script"]], cwd=jeu["dossier"])


def se_connecter(ecran):
    """Affiche le login. Retourne (token, pseudo) ou (None, None) si annulé."""
    url_login = "http://127.0.0.1:5000/api/auth/login"
    token, pseudo = run_login(ecran, url_login)
    if token and pseudo:
        sauvegarder_token(token, pseudo)
    return token, pseudo


def main():
    pygame.init()
    ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
    pygame.display.set_caption("Game Hub Central")

    token, pseudo = se_connecter(ecran)
    if not token or not pseudo:
        print("[Hub] Connexion annulée ou échouée — fermeture.")
        pygame.quit()
        sys.exit()

    while True:
        choix = ecran_hub(ecran, pseudo)

        if choix == "deconnexion":
            supprimer_token()
            token, pseudo = se_connecter(ecran)
            if not token or not pseudo:
                pygame.quit()
                sys.exit()
            continue

        lancer_jeu(choix)

        # Les jeux changent la fenêtre : on la restaure au retour
        ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
        pygame.display.set_caption("Game Hub Central")


if __name__ == "__main__":
    main()
