import pygame

class Weapon(pygame.sprite.Sprite):
    def __init__(self, player, groups): 
        super().__init__(groups)
        
        self.player = player 
        direction = self.player.status.replace('_attack', '')

        # 1. On détermine d'abord la taille et la couleur selon l'arme équipée
        if player.current_weapon == "epee_lego":
            width, height = (45, 15) if direction in ['face_gauche', 'face_droite'] else (15, 35)
            color = (255, 255, 0)
        else:
            width, height = (35, 10) if direction in ['face_gauche', 'face_droite'] else (10, 30)
            color = (255, 50, 50)

        # 2. On crée l'image à sa taille définitive (transparente si tu veux la rendre invisible,
        #    sinon garde le .fill(color) si tu veux la garder visible)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.image.fill(color)

        # 3. On place le rect en fonction de cette taille finale, collé à la hitbox du joueur
        if direction == 'face_droite':
            self.rect = self.image.get_rect(midleft=self.player.hitbox.midright)
        elif direction == 'face_gauche':
            self.rect = self.image.get_rect(midright=self.player.hitbox.midleft)
        elif direction == 'face_haut':
            self.rect = self.image.get_rect(midbottom=self.player.hitbox.midtop)
        else: # face_bas
            self.rect = self.image.get_rect(midtop=self.player.hitbox.midbottom)

        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        # On ne fill() rien : la surface reste transparente, donc invisible à l'écran
