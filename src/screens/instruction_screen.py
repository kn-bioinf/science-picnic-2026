import pygame
import src.config as config


# Instrukcja gry - jak grać w poszczególne etapy. Treść przeniesiona z etapów,
# żeby same etapy były czystsze (bez napisów-instrukcji na ekranie gry).
_SECTIONS = [
    ("Etap 1 - Składanie",
     "Przeciągnij domeny z lewego panelu na mikrotubulę i buduj od dołu: "
     "głowa motoryczna → trzon → ogon. Złóż heterokinezynę-2 jak na wzorze po "
     "prawej, a potem kliknij „Zatwierdź”. Im mniej pomyłek, tym wyższy wynik."),
    ("Etap 2 - Dokowanie",
     "Ładunek przesuwa się tam i z powrotem nad kinezyną. Kliknij myszą (albo "
     "naciśnij SPACJĘ), aby zrzucić go dokładnie na ogon kinezyny. Każde "
     "trafienie to punkt - a tempo rośnie."),
    ("Etap 3 - Transport",
     "Kinezyna biegnie po mikrotubuli. Skacz (↑, SPACJA lub klik), aby ominąć "
     "przeszkody: białka MAP, dyneinę i luki w torze. Strzałka w dół to szybki "
     "opad. Liczy się przebyty dystans."),
]


class InstructionScreen:
    """Ekran instrukcji: jak grać w każdy z trzech etapów."""

    def __init__(self, screen, state, manager):
        self.screen = screen
        self.state = state
        self.manager = manager
        self._btn = pygame.Rect(0, 0, 180, 46)

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

    def draw(self):
        w, h = config.get_size()
        self.screen.fill(config.BG)
        cx = w // 2

        title = config.font(40, bold=True).render("Instrukcja", True, config.TEXT)
        self.screen.blit(title, title.get_rect(center=(cx, 56)))

        text_x = max(64, cx - 420)
        max_w = min(840, w - 2 * text_x)
        hfont = config.font(24, bold=True)
        bfont = config.font(19)
        y = 120
        for head, body in _SECTIONS:
            ht = hfont.render(head, True, config.ACCENT)
            self.screen.blit(ht, (text_x, y)); y += 34
            for ln in self._wrapped(body, bfont, max_w):
                self.screen.blit(bfont.render(ln, True, config.TEXT), (text_x, y))
                y += 26
            y += 18

        self._btn.center = (cx, h - 52)
        pygame.draw.rect(self.screen, config.ACCENT, self._btn, border_radius=8)
        b = config.font(20).render("← Powrót", True, config.WHITE)
        self.screen.blit(b, b.get_rect(center=self._btn.center))
