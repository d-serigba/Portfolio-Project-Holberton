# ============================================================
#   GAME HUB PORFOLIO — main.py (Launcher Central)
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

def ecran_hub(ecran, pseudo):
    """Affiche le sélecteur graphique des deux jeux."""
    font = pygame.font.SysFont("monospace", 26, bold=True)
    small_font = pygame.font.SysFont("monospace", 18)
    
    while True:
        ecran.fill((20, 24, 35)) # Fond sombre bleuté moderne
        
        # En-têtes
        txt_title = font.render("=== PORTFOLIO GAME HUB ===", True, (255, 255, 255))
        txt_user  = small_font.render(f"Joueur connecté : {pseudo}", True, (46, 204, 113))
        
        # Options de jeux
        txt_g1 = font.render("1. Lancer FIGHTING GAME (Brawler)", True, (241, 196, 15))
        txt_g2 = font.render("2. Lancer METROIDVANIA (Arnaud)", True, (155, 89, 182))
        txt_esc = small_font.render("Appuie sur ECHAP pour quitter l'application", True, (149, 165, 166))
        
        # Affichage (Blit)
        ecran.blit(txt_title, (LARGEUR // 2 - txt_title.get_width() // 2, 60))
        ecran.blit(txt_user,  (30, 20))
        ecran.blit(txt_g1,    (80, 220))
        ecran.blit(txt_g2,    (80, 300))
        ecran.blit(txt_esc,   (80, 480))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_1:
                    return "brawler"
                if event.key == pygame.K_2:
                    return "metroidvania"

def forcer_sauvegarde_token(token, pseudo):
    """Partage la session avec les deux sous-jeux via leurs fichiers de sauvegarde token."""
    # Sûreté sur les valeurs
    tk = token if token else "mock_token_12345"
    ps = pseudo if pseudo else "admin"
    
    data = {"token": tk, "user": ps}
    
    # Écriture pour le Metroidvania
    path_mv = os.path.join("metroidvania", "save", "token.json")
    os.makedirs(os.path.dirname(path_mv), exist_ok=True)
    with open(path_mv, "w") as f:
        json.dump(data, f)
        
    # Écriture pour le Brawler
    path_br = os.path.join("fighter_games", "save", "token.json")
    os.makedirs(os.path.dirname(path_br), exist_ok=True)
    with open(path_br, "w") as f:
        json.dump(data, f)
        
    print("[Hub] Session synchronisée localement dans token.json")

def main():
    pygame.init()
    ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
    pygame.display.set_caption("Game Hub Central")
    
    # 1. CONNEXION UNIQUE VIA L'API FLASK
    URL_LOGIN = "http://127.0.0.1:5000/api/auth/login"
    print("[Hub] Ouverture de la fenêtre de connexion...")
    token_joueur, pseudo_joueur = run_login(ecran, URL_LOGIN)
    
    # Si le login screen a renvoyé None mais qu'on a tapé un pseudo, on évite le crash
    if not pseudo_joueur:
        pseudo_joueur = "admin"
        
    print(f"[Hub DEBUG] Session obtenue -> Pseudo: {pseudo_joueur}, Token: {token_joueur}")
    
    # Injecte la session dans les sous-dossiers pour court-circuiter leurs écrans de login
    forcer_sauvegarde_token(token_joueur, pseudo_joueur)
    
    # 2. ACCÈS AU HUB
    while True:
        choix = ecran_hub(ecran, pseudo_joueur)
        
        if choix == "brawler":
            print(f"[Hub] Chargement de Brawler...")
            # On lance le Brawler original (sans injecter d'arguments sys.argv qui le feraient planter)
            subprocess.run([sys.executable, "main.py"], cwd="fighter_games")
            
        elif choix == "metroidvania":
            print(f"[Hub] Chargement de Metroidvania...")
            # On lance le Metroidvania original d'Arnaud (sans arguments additionnels)
            subprocess.run([sys.executable, "main.py"], cwd="metroidvania")

if __name__ == "__main__":
    main()
