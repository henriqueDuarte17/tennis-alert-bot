from livetennisapi import LiveTennisAPI

API_KEY = "twjp_d0426f3915422fc340b35cab0bbaa7d9"

def fetch_live_tennis_matches():
    try:
        matches = []
        with LiveTennisAPI(api_key=API_KEY) as client:
            live_list = client.list_matches(status="live")
            
            for item in live_list:
                # DEBUG TOTAL: Imprime todos os atributos e métodos disponíveis no objeto da API
                print(f"[API INSPECT] Atributos disponíveis no item: {dir(item)}", flush=True)
                if hasattr(item, "odds"):
                    print(f"[API INSPECT] Objeto odds bruto: {item.odds} (tipo: {type(item.odds)})", flush=True)
                
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
                    # Consideramos o 1.º set terminado se houver jogos suficientes (ex: 6-x ou 7-x)
                    if (set1_p1 >= 6 or set1_p2 >= 6) and abs(set1_p1 - set1_p2) >= 1:
                        set1_finished = True

                # Vamos apenas devolver um dummy para ver os logs do inspect
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
                        "favorite": player1,
                        "underdog": player2,
                        "odds_favorite": 1.90,
                        "odds_underdog": 1.90
                    }
                }
                matches.append(formatted_match)
                break # Apenas inspecionamos o primeiro jogo para não inundar os logs
                
        return matches

    except Exception as e:
        print(f"[DATA SOURCE] Erro ao comunicar com a Live Tennis API: {e}")
        return []