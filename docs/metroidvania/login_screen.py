import pygame
from api_client import ApiClient

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

    api = ApiClient()

    # SSO : si un token valide existe déjà (Hub ou autre jeu), on saute le login
    if api.connecte():
        return api.token, api.user

    user_box = pygame.Rect(350, 200, 300, 40)
    pass_box = pygame.Rect(350, 280, 300, 40)
    button_box = pygame.Rect(425, 360, 150, 40)

    user_text = ""
    pass_text = ""
    active_box = "user"
    error_message = ""
    success_message = ""

    running = True
    while running:
        screen.fill((30, 30, 40))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == pygame.MOUSEBUTTONDOWN:
                if user_box.collidepoint(event.pos):
                    active_box = "user"
                elif pass_box.collidepoint(event.pos):
                    active_box = "pass"
                elif button_box.collidepoint(event.pos):
                    success, response = api.login(user_text, pass_text)
                    if success:
                        error_message = ""
                        success_message = "Connexion réussie !"
                        running = False
                    else:
                        error_message = response.get("error", "Identifiants incorrects.")

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    active_box = "pass" if active_box == "user" else "user"
                elif event.key == pygame.K_RETURN:
                    success, response = api.login(user_text, pass_text)
                    if success:
                        running = False
                    else:
                        error_message = response.get("error", "Identifiants incorrects.")
                elif active_box == "user":
                    if event.key == pygame.K_BACKSPACE:
                        user_text = user_text[:-1]
                    else:
                        user_text += event.unicode
                elif active_box == "pass":
                    if event.key == pygame.K_BACKSPACE:
                        pass_text = pass_text[:-1]
                    else:
                        pass_text += event.unicode

        pygame.draw.rect(screen, LIGHT_BLUE if active_box == "user" else GRAY, user_box, 2)
        pygame.draw.rect(screen, LIGHT_BLUE if active_box == "pass" else GRAY, pass_box, 2)
        pygame.draw.rect(screen, GREEN, button_box)

        draw_text("CONNEXION", font, WHITE, screen, 430, 130)
        draw_text("Username:", font, WHITE, screen, 230, 205)
        draw_text("Password:", font, WHITE, screen, 230, 285)
        draw_text(user_text, font, WHITE, screen, user_box.x + 5, user_box.y + 5)
        draw_text("*" * len(pass_text), font, WHITE, screen, pass_box.x + 5, pass_box.y + 5)
        draw_text("Valider", font, BLACK, screen, button_box.x + 40, button_box.y + 5)

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
