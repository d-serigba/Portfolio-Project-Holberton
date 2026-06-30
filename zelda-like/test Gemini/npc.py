import pygame

class NPC(pygame.sprite.Sprite):
    def __init__(self, pos, groups, obstacle_sprites):
        super().__init__(groups)
        self.image = pygame.Surface((48, 64))
        self.image.fill((153, 51, 153)) # Violet
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(-10, -26)
        obstacle_sprites.add(self)

        # Une chaîne de caractères simple et propre
        self.dialogue = "C'est dangereux ici prends ceci..."
        self.has_given_item = False

    def interact(self, player):
        if not self.has_given_item:
            player.inventory["opinel"] = True
            player.current_weapon = "opinel"
            
            # On envoie le texte directement à l'UI
            player.ui.show_message(self.dialogue)
            self.has_given_item = True
        else:
            player.ui.show_message("Fuis vers le metro maintenant, Arnaud !")
