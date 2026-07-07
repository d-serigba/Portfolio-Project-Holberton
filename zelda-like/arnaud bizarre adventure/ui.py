import pygame

class UI:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(None, 24)
        self.queue = []
        self.current_text = ""
        self.text_timer = 0
        self.duration = 4000 # Chaque message dure 4 secondes lors des cinématiques
        self.cinematic_active = False

    def show_message(self, text):
        if isinstance(text, list):
            self.queue.extend(text)
        else:
            self.queue.append(text)

        if not self.current_text:
            self.next_message()

    def next_message(self):
        if self.queue:
            self.current_text = self.queue.pop(0)
            self.text_timer = pygame.time.get_ticks()
        else:
            self.current_text = ""
            self.cinematic_active = False

    def display(self, player):
        current_time = pygame.time.get_ticks()
        
        # 1. Barre de Vie (En haut à gauche)
        bar_rect = pygame.Rect(20, 20, 150, 15)
        pygame.draw.rect(self.display_surface, (40, 40, 40), bar_rect)
        health_ratio = player.health / player.max_health
        if health_ratio > 0:
            current_bar_rect = pygame.Rect(20, 20, int(150 * health_ratio), 15)
            pygame.draw.rect(self.display_surface, (230, 40, 40), current_bar_rect)
        pygame.draw.rect(self.display_surface, (255, 255, 255), bar_rect, 1)

        # 2. BANDEAU D'INVENTAIRE VISUEL (En haut à droite)
        # On dessine 4 cases pour tes 4 items de progression
        items_list = ["opinel", "epee_lego", "lunettes_baceux", "koenigsegg"]
        start_x = self.display_surface.get_size()[0] - 220
        
        for i, item in enumerate(items_list):
            slot_rect = pygame.Rect(start_x + (i * 50), 15, 40, 40)
            # Si le joueur possède l'item, la case s'illumine en bleu/doré, sinon fond sombre
            has_item = player.inventory.get(item, False)
            bg_color = (60, 60, 80) if has_item else (20, 20, 25)
            
            pygame.draw.rect(self.display_surface, bg_color, slot_rect)
            # Bordure dorée pour l'arme actuellement équipée
            border_color = (255, 215, 0) if player.current_weapon == item else (100, 100, 100)
            pygame.draw.rect(self.display_surface, border_color, slot_rect, 2)
            
            # Petit texte indicateur en attendant tes icônes d'items
            if has_item:
                short_name = item[:3].upper() # OPI, EPE, LUN, KOE
                item_text = self.font.render(short_name, True, (255, 255, 255))
                self.display_surface.blit(item_text, (slot_rect.x + 5, slot_rect.y + 12))

        # 3. Boîte de dialogue en bas (Reste inchangée)
        if self.current_text:
            if current_time - self.text_timer < self.duration:
                screen_width, screen_height = self.display_surface.get_size()
                box_height = 90
                box_y = screen_height - box_height - 20
                
                bg_rect = pygame.Rect(50, box_y, screen_width - 100, box_height)
                pygame.draw.rect(self.display_surface, (10, 10, 15), bg_rect)
                pygame.draw.rect(self.display_surface, (255, 255, 255), bg_rect, 2)

                dialogue_surf = self.font.render(str(self.current_text), True, (255, 255, 255))
                self.display_surface.blit(dialogue_surf, (70, box_y + 35))
            else:
                self.next_message()
