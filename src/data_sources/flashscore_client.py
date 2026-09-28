from livetennisapi import LiveTennisAPI

API_KEY = "twjp_d0426f3915422fc340b35cab0bbaa7d9"

def fetch_live_tennis_matches():
    """
    Recupera os jogos ao vivo, gerando um ID único e seguro para evitar o estado 'unknown'
    e utilizando o acumulado de sets [p1_sets, p2_sets] para determinar o fim do 1.º set.
    """
    try:
        matches = []
        with LiveTennisAPI(api_key=API_KEY) as client:
            live_list = client.list_matches(status="live")
            
            for item in live_list:
                p1_obj = getattr(item, "p1", None)
                p2_obj = getattr(item, "p2", None)
                
                player1 = getattr(p1_obj, "name", "Jogador 1") if p1_obj else "Jogador 1"
                player2 = getattr(p2_obj, "name", "Jogador 2") if p2_obj else "Jogador 2"
                
                # Salvaguarda robusta: se o ID vier vazio ou unknown, cria um ID único com os nomes
                raw_id = getattr(item, "match_id", None)
                if not raw_id or str(raw_id).lower() == "unknown":
                    match_id = f"{player1}_{player2}".replace(" ", "_")
                else:
                    match_id = str(raw_id)
                
                tournament = getattr(item, "tournament", "Torneio Ténis")
                
                # Extrair rankings
                rank1 = int(getattr(p1_obj, "ranking", 9999) or 9999)
                rank2 = int(getattr(p2_obj, "ranking", 9999) or 9999)
                
                score_obj = getattr(item, "score", None)
                sets_data = getattr(score_obj, "sets", []) if score_obj else []
                
                set1_p1, set1_p2 = 0, 0
                set1_finished = False
                
                # O sets_data vem como uma lista com os sets ganhos por cada jogador, ex: [0, 1] ou [1, 0] ou [0, 0]
                if sets_data and isinstance(sets_data, (list, tuple)) and len(sets_data) >= 2:
                    p1_sets_won = int(sets_data[0] or 0)
                    p2_sets_won = int(sets_data[1] or 0)
                    
                    set1_p1 = p1_sets_won
                    set1_p2 = p2_sets_won
                    
                    # O 1.º set SÓ terminou se a soma dos sets ganhos for pelo menos 1 (ex: [1, 0] ou [0, 1])
                    if (p1_sets_won + p2_sets_won) > 0:
                        set1_finished = True
                
                # Log limpo para validação em tempo real
                print(f"[SET1 CHECK] {player1} vs {player2} | ID: {match_id} | Sets Ganhos: {sets_data} | Terminado: {set1_finished}", flush=True)

                formatted_match = {
                    "match_id": match_id,
                    "tournament": tournament,
                    "player1": player1,
                    "player2": player2,
                    "rank1": rank1,
                    "rank2": rank2,
                    "score_summary": str(sets_data),
                    "set1_finished": set1_finished,
                    "set1_p1": int(set1_p1),
                    "set1_p2": int(set1_p2),
                    "incidents": getattr(item, "incidents", []),
                    "odds": {
                        "favorite": player1 if rank1 < rank2 else player2,
                        "underdog": player2 if rank1 < rank2 else player1,
                        "odds_favorite": 1.25,
                        "odds_underdog": 3.50
                    }
                }
                matches.append(formatted_match)
                
        return matches

    except Exception as e:
        print(f"[DATA SOURCE] Erro ao comunicar com a Live Tennis API: {e}")
        return []