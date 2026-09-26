import json
import os

def load_match_fixture(filename="challenger_match.json"):
    """Lê o ficheiro JSON da pasta fixtures e devolve os dados estruturados do jogo."""
    # O caminho aponta para a pasta fixtures na raiz do projeto
    fixture_path = os.path.join(os.path.dirname(__file__), "../../../fixtures", filename)
    
    try:
        with open(fixture_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data
    except Exception as e:
        print(f"[ERRO PARSER] Não foi possível carregar o fixture: {e}")
        return None