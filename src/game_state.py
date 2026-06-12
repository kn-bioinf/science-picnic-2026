from pathlib import Path
import json


class GameState:
    """Kontener danych współdzielony przez sceny + obsługa rankingów.

    Rankingi trzymamy w jednym pliku ranking.json jako słownik kategorii:
        {"total": [...], "stage1": [...], "stage2": [...], "stage3": [...]}
    Każda kategoria to lista wpisów {"name", "score"} (malejąco, top 10).

    Konwencja wyników (porównywalna między etapami):
        etap 1 = 20 - liczba pomyłek (min 0)   - składanie kinezyny
        etap 2 = liczba udanych dokowań        - dokowanie ładunku
        etap 3 = liczba pokonanych przeszkód   - bieg na mikrotubuli
        total  = suma z pełnej rozgrywki (1->2->3)
    """

    RANKING_FILE = Path(__file__).parent.parent / "ranking.json"
    CATEGORIES = ("total", "stage1", "stage2", "stage3")
    TOP_N = 10

    def __init__(self):
        self.player_name = "Gracz"
        self.score = 0                 # suma punktów bieżącej (pełnej) rozgrywki
        self.stage_scores = {}         # {1: x, 2: y, 3: z} dla bieżącej rozgrywki
        self.last_cargo = None         # (typ, kolor) ostatniego ładunku z etapu 2

    # ---------------------------------------------------------------- run
    def reset_run(self):
        self.score = 0
        self.stage_scores = {}

    # ------------------------------------------------------------ rankingi
    @classmethod
    def load_rankings(cls):
        """Zwraca słownik kategorii. Migruje stary format (płaska lista)."""
        base = {c: [] for c in cls.CATEGORIES}
        try:
            if not cls.RANKING_FILE.exists():
                return base
            data = json.loads(cls.RANKING_FILE.read_text())
            if isinstance(data, list):          # stary format -> total
                base["total"] = data
                return base
            if isinstance(data, dict):
                for c in cls.CATEGORIES:
                    if isinstance(data.get(c), list):
                        base[c] = data[c]
            return base
        except Exception:
            return base

    @classmethod
    def get_ranking(cls, category):
        return cls.load_rankings().get(category, [])

    def save_score(self, category, score):
        """Dopisuje wynik do kategorii (malejąco, top N) i zapisuje plik."""
        if category not in self.CATEGORIES:
            return
        rankings = self.load_rankings()
        rankings[category].append({"name": self.player_name, "score": int(score)})
        rankings[category] = sorted(
            rankings[category], key=lambda x: x.get("score", 0), reverse=True
        )[: self.TOP_N]
        try:
            self.RANKING_FILE.write_text(json.dumps(rankings, indent=2,
                                                    ensure_ascii=False))
        except Exception:
            pass
        return rankings[category]
