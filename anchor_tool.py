"""
Edytor anchorów (punktów łączenia) klocków kinezyny.

Po co: w stage1 klocki łączą się w łańcuch — DOLNY anchor elementu siada na
GÓRNYM anchorze elementu poniżej (a motor siada na mikrotubuli). Ten edytor
pozwala ustawić te punkty ręcznie i zapisuje je do
assets/images/puzzle-pieces/anchors.json, które gra wczytuje.

Uruchom:
    /home/lambi/miniconda3/envs/kinesinquest/bin/python anchor_tool.py

Sterowanie:
    LEWY  klik   – ustaw DOLNY punkt (czerwony) – styk z elementem poniżej / mikrotubulą
    PRAWY klik   – ustaw GÓRNY punkt (niebieski) – tu doczepia się następny element
    ← / →        – poprzedni / następny klocek
    +/-          – przybliż / oddal edytowany klocek
    R            – reset anchorów bieżącego klocka do centroidu krawędzi
    S            – zapisz anchors.json
    Q / ESC      – zapisz i wyjdź

Po prawej: PODGLĄD trio (Motor→Trzon→Ogon) złożonego wg bieżących anchorów,
nałożony na wyblakłą referencję heteroKinesin2Complete.png. Gdy anchory są
dobre, złożenie pokrywa się z referencją.
"""

import os
import json
import pygame

PIECES_DIR = os.path.join(os.path.dirname(__file__),
                          'assets', 'images', 'puzzle-pieces')
REF_PATH   = os.path.join(os.path.dirname(__file__),
                          'assets', 'images', 'heteroKinesin2Complete.png')
ANCHORS_PATH = os.path.join(PIECES_DIR, 'anchors.json')

CLASS_KEYS = ['Motor', 'Stalk', 'Tail']
CLASS_PL   = {'Motor': 'Glowa (motor)', 'Stalk': 'Trzon', 'Tail': 'Ogon'}
CORRECT    = 'heteroKinesin2'

# Dokładne anchory poprawnego trio (px natywne), wyliczone z referencji –
# służą jako PUNKT STARTOWY dla heteroKinesin2 (zanim cokolwiek ruszysz,
# podgląd już pokrywa się z referencją). Te same wartości ma gra.
HETERO_SEED = {
    'Motor': {'bottom': [55, 44], 'top': [47, 5]},
    'Stalk': {'bottom': [13, 168], 'top': [12, 2]},
    'Tail':  {'bottom': [69, 88], 'top': [69, 0]},
}

# Pozycja DOLNEGO anchora motora w referencji (px natywne) – do nałożenia
# podglądu na heteroKinesin2Complete.png.
REF_MOTOR_BOTTOM = (78, 293)

WIN_W, WIN_H = 1180, 700
EDIT_X, EDIT_Y, EDIT_W, EDIT_H = 20, 70, 600, 600       # obszar edycji klocka
PREV_X, PREV_Y = 660, 70                                 # róg podglądu


def species_of(filename):
    stem = filename[:-4]
    for key in CLASS_KEYS:
        if stem.endswith(key):
            return stem[:-len(key)], key
    return None, None


def centroid_anchors(surf):
    """Domyślne anchory: centroid nieprzezroczystych pikseli przy krawędziach."""
    w, h = surf.get_size()
    alpha = pygame.surfarray.array_alpha(surf)          # [x][y]
    band = max(1, int(h * 0.12))

    def cx(y0, y1):
        cols = (alpha[:, y0:y1] > 40).any(axis=1)
        xs = [x for x in range(w) if cols[x]]
        return sum(xs) / len(xs) if xs else w / 2.0

    return {'top': [round(cx(0, band), 1), 0.0],
            'bottom': [round(cx(h - band, h), 1), float(h - 1)]}


class Piece:
    def __init__(self, filename):
        self.file = filename
        self.species, self.klass = species_of(filename)
        self.img = pygame.image.load(os.path.join(PIECES_DIR, filename)).convert_alpha()
        self.w, self.h = self.img.get_size()
        self.anchors = centroid_anchors(self.img)       # może być nadpisane z json


def load_pieces():
    files = sorted(f for f in os.listdir(PIECES_DIR) if f.lower().endswith('.png'))
    pieces = [Piece(f) for f in files if species_of(f)[1]]
    # kolejność: wg klasy (Motor, Stalk, Tail), w klasie hetero pierwszy
    order = {k: i for i, k in enumerate(CLASS_KEYS)}
    pieces.sort(key=lambda p: (order[p.klass], p.species != CORRECT, p.species))
    return pieces


def load_existing(pieces):
    if not os.path.exists(ANCHORS_PATH):
        return
    try:
        data = json.load(open(ANCHORS_PATH, encoding='utf-8'))
    except (OSError, ValueError):
        return
    for p in pieces:
        if p.file in data:
            a = data[p.file]
            if 'top' in a and 'bottom' in a:
                p.anchors = {'top': list(a['top']), 'bottom': list(a['bottom'])}


def save_anchors(pieces):
    data = {p.file: {'top': [round(p.anchors['top'][0], 1), round(p.anchors['top'][1], 1)],
                     'bottom': [round(p.anchors['bottom'][0], 1), round(p.anchors['bottom'][1], 1)]}
            for p in pieces}
    json.dump(data, open(ANCHORS_PATH, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    return ANCHORS_PATH


def scaled(img, f):
    w, h = img.get_size()
    return pygame.transform.smoothscale(img, (max(1, int(w * f)), max(1, int(h * f))))


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption("Anchor tool – kinezyna")
    font   = pygame.font.SysFont("dejavusans,arial", 16)
    fontb  = pygame.font.SysFont("dejavusans,arial", 20, bold=True)
    small  = pygame.font.SysFont("dejavusans,arial", 13)

    pieces = load_pieces()
    for p in pieces:                          # start hetero od znanych dobrych wartości
        if p.species == CORRECT and p.klass in HETERO_SEED:
            p.anchors = {'top': list(HETERO_SEED[p.klass]['top']),
                         'bottom': list(HETERO_SEED[p.klass]['bottom'])}
    load_existing(pieces)                      # json (jeśli jest) ma pierwszeństwo
    by_class = {}
    for p in pieces:
        by_class.setdefault(p.klass, []).append(p)
    # domyślny "hetero" element każdej klasy do podglądu
    hetero = {}
    for k in CLASS_KEYS:
        for p in by_class.get(k, []):
            if p.species == CORRECT:
                hetero[k] = p

    try:
        ref = pygame.image.load(REF_PATH).convert_alpha()
    except pygame.error:
        ref = None

    idx = 0
    edit_f = 0.0   # 0 => auto-fit
    msg = ""
    clock = pygame.time.Clock()

    def fit_scale(p):
        return min(EDIT_W / p.w, EDIT_H / p.h)

    running = True
    while running:
        p = pieces[idx]
        f = edit_f if edit_f > 0 else fit_scale(p)
        # origin tak, by klocek był wyśrodkowany w obszarze edycji
        disp_w, disp_h = p.w * f, p.h * f
        ox = EDIT_X + (EDIT_W - disp_w) / 2
        oy = EDIT_Y + (EDIT_H - disp_h) / 2

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_q, pygame.K_ESCAPE):
                    running = False
                elif e.key == pygame.K_RIGHT:
                    idx = (idx + 1) % len(pieces); edit_f = 0.0; msg = ""
                elif e.key == pygame.K_LEFT:
                    idx = (idx - 1) % len(pieces); edit_f = 0.0; msg = ""
                elif e.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                    edit_f = (f if edit_f == 0 else edit_f) * 1.25
                elif e.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    edit_f = (f if edit_f == 0 else edit_f) / 1.25
                elif e.key == pygame.K_r:
                    p.anchors = centroid_anchors(p.img); msg = "reset do centroidu"
                elif e.key == pygame.K_s:
                    save_anchors(pieces); msg = f"zapisano {os.path.basename(ANCHORS_PATH)}"
            elif e.type == pygame.MOUSEBUTTONDOWN:
                mx, my = e.pos
                nx = (mx - ox) / f
                ny = (my - oy) / f
                if 0 <= nx <= p.w and 0 <= ny <= p.h:
                    if e.button == 1:
                        p.anchors['bottom'] = [round(nx, 1), round(ny, 1)]
                    elif e.button == 3:
                        p.anchors['top'] = [round(nx, 1), round(ny, 1)]

        # ---- rysowanie ----
        screen.fill((238, 242, 250))

        # nagłówek
        screen.blit(fontb.render(
            f"[{idx+1}/{len(pieces)}]  {p.file}   ({CLASS_PL[p.klass]})",
            True, (15, 25, 55)), (20, 18))
        screen.blit(small.render(
            "LEWY=dolny(czerw.)  PRAWY=gorny(nieb.)   <- ->  +/-  R=reset  S=zapis  Q=wyjscie",
            True, (90, 100, 120)), (20, 44))

        # obszar edycji
        pygame.draw.rect(screen, (255, 255, 255),
                         pygame.Rect(EDIT_X, EDIT_Y, EDIT_W, EDIT_H))
        pygame.draw.rect(screen, (200, 208, 224),
                         pygame.Rect(EDIT_X, EDIT_Y, EDIT_W, EDIT_H), 1)
        big = scaled(p.img, f)
        screen.blit(big, (ox, oy))

        # anchory
        for key, col in (('bottom', (220, 60, 60)), ('top', (50, 110, 220))):
            ax, ay = p.anchors[key]
            sx, sy = ox + ax * f, oy + ay * f
            pygame.draw.line(screen, col, (sx - 10, sy), (sx + 10, sy), 2)
            pygame.draw.line(screen, col, (sx, sy - 10), (sx, sy + 10), 2)
            pygame.draw.circle(screen, col, (int(sx), int(sy)), 5, 2)
            screen.blit(small.render(
                f"{key}=({ax:.1f},{ay:.1f})", True, col), (sx + 8, sy + 6))

        # ---- podgląd złożenia ----
        screen.blit(fontb.render("Podglad zlozenia", True, (15, 25, 55)),
                    (PREV_X, 40))
        pf = 1.4
        baseline = (PREV_X + 150, PREV_Y + 360)   # tu siada dolny anchor motora
        # wyblakla referencja
        if ref is not None:
            r = scaled(ref, pf).copy()
            r.set_alpha(70)
            rtl = (baseline[0] - REF_MOTOR_BOTTOM[0] * pf,
                   baseline[1] - REF_MOTOR_BOTTOM[1] * pf)
            screen.blit(r, rtl)
        # złożenie wg bieżących anchorów (motor->stalk->tail);
        # dla każdej klasy bierz aktualnie edytowany klocek, inaczej hetero
        conn = baseline
        for k in CLASS_KEYS:
            pc = p if p.klass == k else hetero.get(k)
            if pc is None:
                continue
            surf = scaled(pc.img, pf)
            bx, by = pc.anchors['bottom'][0] * pf, pc.anchors['bottom'][1] * pf
            tl = (conn[0] - bx, conn[1] - by)
            screen.blit(surf, tl)
            tx, ty = pc.anchors['top'][0] * pf, pc.anchors['top'][1] * pf
            conn = (tl[0] + tx, tl[1] + ty)
        # mikrotubula – linia bazowa
        pygame.draw.line(screen, (70, 150, 85),
                         (PREV_X, baseline[1]), (WIN_W - 20, baseline[1]), 3)

        if msg:
            screen.blit(font.render(msg, True, (40, 150, 70)), (PREV_X, WIN_H - 30))

        pygame.display.flip()
        clock.tick(60)

    path = save_anchors(pieces)
    print("Zapisano:", path)
    pygame.quit()


if __name__ == '__main__':
    main()
