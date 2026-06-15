from functools import lru_cache
from pathlib import Path
import pygame

"""
Ustawia proste zmienne w tym wielkość okna czy tytuł. Nic wielkiego.
"""

# Czcionki dołączamy do repo (assets/fonts), zamiast polegać na SysFont.
# W przeglądarce (pygbag) SysFont zwykle nie znajduje czcionek systemowych,
# a dołączony TTF działa identycznie na desktopie i w webie.
_FONT_DIR  = Path(__file__).parent.parent / "assets" / "fonts"
_FONT_REG  = _FONT_DIR / "DejaVuSans.ttf"
_FONT_BOLD = _FONT_DIR / "DejaVuSans-Bold.ttf"

W, H  = 1280, 720
FPS   = 60
TITLE = "KinesinQuest"

# Kolory - jasna paleta (czytelna w świetle dziennym)
BG     = (242, 246, 255)
TEXT   = ( 15,  25,  55)
ACCENT = ( 70, 130, 200)
MUTED  = (150, 160, 180)
WHITE  = (255, 255, 255)


@lru_cache(maxsize=64)
def font(size, bold=False):
    # cache: tworzenie obiektu Font jest kosztowne - wołane wielokrotnie co
    # klatkę (HUD + etykiety przeszkód) bez cache potrafi ścinać FPS.
    path = _FONT_BOLD if bold else _FONT_REG
    try:
        return pygame.font.Font(str(path), size)
    except Exception:
        # awaryjnie: SysFont (desktop), a w ostateczności wbudowana czcionka.
        try:
            return pygame.font.SysFont(
                "dejavusans,liberationsans,freesans,arial", size, bold=bold
            )
        except Exception:
            f = pygame.font.Font(None, size)
            f.set_bold(bold)
            return f


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
