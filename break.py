import sys
import pygame
import random  # pour couleur de brique aléatoir, à venir

import os

# Dans votre bloc try/except :



# 1. Initialisation
pygame.init()
pygame.font.init()
police_pause = pygame.font.SysFont("Arial", 64, bold=True)
police_stats = pygame.font.SysFont("Arial", 24, bold=False)

# Initialisation du son avec sécurité anti-plantage
# 1. Pré-configuration et Initialisation
pygame.mixer.pre_init(44100, -16, 2, 512) # Force des paramètres audio standards et légers
pygame.init()
pygame.font.init()

police_pause = pygame.font.SysFont("Arial", 64, bold=True)
police_stats = pygame.font.SysFont("Arial", 24, bold=False)

# Chargement du son sécurisé
son_rebond = None
try:
    # On initialise le mixeur explicitement
    pygame.mixer.init()
    chemin_dossier = os.path.dirname(os.path.abspath(__file__))
    chemin_son = os.path.join(chemin_dossier, "boing.ogg")
    son_rebond = pygame.mixer.Sound(chemin_son)
    son_rebond = pygame.mixer.Sound("boing.ogg")
    son_rebond.set_volume(0.5)
except Exception as e:
    # Si le pilote audio ou le fichier bloque, on passe outre sans figer le programme
    print(f"Note : Mode audio indisponible ({e}). Le jeu se lance en mode silencieux.")

LARGEUR, HAUTEUR = 800, 600
ROWS = 5
COLUMNS = 8
score = 0
MAX_SCORE = ROWS * COLUMNS * 10
MAX_BRICKS = ROWS * COLUMNS
removed_bricks = 0
player = "player 1"
vies = 3
statut_jeu = "JOUER"

ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.set_caption("Casse-briques")

# Raquette
raquette_w, raquette_h = 100, 15
raquette_x = (LARGEUR - raquette_w) // 2
raquette_y = HAUTEUR - 40

# Balle
balle_x, balle_y = LARGEUR // 2, HAUTEUR // 2
balle_dx, balle_dy = 2, -2
balle_rayon = 10

# Définition initiale des rectangles (indispensable pour le premier rendu graphique)
rect_raquette = pygame.Rect(raquette_x, raquette_y, raquette_w, raquette_h)
rect_balle = pygame.Rect(balle_x - balle_rayon, balle_y - balle_rayon, balle_rayon * 2, balle_rayon * 2)

# Briques
briques = []
for i in range(ROWS):
    for j in range(COLUMNS):
        briques.append(pygame.Rect(j * 95 + 35, i * 35 + 50, 85, 25))

horloge = pygame.time.Clock()
en_cours = True

while en_cours:
    horloge.tick(60)

    # Gestion des événements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            en_cours = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if statut_jeu == "JOUER":
                    statut_jeu = "PAUSE"
                elif statut_jeu == "PAUSE":
                    statut_jeu = "JOUER"

    # --- PHYSIQUE ---
    if statut_jeu == "JOUER":
        touches = pygame.key.get_pressed()
        if touches[pygame.K_LEFT] and raquette_x > 0:
            raquette_x -= 6
        if touches[pygame.K_RIGHT] and raquette_x < LARGEUR - raquette_w:
            raquette_x += 6

        balle_x += balle_dx
        balle_y += balle_dy

        # Murs et plafond
        if balle_x - balle_rayon <= 0:
            balle_x = balle_rayon
            balle_dx *= -1
        elif balle_x + balle_rayon >= LARGEUR:
            balle_x = LARGEUR - balle_rayon
            balle_dx *= -1

        if balle_y - balle_rayon <= 0:
            balle_y = balle_rayon
            balle_dy *= -1

        # Mise à jour des rectangles pour les collisions
        rect_raquette = pygame.Rect(raquette_x, raquette_y, raquette_w, raquette_h)
        rect_balle = pygame.Rect(balle_x - balle_rayon, balle_y - balle_rayon, balle_rayon * 2, balle_rayon * 2)

        # Collision Raquette
        if rect_balle.colliderect(rect_raquette):
            balle_y = raquette_y - balle_rayon
            balle_dy = -abs(balle_dy)           

            centre_raquette = raquette_x + (raquette_w / 2)
            facteur_impact = (balle_x - centre_raquette) / (raquette_w / 2)
            balle_dx = facteur_impact * 5

        # Collision Briques
        for brique in briques[:]:
            if rect_balle.colliderect(brique):
                # Ne joue le son que si le fichier a bien été chargé
                if son_rebond:
                    son_rebond.play()
                briques.remove(brique)
                balle_dy *= -1
                score += 10
                removed_bricks += 1
                if removed_bricks == MAX_BRICKS:
                    statut_jeu = "VICTOIRE"
                break

        # Perte de balle
        if balle_y - balle_rayon > HAUTEUR:
            vies -= 1
            if vies <= 0:
                statut_jeu = "GAME_OVER"
            else:
                balle_x, balle_y = LARGEUR // 2, HAUTEUR // 2
                balle_dx, balle_dy = 2, -2

    # --- DESSIN ---
    ecran.fill((20, 20, 20))

    # Affichage ATH (Score et Vies)
    score_surface = police_stats.render(f"Score: {score}", True, (255, 255, 255))
    vies_surface = police_stats.render(f"Vies: {vies}", True, (255, 255, 255))
    ecran.blit(score_surface, (15, 15))
    ecran.blit(vies_surface, (LARGEUR - vies_surface.get_width() - 15, 15))

    # Dessin des éléments
    pygame.draw.rect(ecran, (255, 255, 255), rect_raquette)
    pygame.draw.circle(ecran, (255, 0, 0), (int(balle_x), int(balle_y)), balle_rayon)

    for brique in briques:
        pygame.draw.rect(ecran, (0, 128, 255), brique)

    # Écrans superposés
    if statut_jeu == "PAUSE":
        texte_surface = police_pause.render("PAUSE", True, (255, 255, 0))
        texte_rect = texte_surface.get_rect(center=(LARGEUR // 2, HAUTEUR // 2))
        ecran.blit(texte_surface, texte_rect)

    elif statut_jeu == "VICTOIRE":
        texte_surface = police_pause.render(f"BRAVO {player} !", True, (0, 255, 0))
        texte_rect = texte_surface.get_rect(center=(LARGEUR // 2, HAUTEUR // 2))
        ecran.blit(texte_surface, texte_rect)

    elif statut_jeu == "GAME_OVER":
        texte_surface = police_pause.render("GAME OVER", True, (255, 0, 0))
        texte_rect = texte_surface.get_rect(center=(LARGEUR // 2, HAUTEUR // 2))
        ecran.blit(texte_surface, texte_rect)

    pygame.display.flip()

pygame.quit()
sys.exit()
