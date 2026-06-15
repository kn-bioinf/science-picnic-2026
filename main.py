import asyncio
import sys

import pygame
import src.config as config
from src.config import W, H, FPS, TITLE
from src.game_state import GameState
from src.game_manager import GameManager

# Wykrywamy uruchomienie w przeglądarce (pygbag/Emscripten). Na desktopie
# zachowujemy dotychczasowe zachowanie (okno RESIZABLE), w przeglądarce
# ustawiamy stały rozmiar kanwy - tam oknem zarządza pygbag, a nie OS.
IS_WEB = sys.platform in ("emscripten", "wasi")


def _make_screen():
    if IS_WEB:
        return pygame.display.set_mode((W, H))
    info = pygame.display.Info()
    init_w, init_h = info.current_w, max(200, info.current_h - 48)
    return pygame.display.set_mode((init_w, init_h), pygame.RESIZABLE)


async def main():
    pygame.init()
    screen = _make_screen()
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    state = GameState()
    manager = GameManager(screen, state)

    running = True
    # To tylko trzyma grę przy życiu do momentu jej wyłączenia. Głównym
    # silnikiem jest src/game_manager.py. await asyncio.sleep(0) na końcu
    # każdej klatki oddaje sterowanie przeglądarce (w przeglądarce wymagane,
    # na desktopie po prostu nie blokuje pętli zdarzeń).
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
        await asyncio.sleep(0)

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
