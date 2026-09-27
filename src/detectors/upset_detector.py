def check_for_first_set_upset(match, odds_data):
    """
    Verifica se houve um upset no 1.º set baseado na tabela de diferenças de Ranking:
    - Top 100: diferença >= 100 posições
    - Rank 101 a 200: diferença >= 150 posições
    - Rank > 200: diferença >= 200 posições
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
        
    rank_diff = und_rank - fav_rank
    
    # APLICAR A SUA TABELA DE CRITÉRIOS DE SUPER-FAVORITO:
    is_super_favorite = False
    
    if fav_rank <= 100:
        if rank_diff >= 100:
            is_super_favorite = True
    elif fav_rank <= 200:
        if rank_diff >= 150:
            is_super_favorite = True
    else:
        if rank_diff >= 200:
            is_super_favorite = True
            
    if not is_super_favorite:
        return False, None, None
        
    # Se o super-favorito PERDEU o 1.º set, temos um upset!
    winner_set1 = player1 if p1_score > p2_score else player2
    
    if winner_set1 != favorite:
        return True, winner_set1, favorite
        
    return False, None, None