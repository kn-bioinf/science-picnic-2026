from pathlib import Path
import json


class GameState:
    """Prosty kontener danych – dostępny we wszystkich scenach."""

    RANKING_FILE = Path(__file__).parent.parent / "ranking.json"

    def __init__(self):
        self.player_name = "Gracz"
        self.score       = 0        # suma punktów ze wszystkich etapów

    def save_ranking(self):
        """Zapisuje prosty ranking (name, score) do `ranking.json`.

        Minimalna implementacja: dopisuje wpis i trzyma top10.
        """
        try:
            data = []
            if self.RANKING_FILE.exists():
                data = json.loads(self.RANKING_FILE.read_text())
            data.append({"name": self.player_name, "score": int(self.score)})
            data = sorted(data, key=lambda x: x["score"], reverse=True)[:10]
            self.RANKING_FILE.write_text(json.dumps(data, indent=2))
            return data
        except Exception:
            return []

    @staticmethod
    def load_ranking():
        try:
            p = GameState.RANKING_FILE
            if not p.exists():
                return []
            return json.loads(p.read_text())
        except Exception:
            return []
