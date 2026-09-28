from livetennisapi import LiveTennisAPI

API_KEY = "twjp_d0426f3915422fc340b35cab0bbaa7d9"

def fetch_live_tennis_matches():
    """
    Recupera os jogos de ténis ao vivo, extraindo os rankings oficiais dos jogadores
    e o estado/placar robusto do 1.º set.
    """
    try:
        matches = []
        with LiveTennisAPI(api_key=API_KEY) as client:
            live_list = client.list_matches(status="live")
            
            for item in live_list:
                match_id = str(getattr(item, "match_id", "unknown"))
                tournament = getattr(item, "tournament", "Torneio Ténis")
                
                p1_obj = getattr(item, "p1", None)
                p2_obj = getattr(item, "p2", None)
                
                player1 = getattr(p1_obj, "name", "Jogador 1") if p1_obj else "Jogador 1"
                player2 = getattr(p2_obj, "name", "Jogador 2") if p2_obj else "Jogador 2"
                
                # Extrair rankings (se disponíveis, caso contrário assume 9999)
                rank1 = int(getattr(p1_obj, "ranking", 9999) or 9999)
                rank2 = int(getattr(p2_obj, "ranking", 9999) or 9999)
                
                # Diagnóstico de rankings nos logs
                print(f"[RANK INSPECT] {player1} (Rank: {rank1}) vs {player2} (Rank: {rank2}) [Torneio: {tournament}]", flush=True)
                
                score_obj = getattr(item, "score", None)
                current_set = getattr(score_obj, "current_set", 1) if score_obj else 1
                sets_data = getattr(score_obj, "sets", []) if score_obj else []
                
                set1_p1, set1_p2 = 0, 0
                set1_finished = False
                
                if sets_data and len(sets_data) > 0:
                    first_set = sets_data[0]
                    
                    # Tentar extrair por atributos p1/p2 ou por índices/tuplos caso venha em formato de lista
                    if hasattr(first_set, "p1") and hasattr(first_set, "p2"):
                        set1_p1 = int(getattr(first_set, "p1", 0) or 0)
                        set1_p2 = int(getattr(first_set, "p2", 0) or 0)
                    elif isinstance(first_set, (list, tuple)) and len(first_set) >= 2:
                        set1_p1 = int(first_set[0] or 0)
                        set1_p2 = int(first_set[1] or 0)
                        
                    # O 1.º set está terminado se alguém chegou a 6 ou 7 com vantagem, ou se já avançámos para o 2.º set ou superior
                    if (set1_p1 >= 6 or set1_p2 >= 6) and abs(set1_p1 - set1_p2) >= 1:
                        set1_finished = True
                
                # Salvaguarda adicional: se o jogo já vai no 2.º set ou mais, o 1.º set está obrigatoriamente concluído
                if current_set > 1:
                    set1_finished = True

                # Diagnóstico robusto do 1.º set nos logs
                print(f"[SET1 INSPECT] {player1} vs {player2} | Placar Set 1: [{set1_p1} - {set1_p2}] | Current Set: {current_set} | Terminado: {set1_finished} | Sets: {sets_data}", flush=True)

                formatted_match = {
                    "match_id": match_id,
                    "tournament": tournament,
                    "player1": player1,
                    "player2": player2,
                    "rank1": rank1,
                    "rank2": rank2,
                    "current_set": int(current_set),
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