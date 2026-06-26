import pygame

pygame.init()

#create game window
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREN_WIDTH? SCREEN_HEIGHT))
pygame.display.set_caption("brawler")

#function for drawing background
def draw_bg():
    screen.blit(bg_images, (0, 0))

#load background image
bg_image = pygame.image.load("assets/images/background/background.jpg").convert_alpha()

#game loop
run = True
while run:

    #draw background
    draw_bg
    #event handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False


#exit pygame
pygame.quit()
