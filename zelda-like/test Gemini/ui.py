import pygame

class UI:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(None, 30) # Police par défaut de Pygame
        self.current_text = ""
        self.text_timer = 0

    def show_message(self, text):
        self.current_text = text
        self.text_timer = pygame.time.get_ticks()

    def display(self, player):
        current_time = pygame.time.get_ticks()
        
        # 1. Dessiner l'inventaire en haut à gauche
        weapon_text = f"Arme: {player.current_weapon if player.current_weapon else 'Aucune'}"
        text_surf = self.font.render(weapon_text, True, (255, 255, 255))
        self.display_surface.blit(text_surf, (20, 20))

        # 2. Dessiner la boîte de dialogue si un texte est actif (pendant 3 secondes)
        if self.current_text and current_time - self.text_timer < 3000:
            # Boîte de fond noir en bas de l'écran
            bg_rect = pygame.Rect(50, 340, 860, 80)
            pygame.draw.rect(self.display_surface, (10, 10, 15), bg_rect)
            pygame.draw.rect(self.display_surface, (255, 255, 255), bg_rect, 2) # Bordure blanche

            # Le texte
            dialogue_surf = self.font.render(str(self.current_text), True, (255, 255, 255))
            self.display_surface.blit(dialogue_surf, (70, 365))
        elif current_time - self.text_timer >= 3000:
            self.current_text = "" # On efface le texte après le délai
