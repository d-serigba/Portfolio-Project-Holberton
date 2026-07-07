import pygame

class NPC(pygame.sprite.Sprite):
    def __init__(self, pos, groups, obstacle_sprites):
        super().__init__(groups)
        self.image = pygame.Surface((48, 64))
        self.image.fill((153, 51, 153))
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(-10, -26)
        obstacle_sprites.add(self)

        self.interaction_count = 0
        
        # --- Variables pour le Timer ---
        self.is_delivering_item = False
        self.timer_start = 0
        self.player_ref = None # Pour garder la trace d'Arnaud pendant le timer

    def interact(self, player):
        # 1. Si on a déjà fini toute la séquence (état final)
        if self.interaction_count >= 1:
            player.ui.show_message("Arthur: Fuis vers le metro maintenant, Arnaud ! Courage !")
            return

        # 2. Début de la séquence (le joueur interagit pour la première fois)
        if not self.is_delivering_item:
            # Affiche Texte 1
            player.ui.show_message("Arthur: Hein ? Tu as recu un message bizarre des brothers ? Ok tu peux y aller mais attends...")
            
            # Lance le timer silencieux
            self.is_delivering_item = True
            self.timer_start = pygame.time.get_ticks()
            self.player_ref = player

    def update(self):
        # 3. Cette fonction tourne en boucle en arrière-plan
        if self.is_delivering_item:
            current_time = pygame.time.get_ticks()
            
            # On vérifie si 2500 millisecondes (2,5 secondes) se sont écoulées
            if current_time - self.timer_start > 2500:
                
                # Le temps est écoulé ! On arrête le chrono
                self.is_delivering_item = False
                self.interaction_count = 1
                
                # Ajout de l'Opinel silencieusement
                self.player_ref.inventory["opinel"] = True
                self.player_ref.current_weapon = "opinel"
                
                # Affiche Texte 2 (la suite s'enchaîne toute seule !)
                self.player_ref.ui.show_message([
                    "Arthur: L'ambiance au metro est terrifiante. C'est dangereux là-bas, prends cet Opinel !",
                    "-> Vous avez obtenu l'Opinel ! Vite au métro !"
                ])
