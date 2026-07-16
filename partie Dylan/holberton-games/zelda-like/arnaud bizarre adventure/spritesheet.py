import pygame

class SpriteSheet:
    def __init__(self, filename):
        try:
            # On charge avec convert_alpha() pour garder les canaux transparents
            self.sheet = pygame.image.load(filename).convert_alpha()
        except pygame.error as e:
            print(f"Impossible de charger la spritesheet : {filename}")
            raise SystemExit(e)

    def get_image(self, frame_x, frame_y, width, height, scale=4):
        """Découpe proprement une frame et l'agrandit sans flou"""
        # 1. On crée une surface vierge transparente à la taille d'origine (16x16)
        image = pygame.Surface((width, height), pygame.SRCALPHA).convert_alpha()
        
        # 2. On blit le morceau de la spritesheet dessus
        image.blit(self.sheet, (0, 0), (frame_x * width, frame_y * height, width, height))
        
        # 3. On applique le zoom net (Nearest Neighbor)
        if scale != 1:
            new_size = (width * scale, height * scale)
            image = pygame.transform.scale(image, new_size)
            
        return image
