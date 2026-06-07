import pygame
import src.config as config
from src.config import FPS, TITLE
from src.game_state import GameState
from src.game_manager import GameManager

pygame.init()
info = pygame.display.Info()
init_w, init_h = info.current_w, max(200, info.current_h - 48)
screen = pygame.display.set_mode((init_w, init_h), pygame.RESIZABLE)
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()

state   = GameState()
manager = GameManager(screen, state)

running = True
# To tylko trzyma grę przy życiu do momentu jej wyłączenia. Głównym silnikiem jest src/game_manager.py
while running:
    dt = clock.tick(FPS) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        else:
            manager.handle_event(event)
    manager.update(dt)
    manager.draw()
    pygame.display.flip()

pygame.quit()
