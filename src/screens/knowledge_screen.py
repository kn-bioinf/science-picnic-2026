import os
import pygame
import src.config as config
from src.effects import assemble_protein

_PIECES = os.path.join(os.path.dirname(__file__), "..", "..",
                       "assets", "images", "puzzle-pieces")


def _p(name):
    return os.path.join(_PIECES, name)


# Trzy białka motoryczne złożone z części (od dołu do góry: motor, [trzon], ogon).
# Każde: (nazwa, podpis-kierunek, lista plików części).
_FIGURES = [
    ("Kinezyna", "mikrotubula  •  do obrzeży →",
     [_p("heteroKinesin2Motor.png"), _p("heteroKinesin2Stalk.png"),
      _p("heteroKinesin2Tail.png")]),
    ("Dyneina", "mikrotubula  •  ← do środka",
     [_p("DyneinMotor.png"), _p("DyneinTail.png")]),
    ("Miozyna V", "po włóknach aktyny",
     [_p("MyosinVMotor.png"), _p("MyosinVStalk.png"), _p("MyosinVTail.png")]),
]

_PARAS = [
    ("Białka motoryczne - komórkowi tragarze",
     "Wnętrze komórki to ruchliwe miasto, w którym wciąż trzeba coś dowieźć na "
     "miejsce. Robią to białka motoryczne - maleńkie nanosilniki, które spalają "
     "paliwo (ATP, komórkową „baterię\") i krok po kroku przenoszą ładunki po "
     "wewnętrznych torach."),
    ("Tory i trzy rodziny",
     "Te tory to cienkie rurki zwane mikrotubulami oraz włókna aktyny - komórkowe "
     "„szyny\". Po mikrotubulach chodzą kinezyna i dyneina (w przeciwne strony), a "
     "po aktynie miozyna. My zajmiemy się kinezyną."),
    ("Co i dokąd niesie kinezyna",
     "Kinezyna „idzie\" na dwóch główkach-nóżkach i ciągnie ładunek: pęcherzyki "
     "(błonowe „paczki\"), mitochondria (elektrownie) czy lizosomy (śmietniki). "
     "Pracuje w prawie każdej komórce - zwykle wiezie ładunek od jej środka ku "
     "obrzeżom, tam gdzie jest właśnie potrzebny."),
    ("W tej grze",
     "Prześledzimy całą drogę kinezyny: od jej powstania (złożenie z części), "
     "przez przyłączenie ładunku, aż po transport po mikrotubuli."),
]


class KnowledgeScreen:
    """Wprowadzenie: białka motoryczne (kinezyna, dyneina, miozyna), co kinezyna
    przenosi, skąd dokąd i dlaczego to ważne."""

    def __init__(self, screen, state, manager):
        self.screen = screen
        self.state = state
        self.manager = manager
        self._btn = pygame.Rect(0, 0, 180, 46)
        # złóż figury białek raz (potem tylko skalujemy do układu)
        self._figs = []
        for name, sub, parts in _FIGURES:
            try:
                self._figs.append((name, sub, assemble_protein(parts)))
            except (pygame.error, FileNotFoundError, ValueError):
                self._figs.append((name, sub, None))

    def handle_event(self, e):
        if (e.type == pygame.MOUSEBUTTONDOWN and e.button == 1
                and self._btn.collidepoint(e.pos)):
            self.manager.transition_to(self.manager.MENU)
        elif e.type == pygame.KEYDOWN and e.key in (pygame.K_RETURN, pygame.K_ESCAPE):
            self.manager.transition_to(self.manager.MENU)

    def update(self, dt):
        pass

    def _wrapped(self, text, font, max_w):
        lines, cur = [], ""
        for word in text.split():
            trial = word if not cur else cur + " " + word
            if font.size(trial)[0] <= max_w:
                cur = trial
            else:
                lines.append(cur); cur = word
        if cur:
            lines.append(cur)
        return lines

    def _draw_figures(self, panel_x, top_y, panel_w, panel_h):
        """Trzy białka w rzędzie, każde z podpisem nazwy i kierunku."""
        n = len(self._figs)
        cell_w = panel_w // n
        fig_h = min(int(panel_h * 0.74), 300)
        for i, (name, sub, img) in enumerate(self._figs):
            ccx = panel_x + cell_w * i + cell_w // 2
            if img:
                s = min((cell_w - 24) / img.get_width(), fig_h / img.get_height())
                fig = pygame.transform.smoothscale(
                    img, (max(1, int(img.get_width() * s)),
                          max(1, int(img.get_height() * s))))
                r = fig.get_rect(midtop=(ccx, top_y))
                self.screen.blit(fig, r)
                base_y = r.bottom + 8
            else:
                base_y = top_y + fig_h
            nm = config.font(19, bold=True).render(name, True, config.ACCENT)
            self.screen.blit(nm, nm.get_rect(midtop=(ccx, base_y)))
            sb = config.font(13).render(sub, True, config.MUTED)
            self.screen.blit(sb, sb.get_rect(midtop=(ccx, base_y + 26)))

    def draw(self):
        w, h = config.get_size()
        self.screen.fill(config.BG)

        title = config.font(40, bold=True).render("Wiedza na start", True, config.TEXT)
        self.screen.blit(title, title.get_rect(center=(w // 2, 52)))

        # prawy panel: trzy białka motoryczne w rzędzie
        panel_x = int(w * 0.55)
        panel_w = w - panel_x - 56
        self._draw_figures(panel_x, 120, panel_w, int(h * 0.62))

        # lewy panel: tekst (zawijany do szerokości lewej kolumny)
        text_x = 64
        max_w = panel_x - text_x - 40
        hfont = config.font(23, bold=True)
        bfont = config.font(18)
        y = 98
        for head, body in _PARAS:
            ht = hfont.render(head, True, config.ACCENT)
            self.screen.blit(ht, (text_x, y)); y += 30
            for ln in self._wrapped(body, bfont, max_w):
                self.screen.blit(bfont.render(ln, True, config.TEXT), (text_x, y))
                y += 24
            y += 10

        # powrót
        self._btn.center = (text_x + 90, h - 46)
        pygame.draw.rect(self.screen, config.ACCENT, self._btn, border_radius=8)
        b = config.font(20).render("← Powrót", True, config.WHITE)
        self.screen.blit(b, b.get_rect(center=self._btn.center))
        hint = config.font(14).render("Enter / Esc - powrót", True, config.MUTED)
        self.screen.blit(hint, hint.get_rect(midleft=(self._btn.right + 16, self._btn.centery)))
