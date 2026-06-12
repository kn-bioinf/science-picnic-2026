"""
Reużywalne efekty wizualne dla etapów gry.

Zawiera:
  * CellBackground – animowane tło „wnętrza komórki": gradient + miękkie
    organelle, dryfujące cząsteczki oraz oddalone mikrotubule z sunącymi po
    nich kinezynami (które niosą różne ładunki). Vibe fabryki.
  * draw_walking_motor – animacja „kroczenia" kinezyny: rozcina grafikę
    motora na lewą/prawą główkę i buja je naprzemiennie (hand-over-hand).
"""

import os
import json
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
        # buduj na powierzchni z jawną alfą, potem .convert() do formatu ekranu
        # (inaczej przy rysowaniu wprost na ekran bywają czarne artefakty)
        s = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        for y in range(self.h):
            f = y / self.h
            col = tuple(int(self.TOP[i] + (self.BOT[i] - self.TOP[i]) * f)
                        for i in range(3))
            s.fill((*col, 255), pygame.Rect(0, y, self.w, 1))
        for fx, fy, r, col in [(0.34, 0.35, 190, (224, 236, 230)),
                               (0.59, 0.65, 240, (220, 232, 242)),
                               (0.50, 0.17, 150, (230, 238, 232))]:
            blob = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(blob, (*col, 90), (r, r), r)
            s.blit(blob, (int(self.w * fx) - r, int(self.h * fy) - r))
        return s.convert()

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


def _band_centroid_x(img, top):
    """Środek (x) nieprzezroczystych pikseli przy górnej/dolnej krawędzi obrazka."""
    w, h = img.get_size()
    band = max(1, int(h * 0.12))
    try:
        alpha = pygame.surfarray.array_alpha(img)         # [x][y]
    except Exception:
        return w / 2
    sl = alpha[:, 0:band] if top else alpha[:, h - band:h]
    cols = (sl > 40).any(axis=1)
    xs = [x for x in range(w) if cols[x]]
    return sum(xs) / len(xs) if xs else w / 2


_ANCHOR_OVERRIDES = None


def _anchor_overrides():
    """Ręcznie dostrojone anchory części (anchors.json, px natywne) – te same,
    których używa etap 1, więc figury składają się 1:1 jak w grze."""
    global _ANCHOR_OVERRIDES
    if _ANCHOR_OVERRIDES is None:
        path = os.path.join(os.path.dirname(__file__), '..', 'assets',
                            'images', 'puzzle-pieces', 'anchors.json')
        try:
            with open(path, encoding='utf-8') as fh:
                _ANCHOR_OVERRIDES = json.load(fh)
        except (OSError, ValueError):
            _ANCHOR_OVERRIDES = {}
    return _ANCHOR_OVERRIDES


def assemble_protein(part_paths):
    """Składa białko motoryczne z części (kolejność OD DOŁU do GÓRY: motor,
    [trzon], ogon) w jeden Surface. Punkty łączenia ('top'/'bottom', px natywne)
    bierze z anchors.json – dokładnie tak jak etap 1 – a gdy ich brak, używa
    centroidu nieprzezroczystych pikseli. Dzięki temu figury na ekranie wiedzy
    składają się tak samo dobrze jak w rozgrywce.
    """
    overrides = _anchor_overrides()
    placed, conn = [], (0.0, 0.0)
    for p in part_paths:
        img = pygame.image.load(p).convert_alpha()
        h = img.get_height()
        ov = overrides.get(os.path.basename(p))
        if ov and 'top' in ov and 'bottom' in ov:
            top, bottom = tuple(ov['top']), tuple(ov['bottom'])
        else:
            top = (_band_centroid_x(img, top=True), 0.0)
            bottom = (_band_centroid_x(img, top=False), float(h - 1))
        tl = (conn[0] - bottom[0], conn[1] - bottom[1])
        placed.append((img, tl))
        conn = (tl[0] + top[0], tl[1] + top[1])
    minx = min(tl[0] for _, tl in placed)
    miny = min(tl[1] for _, tl in placed)
    maxx = max(tl[0] + im.get_width() for im, tl in placed)
    maxy = max(tl[1] + im.get_height() for im, tl in placed)
    surf = pygame.Surface((max(1, int(maxx - minx)), max(1, int(maxy - miny))),
                          pygame.SRCALPHA)
    for im, tl in placed:
        surf.blit(im, (int(tl[0] - minx), int(tl[1] - miny)))
    return surf


def draw_cargo(surface, cargo_type, color, cx, cy, scale=1.0):
    """Rysuje ładunek (cargo) danego typu wyśrodkowany w (cx, cy).

    Współdzielone przez etap 2 (dokowanie) i etap 3 (transport), żeby ten sam
    ładunek wyglądał identycznie w obu miejscach. `scale` zmniejsza/powiększa
    rysunek (etap 3 wozi go mniejszy na ogonie kinezyny). Bez podpisu tekstowego.
    """
    def s(v):
        return max(1, int(v * scale))

    if cargo_type == "Mitochondrium":
        pygame.draw.ellipse(surface, color, (cx - s(24), cy - s(16), s(48), s(32)))
        for off in (-12, -6, 0, 6, 12):
            pygame.draw.line(surface, (160, 90, 50),
                             (cx + s(off), cy - s(10)), (cx + s(off), cy + s(10)), s(3))
    elif cargo_type == "Lizosom":
        pygame.draw.circle(surface, color, (cx, cy), s(20))
        for angle in range(0, 360, 45):
            dx = int(s(12) * math.cos(math.radians(angle)))
            dy = int(s(12) * math.sin(math.radians(angle)))
            pygame.draw.circle(surface, (220, 170, 235), (cx + dx, cy + dy), s(6))
    else:  # "Pęcherzyk" (domyślny)
        pygame.draw.circle(surface, color, (cx, cy), s(20))
        pygame.draw.circle(surface, (255, 255, 255), (cx - s(6), cy - s(6)), s(6))
        pygame.draw.circle(surface, (255, 255, 255), (cx + s(8), cy - s(8)), s(4))


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


def draw_walking_complete(surface, img, topleft, t,
                          head_frac=0.86, split_frac=0.565,
                          amp=3.0, speed=4.5):
    """Animuje GOTOWĄ kinezynę z jednego obrazka (np. heteroKinesin2Complete.png).

    Obie główki motoryczne są na DOLE obrazka, więc górna część postaci jest
    statyczna, a dolny pasek (rozcięty na lewą/prawą główkę) buja się
    naprzemiennie – efekt kroczenia. Domyślne `head_frac`/`split_frac` dobrane
    pod heteroKinesin2Complete.png (główki w dolnych ~14%, środek motora ~0.565
    szerokości).

    img      – gotowy obrazek kinezyny (już przeskalowany),
    topleft  – pozycja lewego-górnego rogu,
    head_frac – od jakiej części wysokości (od góry) zaczynają się główki,
    split_frac – x rozdzielenia obu główek (ułamek szerokości).
    """
    w, h = img.get_size()
    head_top = max(1, min(h - 1, int(h * head_frac)))
    split_x  = max(1, min(w - 1, int(w * split_frac)))
    ox, oy = int(topleft[0]), int(topleft[1])
    hh = h - head_top
    # górna (statyczna) część postaci
    surface.blit(img.subsurface(pygame.Rect(0, 0, w, head_top)), (ox, oy))
    # dwie główki na dole – tylko UNOSZONE naprzemiennie (jedna oparta, druga
    # w górze). Nigdy nie schodzą poniżej linii, więc przy szwie nie ma szpary.
    s = math.sin(t * speed)
    dl = -amp * (0.5 + 0.5 * s)     # lewa: 0 (oparta) .. -amp (uniesiona)
    dr = -amp * (0.5 - 0.5 * s)     # prawa: w przeciwfazie
    left  = img.subsurface(pygame.Rect(0, head_top, split_x, hh))
    right = img.subsurface(pygame.Rect(split_x, head_top, w - split_x, hh))
    surface.blit(left,  (ox, int(oy + head_top + dl)))
    surface.blit(right, (ox + split_x, int(oy + head_top + dr)))
