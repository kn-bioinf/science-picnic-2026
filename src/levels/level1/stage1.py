import pygame
import os
import math
import src.config as config

_PIECES_DIR = os.path.join(
    os.path.dirname(__file__), '..', '..', '..', 'assets', 'images', 'puzzle-pieces'
)

SCALE       = 1.5    # display scale multiplier
SNAP_RADIUS = 95     # px – drop within this radius → lerp-snap to slot
LERP_SPEED  = 9.0    # ease-out speed
GHOST_ALPHA = 40
PANEL_W     = 260    # right-side panel width
# Overlap per joint derived from complete reference image:
# (sum piece heights 307 − complete height 293) / 2 joints = 7 px at 1× → 11 px at 1.5×
OVERLAP     = int(7 * SCALE + 0.5)

_PIECE_DEFS = [
    ('tail',  'heteroKinesin2Tail.png',  'Ogon'),
    ('stalk', 'heteroKinesin2Stalk.png', 'Trzon'),
    ('motor', 'heteroKinesin2Motor.png', 'Głowy'),
]


# ------------------------------------------------------------------ helpers

def _load_img(filename):
    path = os.path.join(_PIECES_DIR, filename)
    img  = pygame.image.load(path).convert_alpha()
    w, h = img.get_size()
    return pygame.transform.smoothscale(img, (int(w * SCALE), int(h * SCALE)))



def _arrange_panel(images, cx, y_top, y_bottom):
    """Return (cx, cy) for each image, evenly spaced in [y_top, y_bottom]."""
    total_h = sum(i.get_height() for i in images)
    slack   = y_bottom - y_top - total_h
    gap     = slack / (len(images) + 1)
    y = y_top + gap
    out = []
    for img in images:
        out.append((cx, int(y + img.get_height() / 2)))
        y += img.get_height() + gap
    return out


# ------------------------------------------------------------------ piece

class _Piece:
    def __init__(self, name, label, image, slot, home):
        self.name   = name
        self.label  = label
        self.image  = image
        w, h = image.get_size()
        self.rect   = pygame.Rect(0, 0, w, h)
        self.rect.center = home
        self.slot   = slot    # (cx, cy) target in assembly area
        self.home   = home    # (cx, cy) resting place in panel
        # state: 'panel' | 'dragging' | 'snapping' | 'snapped'
        self.state      = 'panel'
        self.lerp_from  = home
        self.lerp_t     = 0.0
        self.drop_score = 0.0   # quality 0-1, set when snapped

    def set_center(self, cx, cy):
        self.rect.centerx = int(cx)
        self.rect.centery = int(cy)

    def lerp_center(self):
        fx, fy = self.lerp_from
        tx, ty = self.slot
        t = min(1.0, self.lerp_t)
        e = 1.0 - (1.0 - t) ** 2   # ease-out quadratic
        return fx + (tx - fx) * e, fy + (ty - fy) * e


# ------------------------------------------------------------------ stage

class Stage1:
    """
    Etap 1 – składanie kinezyny z 3 elementów: Ogon / Trzon / Głowy.
    Drag-and-drop z lerp-snapem. Score 0-100 odzwierciedla jakość złożenia.
    """

    def __init__(self, screen, state, next_fn):
        self.screen = screen
        self.state  = state
        self.next   = next_fn

        self._drag     = None
        self._drag_off = (0, 0)
        self._done     = False
        self._btn      = pygame.Rect(0, 0, 160, 44)

        self._pieces = self._build_pieces()
        self._ghosts = {p.name: self._make_ghost(p.image) for p in self._pieces}

    # -------------------------------------------------------------- setup

    @staticmethod
    def _make_ghost(img):
        g = img.copy()
        g.set_alpha(GHOST_ALPHA)
        return g

    def _build_pieces(self):
        w, h = config.get_size()

        images = [_load_img(f) for _, f, _ in _PIECE_DEFS]
        th, sh, mh = (img.get_height() for img in images)

        # Stack pieces with OVERLAP px of image-rect overlap per joint,
        # matching the complete reference image (7 px at 1× → 11 px at 1.5×)
        y_tail  = 0
        y_stalk = th - OVERLAP
        y_motor = y_stalk + sh - OVERLAP

        total_h  = y_motor + mh
        y_offset = h // 2 - total_h // 2

        asm_cx = (w - PANEL_W) // 2

        slots = [
            (asm_cx, y_tail  + y_offset + th // 2),
            (asm_cx, y_stalk + y_offset + sh // 2),
            (asm_cx, y_motor + y_offset + mh // 2),
        ]

        panel_cx = w - PANEL_W // 2
        homes = _arrange_panel(images, panel_cx, 50, h - 50)

        return [
            _Piece(name, label, images[i], slots[i], homes[i])
            for i, (name, _, label) in enumerate(_PIECE_DEFS)
        ]

    # -------------------------------------------------------------- events

    def handle_event(self, e):
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            if self._done and self._btn.collidepoint(e.pos):
                self.next(self._calc_score())
                return
            # Pick up any non-snapping piece (including already-snapped ones)
            for piece in reversed(self._pieces):
                if piece.state in ('panel', 'snapped') and piece.rect.collidepoint(e.pos):
                    if piece.state == 'snapped':
                        piece.drop_score = 0.0
                        self._done = False
                    piece.state    = 'dragging'
                    self._drag     = piece
                    self._drag_off = (e.pos[0] - piece.rect.x,
                                      e.pos[1] - piece.rect.y)
                    break

        elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
            if self._drag:
                p    = self._drag
                self._drag = None
                dist = math.hypot(p.rect.centerx - p.slot[0],
                                  p.rect.centery - p.slot[1])
                if dist < SNAP_RADIUS:
                    p.lerp_from  = (p.rect.centerx, p.rect.centery)
                    p.lerp_t     = 0.0
                    p.drop_score = max(0.0, 1.0 - dist / SNAP_RADIUS)
                    p.state      = 'snapping'
                else:
                    p.state = 'panel'   # stays where dropped

        elif e.type == pygame.MOUSEMOTION and self._drag:
            p = self._drag
            p.rect.x = e.pos[0] - self._drag_off[0]
            p.rect.y = e.pos[1] - self._drag_off[1]

    # -------------------------------------------------------------- update

    def update(self, dt):
        for p in self._pieces:
            if p.state == 'snapping':
                p.lerp_t += dt * LERP_SPEED
                cx, cy = p.lerp_center()
                p.set_center(cx, cy)
                if p.lerp_t >= 1.0:
                    p.set_center(*p.slot)
                    p.state = 'snapped'

        if not self._done and all(p.state == 'snapped' for p in self._pieces):
            self._done = True

    # -------------------------------------------------------------- draw

    def draw(self):
        w, h = config.get_size()
        self.screen.fill(config.BG)

        # Right panel
        panel_x = w - PANEL_W
        pygame.draw.rect(self.screen, (215, 225, 246),
                         pygame.Rect(panel_x, 0, PANEL_W, h))
        pygame.draw.line(self.screen, config.MUTED,
                         (panel_x, 0), (panel_x, h), 2)
        lbl = config.font(18, bold=True).render("Elementy", True, config.TEXT)
        self.screen.blit(lbl, lbl.get_rect(centerx=panel_x + PANEL_W // 2, y=12))

        # Panel: labels and faint silhouette only for pieces currently at home
        for p in self._pieces:
            at_home = (p.state == 'panel' and
                       abs(p.rect.centerx - p.home[0]) < 10 and
                       abs(p.rect.centery - p.home[1]) < 10)
            if at_home:
                txt = config.font(14).render(p.label, True, config.MUTED)
                self.screen.blit(txt, txt.get_rect(
                    centerx=p.home[0],
                    y=p.home[1] - p.image.get_height() // 2 - 18
                ))

        # Ghost slot outlines in assembly area
        for p in self._pieces:
            if p.state != 'snapped':
                g = self._ghosts[p.name]
                self.screen.blit(g, g.get_rect(center=p.slot))

        # Snap-radius ring while dragging
        if self._drag:
            sx, sy = self._drag.slot
            pygame.draw.circle(self.screen, (160, 190, 230),
                               (sx, sy), SNAP_RADIUS, 1)

        # Pieces: non-dragged first, dragged on top
        for p in self._pieces:
            if p is not self._drag:
                self.screen.blit(p.image, p.rect)
                if p.state == 'snapped':
                    pygame.draw.rect(self.screen, (55, 175, 85),
                                     p.rect.inflate(4, 4), 2, border_radius=4)
                elif p.state == 'panel' and p.rect.centerx < panel_x:
                    # Floating piece in assembly area – dashed outline to show it's moveable
                    pygame.draw.rect(self.screen, config.ACCENT,
                                     p.rect.inflate(4, 4), 1, border_radius=4)
        if self._drag:
            self.screen.blit(self._drag.image, self._drag.rect)

        # Title
        asm_cx = panel_x // 2
        title = config.font(30, bold=True).render("Składanie kinezyny", True, config.TEXT)
        self.screen.blit(title, title.get_rect(centerx=asm_cx, y=16))

        # Live score – top-left corner
        pct = self._live_score()
        self.screen.blit(config.font(14).render("Wynik", True, config.MUTED),
                         (16, 62))
        self.screen.blit(config.font(48, bold=True).render(f"{pct}%", True,
                         self._score_color(pct)), (12, 76))

        # Bottom bar
        if self._done:
            t = config.font(22, bold=True).render(
                "Kinezyna złożona!", True, (40, 150, 70))
            self.screen.blit(t, t.get_rect(centerx=asm_cx, y=h - 90))
            self._btn.center = (asm_cx, h - 48)
            pygame.draw.rect(self.screen, config.ACCENT, self._btn, border_radius=8)
            btn_txt = config.font(20).render("Dalej ->", True, config.WHITE)
            self.screen.blit(btn_txt, btn_txt.get_rect(center=self._btn.center))
        else:
            hint = config.font(15).render(
                "Przeciągnij elementy na oznaczone miejsca", True, config.MUTED)
            self.screen.blit(hint, hint.get_rect(centerx=asm_cx, y=h - 34))

    # -------------------------------------------------------------- score

    def _live_score(self):
        """0-100: snapped pieces use their quality; unplaced assume perfect."""
        total = sum(
            p.drop_score if p.state == 'snapped' else 1.0
            for p in self._pieces
        )
        return int(total / len(self._pieces) * 100)

    def _calc_score(self):
        avg = sum(p.drop_score for p in self._pieces) / len(self._pieces)
        return int(avg * 100)

    @staticmethod
    def _score_color(pct):
        if pct >= 80: return (40, 170, 70)
        if pct >= 50: return (210, 150, 20)
        return (200, 50, 50)
