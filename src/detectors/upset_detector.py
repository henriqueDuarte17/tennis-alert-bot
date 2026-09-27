def check_for_first_set_upset(match, odds_data):
    """
    Verifica se houve um upset no 1.º set para super favoritos.
    Critério: O favorito tinha uma odd máxima de 1.30 e perdeu o 1.º set.
    """
    print(f"[DEBUG] A analisar jogo ID {match.get('match_id')}: match={match}, odds_data={odds_data}", flush=True)

    set1_finished = match.get("set1_finished", False)
    if not set1_finished:
        return False, None, None
        
    p1_score = match.get("set1_p1", 0)
    p2_score = match.get("set1_p2", 0)
    
    player1 = match.get("player1")
    player2 = match.get("player2")
    
    odds_fav = odds_data.get("odds_favorite", 1.40)
    favorite = odds_data.get("favorite", player1)
    underdog = odds_data.get("underdog", player2)
    
    print(f"[DEBUG] odds_fav={odds_fav}, favorite={favorite}, p1={p1_score}, p2={p2_score}", flush=True)

    # DEFINIR LIMITE DE SUPER FAVORITO (odd máxima de 1.30)
    MAX_FAV_ODD = 1.30
    
    if odds_fav > MAX_FAV_ODD:
        return False, None, None # O favorito tinha uma odd superior a 1.30, ignorar
        
    # Verificar quem ganhou o 1.º set
    winner_set1 = player1 if p1_score > p2_score else player2
    
    # Se o vencedor do set NÃO foi o favorito, temos um upset de um super favorito!
    if winner_set1 != favorite:
        return True, winner_set1, favorite
        
    return False, None, None