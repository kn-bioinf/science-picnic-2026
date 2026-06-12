"""
Reużywalne efekty wizualne dla etapów gry.

Zawiera:
  * CellBackground – animowane tło „wnętrza komórki": gradient + miękkie
    organelle, dryfujące cząsteczki oraz oddalone mikrotubule z sunącymi po
    nich kinezynami (które niosą różne ładunki). Vibe fabryki.
  * draw_walking_motor – animacja „kroczenia" kinezyny: rozcina grafikę
    motora na lewą/prawą główkę i buja je naprzemiennie (hand-over-hand).
"""

import math
import random
import pygame


class CellBackground:
    """Animowane tło wnętrza komórki z oddalonymi mikrotubulami i kinezynami.

    Użycie:
        bg = CellBackground(W, H, x0, x1)   # x0..x1 – widoczny pas torów
        bg.draw(surface, t)                 # t – czas w sekundach (rośnie)
    """

    # tory: (ułamek wysokości, prędkość px/s, liczba kinezyn, kierunek +1/-1)
    LANES = [(0.16, 15, 2, +1), (0.32, 23, 3, -1), (0.49, 18, 2, +1)]
    MARGIN = 80          # px – tory wystają poza widoczny pas, by ukryć zawijanie

    BEAD_L = (206, 224, 210)
    BEAD_D = (182, 208, 190)
    KIN_HEADS = [(168, 188, 210), (152, 196, 168)]   # niebieska / zielona główka
    KIN_D  = (146, 170, 200)
    # ładunki: pęcherzyk, mitochondrium, drugi pęcherzyk
    CARGOS = [(190, 180, 210), (200, 170, 150), (170, 202, 190)]
    TOP, BOT = (236, 244, 252), (210, 226, 238)

    def __init__(self, width, height, x0=None, x1=None):
        self.w, self.h = width, height
        self.x0 = 16 if x0 is None else x0
        self.x1 = (width - 16) if x1 is None else x1
        self._grad = self._make_gradient()
        # dryfujące cząsteczki/pęcherzyki – „życie" cytoplazmy
        rnd = random.Random(20260612)
        self._floaters = [
            (rnd.uniform(0, width), rnd.uniform(0, height),
             rnd.uniform(6, 20) * rnd.choice((-1, 1)), rnd.uniform(0, 6.28),
             rnd.randint(2, 4),
             rnd.choice([(214, 224, 234), (206, 220, 212), (222, 214, 228)]))
            for _ in range(18)
        ]

    def _make_gradient(self):
        s = pygame.Surface((self.w, self.h))
        for y in range(self.h):
            f = y / self.h
            s.fill(tuple(int(self.TOP[i] + (self.BOT[i] - self.TOP[i]) * f)
                         for i in range(3)),
                   pygame.Rect(0, y, self.w, 1))
        for fx, fy, r, col in [(0.34, 0.35, 190, (224, 236, 230)),
                               (0.59, 0.65, 240, (220, 232, 242)),
                               (0.50, 0.17, 150, (230, 238, 232))]:
            blob = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(blob, (*col, 90), (r, r), r)
            s.blit(blob, (int(self.w * fx) - r, int(self.h * fy) - r))
        return s

    def draw(self, surface, t):
        surface.blit(self._grad, (0, 0))
        self._draw_floaters(surface, t)
        a, b = self.x0 - self.MARGIN, self.x1 + self.MARGIN
        period = b - a
        if period <= 0:
            return
        for li, (fy, speed, n, d) in enumerate(self.LANES):
            ly = int(self.h * fy)
            self._draw_mt(surface, a, b, ly)
            for k in range(n):
                base = (t * speed + (k / n) * period + li * 53) % period
                x = (a + base) if d > 0 else (b - base)
                self._draw_kinesin(surface, int(x), ly, k * 3 + li, t)

    def _draw_floaters(self, surface, t):
        for bx, by, sp, ph, r, col in self._floaters:
            x = (bx + sp * t) % self.w
            y = by + math.sin(t * 0.5 + ph) * 8
            pygame.draw.circle(surface, col, (int(x), int(y)), r)

    def _draw_mt(self, surface, x0, x1, ly):
        r, step = 7, 11
        for row, ry in enumerate((ly, ly + step - 2)):
            x = x0 + r + (row * (step // 2))
            i = 0
            while x < x1 - r:
                col = self.BEAD_L if (i + row) % 2 == 0 else self.BEAD_D
                pygame.draw.circle(surface, col, (int(x), ry), r)
                x += step
                i += 1

    def _draw_kinesin(self, surface, x, ly, seed, t):
        bob = math.sin(t * 6 + seed) * 1.6
        head_dy = math.sin(t * 8 + seed) * 2.0
        base = ly - 1
        cy = int(base - 24 + bob)
        # trzon
        pygame.draw.line(surface, self.KIN_D, (x, base - 3), (x, base - 18), 2)
        # ładunek – różny w zależności od kinezyny
        cargo = self.CARGOS[seed % len(self.CARGOS)]
        if seed % len(self.CARGOS) == 1:               # mitochondrium (owal)
            pygame.draw.ellipse(surface, cargo, pygame.Rect(x - 8, cy - 4, 16, 9))
            pygame.draw.ellipse(surface, self.KIN_D, pygame.Rect(x - 8, cy - 4, 16, 9), 1)
        else:                                          # pęcherzyk (kółko)
            pygame.draw.circle(surface, cargo, (x, cy), 6)
        # dwie główki na torze, naprzemiennie
        head = self.KIN_HEADS[seed % len(self.KIN_HEADS)]
        pygame.draw.circle(surface, head, (x - 4, int(base + head_dy)), 4)
        pygame.draw.circle(surface, head, (x + 4, int(base - head_dy)), 4)


def draw_walking_motor(surface, build_img, rect, cut_x, t, amp=3.0, speed=4.5):
    """Rysuje motor jako dwie główki bujane naprzemiennie (hand-over-hand).

    build_img – grafika motora (już przeskalowana),
    rect      – docelowa pozycja (jak przy zwykłym blicie),
    cut_x     – x cięcia w pikselach grafiki (zwykle punkt doczepienia trzonu;
                szew chowa się wtedy pod trzonem).
    """
    w, h = build_img.get_size()
    cut = max(1, min(w - 1, int(round(cut_x))))
    left  = build_img.subsurface(pygame.Rect(0, 0, cut, h))
    right = build_img.subsurface(pygame.Rect(cut, 0, w - cut, h))
    dl = math.sin(t * speed) * amp
    surface.blit(left,  (rect.x, int(rect.y + dl)))
    surface.blit(right, (rect.x + cut, int(rect.y - dl)))
