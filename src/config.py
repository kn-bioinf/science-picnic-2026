import pygame

"""
Ustawia proste zmienne w tym wielkość okna czy tytuł. Nic wielkiego.
"""

W, H  = 1280, 720
FPS   = 60
TITLE = "Science Picnic 2026"

# Kolory – jasna paleta (czytelna w świetle dziennym)
BG     = (242, 246, 255)
TEXT   = ( 15,  25,  55)
ACCENT = ( 70, 130, 200)
MUTED  = (150, 160, 180)
WHITE  = (255, 255, 255)


def font(size, bold=False):
    return pygame.font.SysFont(
        "dejavusans,liberationsans,freesans,arial", size, bold=bold
    )


def get_size():
    """Zwraca aktualny rozmiar okna jako (w, h).
    """
    surf = pygame.display.get_surface()
    if surf:
        return surf.get_size()
    return W, H


def get_w():
    return get_size()[0]


def get_h():
    return get_size()[1]
