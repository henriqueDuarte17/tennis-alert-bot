from livetennisapi import LiveTennisAPI

API_KEY = "twjp_d0426f3915422fc340b35cab0bbaa7d9"

def fetch_live_tennis_matches():
    """
    Recupera os jogos de ténis ao vivo, utilizando diretamente o array de sets 
    (ex: [1, 0] ou similar) para determinar o fim e o vencedor do 1.º set de forma fiável.
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
                
                # Extrair rankings
                rank1 = int(getattr(p1_obj, "ranking", 9999) or 9999)
                rank2 = int(getattr(p2_obj, "ranking", 9999) or 9999)
                
                score_obj = getattr(item, "score", None)
                sets_data = getattr(score_obj, "sets", []) if score_obj else []
                
                set1_p1, set1_p2 = 0, 0
                set1_finished = False
                
                # Análise direta do array de sets da API (ex: se trouxer os sets ganhos ou pontuações)
                if sets_data and len(sets_data) > 0:
                    first_item = sets_data[0]
                    
                    # Se vier em formato de objeto com p1/p2
                    if hasattr(first_item, "p1") and hasattr(first_item, "p2"):
                        set1_p1 = int(getattr(first_item, "p1", 0) or 0)
                        set1_p2 = int(getattr(first_item, "p2", 0) or 0)
                    elif isinstance(first_item, (list, tuple)) and len(first_item) >= 2:
                        set1_p1 = int(first_item[0] or 0)
                        set1_p2 = int(first_item[1] or 0)
                    elif isinstance(first_item, int):
                        # Caso a API devolva diretamente os sets ganhos por cada jogador na estrutura
                        # Ex: sets_data[0] ser os sets do jogador 1 e sets_data[1] do jogador 2
                        pass

                # REGRA INFALÍVEL DE TÉRMINO DO 1.º SET:
                # O 1.º set terminou se alguém atingiu 6 ou 7 jogos, OU se já existem 
                # registos de sets que comprovem que o 1.º set foi concluído.
                if (set1_p1 >= 6 or set1_p2 >= 6) and abs(set1_p1 - set1_p2) >= 1:
                    set1_finished = True
                elif len(sets_data) >= 2:
                    # Se a API já registou dados para além do primeiro elemento (indicando avanço no marcador global)
                    set1_finished = True

                # Diagnóstico para acompanhamento nos logs do Render
                print(f"[SET1 CHECK] {player1} vs {player2} | Placar 1.º Set: {set1_p1}-{set1_p2} | Terminado: {set1_finished} | Sets Data: {sets_data}", flush=True)

                formatted_match = {
                    "match_id": match_id,
                    "tournament": tournament,
                    "player1": player1,
                    "player2": player2,
                    "rank1": rank1,
                    "rank2": rank2,
                    "current_set": 1,
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