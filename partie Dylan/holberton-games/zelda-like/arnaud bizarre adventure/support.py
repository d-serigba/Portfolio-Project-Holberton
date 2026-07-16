import pygame

def import_sprite_sheet(chemin, largeur_frame, hauteur_frame):
    """
    Découpe une grande feuille de sprites en petites images individuelles.
    Retourne une liste de surfaces Pygame.
    """
    sheet = pygame.image.load(chemin).convert_alpha()
    largeur_sheet, hauteur_sheet = sheet.get_size()
    frames = []
    
    # On parcourt la grille de haut en bas et de gauche à droite
    for y in range(0, hauteur_sheet, hauteur_frame):
        for x in range(0, largeur_sheet, largeur_frame):
            # On crée un cache transparent de la taille d'une frame
            frame = pygame.Surface((largeur_frame, hauteur_frame), pygame.SRCALPHA)
            # On "tamponne" la portion de la grande image sur notre cache
            frame.blit(sheet, (0, 0), (x, y, largeur_frame, hauteur_frame))
            frames.append(frame)
            
    return frames
