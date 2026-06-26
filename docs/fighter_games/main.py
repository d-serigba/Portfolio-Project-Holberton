import pygame

pygame.init()

#create game window
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("brawler")

#function for drawing background
def draw_bg():
    scaled_bg = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(scaled_bg, (0, 0))

#load background image
bg_image = pygame.image.load("asset/images/background/background.png").convert_alpha()

#game loop
run = True
while run:

    #draw background
    draw_bg()

    #event handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    

    #update display
    pygame.display.update() 

#exit pygame
pygame.quit()
