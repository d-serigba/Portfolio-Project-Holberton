import pygame
import requests

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_BLUE = (173, 216, 230)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (70, 120, 220)

BASE_URL = "http://127.0.0.1:5000/api/auth"


def draw_text(text, font, color, surface, x, y):
    surface.blit(font.render(text, True, color), (x, y))


def appeler_api(route, username, password):
    """Appelle /login ou /register. Retourne (token, username, erreur)."""
    try:
        r = requests.post(
            f"{BASE_URL}/{route}",
            json={"username": username, "password": password},
            timeout=5,
        )
    except requests.exceptions.RequestException:
        return None, None, "Serveur injoignable (Flask lancé ?)"

    if r.status_code in (200, 201):
        data = r.json()
        user_info = data.get("user", {})
        return data.get("token"), user_info.get("username", username), ""

    try:
        erreur = r.json().get("error", "Erreur inconnue.")
    except ValueError:
        erreur = f"Erreur serveur ({r.status_code})."
    return None, None, erreur


def run_login(screen, url_api=None):
    """
    Affiche l'écran de connexion / inscription.
    Retourne (token, username) ou (None, None) si l'utilisateur ferme la fenêtre.
    Le fichier token.json est géré par le Hub, pas ici.
    """
    pygame.font.init()
    font = pygame.font.SysFont("Arial", 24)
    clock = pygame.time.Clock()

    user_box = pygame.Rect(350, 200, 300, 40)
    pass_box = pygame.Rect(350, 280, 300, 40)
    login_btn = pygame.Rect(230, 360, 200, 40)
    register_btn = pygame.Rect(470, 360, 200, 40)

    user_text = ""
    pass_text = ""
    active_box = "user"
    message = ""
    message_color = RED
    en_attente = False

    while True:
        screen.fill((30, 30, 40))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None, None

            if event.type == pygame.MOUSEBUTTONDOWN and not en_attente:
                if user_box.collidepoint(event.pos):
                    active_box = "user"
                elif pass_box.collidepoint(event.pos):
                    active_box = "pass"
                elif login_btn.collidepoint(event.pos):
                    route = "login"
                elif register_btn.collidepoint(event.pos):
                    route = "register"
                else:
                    route = None

                if route:
                    en_attente = True
                    message, message_color = "Connexion en cours...", GRAY
                    # Rendu immédiat du message avant l'appel réseau
                    screen.fill((30, 30, 40))
                    pygame.display.flip()

                    token, pseudo, erreur = appeler_api(route, user_text, pass_text)
                    en_attente = False
                    if token:
                        return token, pseudo
                    message, message_color = erreur, RED

            if event.type == pygame.KEYDOWN and not en_attente:
                if event.key == pygame.K_TAB:
                    active_box = "pass" if active_box == "user" else "user"
                elif event.key == pygame.K_RETURN:
                    # Entrée = connexion
                    en_attente = True
                    message, message_color = "Connexion en cours...", GRAY
                    screen.fill((30, 30, 40))
                    pygame.display.flip()

                    token, pseudo, erreur = appeler_api("login", user_text, pass_text)
                    en_attente = False
                    if token:
                        return token, pseudo
                    message, message_color = erreur, RED
                elif event.key == pygame.K_BACKSPACE:
                    if active_box == "user":
                        user_text = user_text[:-1]
                    else:
                        pass_text = pass_text[:-1]
                elif event.unicode:
                    if active_box == "user":
                        user_text += event.unicode
                    else:
                        pass_text += event.unicode

        # Cadres des champs
        pygame.draw.rect(screen, LIGHT_BLUE if active_box == "user" else GRAY, user_box, 2)
        pygame.draw.rect(screen, LIGHT_BLUE if active_box == "pass" else GRAY, pass_box, 2)

        # Boutons
        pygame.draw.rect(screen, GREEN, login_btn)
        pygame.draw.rect(screen, BLUE, register_btn)

        # Textes
        draw_text("CONNEXION", font, WHITE, screen, 430, 130)
        draw_text("Username:", font, WHITE, screen, 230, 205)
        draw_text("Password:", font, WHITE, screen, 230, 285)
        draw_text(user_text, font, WHITE, screen, user_box.x + 5, user_box.y + 5)
        draw_text("*" * len(pass_text), font, WHITE, screen, pass_box.x + 5, pass_box.y + 5)
        draw_text("SE CONNECTER", font, BLACK, screen, login_btn.x + 15, login_btn.y + 5)
        draw_text("CRÉER UN COMPTE", font, WHITE, screen, register_btn.x + 10, register_btn.y + 5)

        if message:
            draw_text(message, font, message_color, screen, 230, 430)

        pygame.display.flip()
        clock.tick(30)
