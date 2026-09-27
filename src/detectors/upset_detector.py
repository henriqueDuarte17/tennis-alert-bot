def check_for_first_set_upset(match, odds_data):
    """
    Verifica se houve um upset no 1.º set baseado na diferença de Ranking (Super-Favorito).
    Critério: O favorito por ranking (posição muito superior) perdeu o 1.º set.
    """
    set1_finished = match.get("set1_finished", False)
    if not set1_finished:
        return False, None, None
        
    p1_score = match.get("set1_p1", 0)
    p2_score = match.get("set1_p2", 0)
    
    player1 = match.get("player1")
    player2 = match.get("player2")
    rank1 = match.get("rank1", 9999)
    rank2 = match.get("rank2", 9999)
    
    # Se ambos não tiverem ranking conhecido, ignoramos
    if rank1 == 9999 and rank2 == 9999:
        return False, None, None
        
    # Determinar quem é o super-favorito pelo ranking
    if rank1 < rank2:
        favorite = player1
        underdog = player2
        fav_rank = rank1
        und_rank = rank2
    else:
        favorite = player2
        underdog = player1
        fav_rank = rank2
        und_rank = rank1
        
    # CRITÉRIO DE SUPER-FAVORITO POR RANKING:
    # O favorito tem de ter um bom ranking (ex: <= 300) e a diferença para o adversário tem de ser grande (ex: >= 300 posições)
    rank_diff = und_rank - fav_rank
    is_super_favorite = (fav_rank <= 300 and rank_diff >= 300) or (fav_rank <= 100 and rank_diff >= 150)
    
    if not is_super_favorite:
        return False, None, None
        
    # Se o super-favorito PERDEU o 1.º set, temos um upset!
    winner_set1 = player1 if p1_score > p2_score else player2
    
    if winner_set1 != favorite:
        return True, winner_set1, favorite
        
    return False, None, None