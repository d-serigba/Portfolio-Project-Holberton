import pygame
import os
import sys
import json
import time
import random

# Permet d'éviter les soucis audio sur certaines configs WSL/Linux
os.environ["SDL_AUDIODRIVER"] = "dummy"
from pygame import mixer
from fighter import Fighter
from api_client import ApiClient
from login_screen import run_login  # <--- IMPORT DE L'ÉCRAN DE CONNEXION UNIFIÉ

mixer.init()
pygame.init()

# Récupération du dossier absolu où se trouve ce fichier main.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Brawler")
clock = pygame.time.Clock()
FPS = 60

RED = (255, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Sécurisation des chemins d'accès aux assets
def get_asset_path(relative_path):
    return os.path.join(BASE_DIR, relative_path)

# ── INITIALISATION DE L'API & CONNEXION / SSO ──────────────
api = ApiClient(nom_jeu="brawler")

# On lance la procédure de connexion (SSO automatique si token.json existe, sinon écran de saisie)
token_joueur, pseudo_joueur = run_login(screen)

print(f"[Brawler] Connecté avec succès en tant que : {pseudo_joueur}")
debut_temps = time.time()

# ── CHARGEMENT DES ASSETS ──────────────────────────────────
pygame.mixer.music.load(get_asset_path("asset/audio/music.ogg"))
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1, 0.0, 5000)
sword_fx = pygame.mixer.Sound(get_asset_path("asset/audio/sword.ogg"))
sword_fx.set_volume(0.5)
magic_fx = pygame.mixer.Sound(get_asset_path("asset/audio/magic.ogg"))
magic_fx.set_volume(0.75)

bg_image = pygame.image.load(get_asset_path("asset/images/background/background.png")).convert_alpha()
fighter_1_sheet = pygame.image.load(get_asset_path("asset/warrior/warrior.png")).convert_alpha()

# Protection contre les variations d'écriture du dossier wisard/wizard
try:
    fighter_2_sheet = pygame.image.load(get_asset_path("asset/wizard/wizard.png")).convert_alpha()
except FileNotFoundError:
    fighter_2_sheet = pygame.image.load(get_asset_path("asset/wisard/wizard.png")).convert_alpha()

victory_img = pygame.image.load(get_asset_path("asset/icone/victory.png")).convert_alpha()

WARRIOR_SIZE = 162
WARRIOR_SCALE = 4
WARRIOR_OFFSET = [72, 56]
WARRIOR_DATA = [WARRIOR_SIZE, WARRIOR_SCALE, WARRIOR_OFFSET]
WIZARD_SIZE = 250
WIZARD_SCALE = 3
WIZARD_OFFSET = [112, 107]
WIZARD_DATA = [WIZARD_SIZE, WIZARD_SCALE, WIZARD_OFFSET]
WARRIOR_ANIMATION_STEPS = [10, 8, 1, 7, 7, 3, 7]
WIZARD_ANIMATION_STEPS = [8, 8, 1, 8, 8, 3, 7]

try:
    count_font = pygame.font.Font(get_asset_path("asset/fonts/turok.ttf"), 80)
    score_font = pygame.font.Font(get_asset_path("asset/fonts/turok.ttf"), 30)
except FileNotFoundError:
    count_font = pygame.font.Font(get_asset_path("asset/fonds/turok.ttf"), 80)
    score_font = pygame.font.Font(get_asset_path("asset/fonds/turok.ttf"), 30)

menu_font = pygame.font.SysFont("monospace", 48, bold=True)
small_font = pygame.font.SysFont("monospace", 28)

def draw_text(text, font, color, x, y):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

def draw_bg():
    scaled_bg = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(scaled_bg, (0, 0))

def draw_health_bar(health, x, y):
    ratio = health / 100
    pygame.draw.rect(screen, WHITE, (x-2, y-2, 404, 34))
    pygame.draw.rect(screen, RED, (x, y, 400, 30))
    pygame.draw.rect(screen, YELLOW, (x, y, int(400 * ratio), 30))

# ── ÉCRAN DE SÉLECTION MODE ────────────────────────────────
def ecran_mode():
    """Retourne True si 1 joueur (NPC), False si 2 joueurs."""
    choix = None
    while choix is None:
        draw_bg()
        draw_text("BRAWLER", menu_font, YELLOW, 350, 80)
        draw_text("1  JOUEUR  vs  NPC", small_font, WHITE, 280, 250)
        draw_text("2  JOUEURS  locaux", small_font, WHITE, 280, 320)
        draw_text("Appuie sur 1 ou 2", small_font, (180, 180, 180), 300, 420)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_1:
                    choix = True   # 1 joueur
                if event.key == pygame.K_2:
                    choix = False  # 2 joueurs
    return choix

mode_npc = ecran_mode()

# ── JEU ───────────────────────────────────────────────────
intro_count = 3
last_count_update = pygame.time.get_ticks()
score = [0, 0]
round_over = False
ROUND_OVER_COOLDOWN = 2000

def creer_fighters():
    f1 = Fighter(1, 200, 370, False, WARRIOR_DATA, fighter_1_sheet, WARRIOR_ANIMATION_STEPS, sword_fx)
    f2 = Fighter(2, 700, 370, True, WIZARD_DATA, fighter_2_sheet, WIZARD_ANIMATION_STEPS, magic_fx)
    return f1, f2

fighter_1, fighter_2 = creer_fighters()

run = True
while run:
    clock.tick(FPS)
    draw_bg()
    draw_health_bar(fighter_1.health, 20, 20)
    draw_health_bar(fighter_2.health, 580, 20)
    draw_text(f"{pseudo_joueur}: " + str(score[0]), score_font, RED, 20, 60)
    label_p2 = "NPC: " + str(score[1]) if mode_npc else "P2: " + str(score[1])
    draw_text(label_p2, score_font, RED, 580, 60)

    if intro_count <= 0:
        fighter_1.move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, fighter_2, round_over)
        if mode_npc:
            fighter_2.move_npc(SCREEN_WIDTH, SCREEN_HEIGHT, screen, fighter_1, round_over)
        else:
            fighter_2.move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, fighter_1, round_over)
    else:
        draw_text(str(intro_count), count_font, RED, SCREEN_WIDTH//2, SCREEN_HEIGHT//3)
        if pygame.time.get_ticks() - last_count_update >= 1000:
            intro_count -= 1
            last_count_update = pygame.time.get_ticks()

    fighter_1.update()
    fighter_2.update()
    fighter_1.draw(screen)
    fighter_2.draw(screen)

    if not round_over:
        if not fighter_1.alive:
            score[1] += 1
            round_over = True
            round_over_time = pygame.time.get_ticks()
        elif not fighter_2.alive:
            score[0] += 1
            round_over = True
            round_over_time = pygame.time.get_ticks()
    else:
        screen.blit(victory_img, (300, 150))
        if pygame.time.get_ticks() - round_over_time > ROUND_OVER_COOLDOWN:
            round_over = False
            intro_count = 3
            fighter_1, fighter_2 = creer_fighters()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                run = False

    pygame.display.update()

# ── ENVOI SCORE API ────────────────────────────────────────
try:
    temps_jeu = int(time.time() - debut_temps)
    # Calcule un score basé sur tes rounds gagnés
    score_final = score[0] * 100
    completion = 100 if score[0] > score[1] else 50
    api.envoyer_score(score_final, completion, temps_jeu)
    print(f"[Brawler API] Score envoyé avec succès : {score_final} pts")
except Exception as e:
    print(f"[Brawler API] Impossible d'envoyer le score : {e}")

pygame.quit()
sys.exit()
