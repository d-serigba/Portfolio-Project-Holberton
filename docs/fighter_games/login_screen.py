import pygame
from api_client import ApiClient  # On importe ton client API unifié

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_BLUE = (173, 216, 230)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

def run_login(screen):
    pygame.font.init()
    font = pygame.font.SysFont("Arial", 24)
    clock = pygame.time.Clock()

    # Initialisation du client API
    api = ApiClient(nom_jeu="brawler")

    # Si un token SSO valide est déjà présent, on passe directement au jeu !
    if api.connecte():
        return api.token, api.user

    # Boîtes de saisie (x, y, largeur, hauteur)
    user_box = pygame.Rect(350, 200, 300, 40)
    pass_box = pygame.Rect(350, 280, 300, 40)
    button_box = pygame.Rect(425, 360, 150, 40)

    user_text = ""
    pass_text = ""
    active_box = "user"  # Qui a le focus au début
    error_message = ""
    success_message = ""

    running = True
    while running:
        screen.fill((30, 30, 40))  # Fond sombre stylé

        # Événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if user_box.collidepoint(event.pos):
                    active_box = "user"
                elif pass_box.collidepoint(event.pos):
                    active_box = "pass"
                elif button_box.collidepoint(event.pos):
                    active_box = "submit"
                    
                    # Tentative de connexion via le client API unifié
                    success, response = api.login(user_text, pass_text)
                    if success:
                        error_message = ""
                        success_message = "Connexion réussie !"
                        running = False  # Ferme l'écran de login et lance le jeu
                    else:
                        error_message = response.get("error", "Identifiants incorrects.")

            if event.type == pygame.KEYDOWN:
                if active_box == "user":
                    if event.key == pygame.K_BACKSPACE:
                        user_text = user_text[:-1]
                    elif event.key != pygame.K_RETURN and event.key != pygame.K_TAB:
                        user_text += event.unicode
                elif active_box == "pass":
                    if event.key == pygame.K_BACKSPACE:
                        pass_text = pass_text[:-1]
                    elif event.key != pygame.K_RETURN and event.key != pygame.K_TAB:
                        pass_text += event.unicode

        # Dessin des box (Changement de couleur si actif)
        pygame.draw.rect(screen, LIGHT_BLUE if active_box == "user" else GRAY, user_box, 2)
        pygame.draw.rect(screen, LIGHT_BLUE if active_box == "pass" else GRAY, pass_box, 2)
        pygame.draw.rect(screen, GREEN, button_box)

        # Rendu des textes
        draw_text("CONNEXION", font, WHITE, screen, 430, 130)
        draw_text("Username:", font, WHITE, screen, 230, 205)
        draw_text("Password:", font, WHITE, screen, 230, 285)
        
        # Affichage du texte tapé (on masque le mot de passe)
        draw_text(user_text, font, WHITE, screen, user_box.x + 5, user_box.y + 5)
        draw_text("*" * len(pass_text), font, WHITE, screen, pass_box.x + 5, pass_box.y + 5)
        draw_text("Valider", font, BLACK, screen, button_box.x + 40, button_box.y + 5)

        # Messages d'erreur ou succès
        if error_message:
            draw_text(error_message, font, RED, screen, 350, 430)
        if success_message:
            draw_text(success_message, font, GREEN, screen, 350, 430)

        pygame.display.flip()
        clock.tick(30)

    return api.token, api.user

def draw_text(text, font, color, surface, x, y):
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, (x, y))
