from livetennisapi import LiveTennisAPI

# Insere a chave diretamente para garantir que o teste arranca sem falhas de leitura do .env
API_KEY = "twjp_d0426f3915422fc340b35cab0bbaa7d9"

def fetch_live_tennis_matches():
    """
    Recupera os jogos de ténis ao vivo utilizando a Live Tennis API oficial,
    extraindo as odds reais de cada jogo.
    """
    try:
        matches = []
        with LiveTennisAPI(api_key=API_KEY) as client:
            # Pede os jogos ativos
            live_list = client.list_matches(status="live")
            
            for item in live_list:
                match_id = str(getattr(item, "match_id", "unknown"))
                tournament = getattr(item, "tournament", "Torneio Ténis")
                
                p1_obj = getattr(item, "p1", None)
                p2_obj = getattr(item, "p2", None)
                
                player1 = getattr(p1_obj, "name", "Jogador 1") if p1_obj else "Jogador 1"
                player2 = getattr(p2_obj, "name", "Jogador 2") if p2_obj else "Jogador 2"
                
                score_obj = getattr(item, "score", None)
                current_set = getattr(score_obj, "current_set", 1) if score_obj else 1
                sets_data = getattr(score_obj, "sets", []) if score_obj else []
                
                set1_p1, set1_p2 = 0, 0
                set1_finished = False
                if sets_data and len(sets_data) > 0:
                    set1_p1 = getattr(sets_data[0], "p1", 0)
                    set1_p2 = getattr(sets_data[0], "p2", 0)
                    set1_p2_val = getattr(sets_data[0], "p2", 0)
                    # Consideramos o 1.º set terminado se houver pontuação avançada (ex: 6-3, 6-4, etc.)
                    if (set1_p1 >= 6 or set1_p2 >= 6) and abs(set1_p1 - set1_p2) >= 2:
                        set1_p1 = getattr(sets_data[0], "p1", 0)
                        set1_p2 = getattr(sets_data[0], "p2", 0)
                        set1_finished = True

                # --- EXTRAÇÃO DINÂMICA DE ODDS DA API ---
                raw_odds = getattr(item, "odds", None)
                
                # Valores predefinidos caso a API não traga odds para este jogo específico
                odd_p1 = 1.90
                odd_p2 = 1.90
                
                if raw_odds:
                    # Tenta extrair as odds reais dependendo de como a biblioteca as devolve
                    odd_p1 = float(getattr(raw_odds, "p1", getattr(raw_odds, "home", 1.90)))
                    odd_p2 = float(getattr(raw_odds, "p2", getattr(raw_odds, "away", 1.90)))
                
                # Determinar quem é o favorito e o underdog com base nas odds reais
                if odd_p1 <= odd_p2:
                    favorite = player1
                    underdog = player2
                    odds_favorite = odd_p1
                    odds_underdog = odd_p2
                else:
                    favorite = player2
                    underdog = player1
                    odds_favorite = odd_p2
                    odds_underdog = odd_p1

                formatted_match = {
                    "match_id": match_id,
                    "tournament": tournament,
                    "player1": player1,
                    "player2": player2,
                    "current_set": int(current_set),
                    "score_summary": str(sets_data),
                    "set1_finished": set1_finished,
                    "set1_p1": int(set1_p1),
                    "set1_p2": int(set1_p2),
                    "incidents": getattr(item, "incidents", []),
                    "odds": {
                        "favorite": favorite,
                        "underdog": underdog,
                        "odds_favorite": float(odds_favorite),
                        "odds_underdog": float(odds_underdog)
                    }
                }
                matches.append(formatted_match)
                
        return matches

    except Exception as e:
        print(f"[DATA SOURCE] Erro ao comunicar com a Live Tennis API: {e}")
        return []