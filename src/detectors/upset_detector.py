def check_for_first_set_upset(match, odds_data):
    """
    Verifica se houve um upset no 1.º set:
    - Identifica o super-favorito com base na tabela de rankings.
    - Confirma se o 1.º set terminou.
    - Dispara o alerta SE O SUPER-FAVORITO PERDEU o 1.º set.
    """
    if not match.get("set1_finished", False):
        return False, None, None
        
    p1, p2 = match.get("player1"), match.get("player2")
    r1, r2 = match.get("rank1", 9999), match.get("rank2", 9999)
    
    if r1 == 9999 and r2 == 9999:
        return False, None, None
        
    # 1. Identificar quem é o favorito (menor número de rank) e o underdog (maior número)
    if r1 < r2:
        favorite = p1
        underdog = p2
        fav_rank = r1
        und_rank = r2
    else:
        favorite = p2
        underdog = p1
        fav_rank = r2
        und_rank = r1
        
    diff = und_rank - fav_rank
    
    # 2. Validar se o favorito cumpre os critérios de super-favorito por patamares
    is_super_favorite = False
    if fav_rank <= 100 and diff >= 100:
        is_super_favorite = True
    elif 100 < fav_rank <= 200 and diff >= 150:
        is_super_favorite = True
    elif fav_rank > 200 and diff >= 200:
        is_super_favorite = True
        
    if not is_super_favorite:
        return False, None, None
        
    # 3. Ver quem ganhou o 1.º set
    p1_score = match.get("set1_p1", 0)
    p2_score = match.get("set1_p2", 0)
    
    winner_set1 = p1 if p1_score > p2_score else p2
    
    # 4. O UPSET OCORRE SE O VENCEDOR DO SET FOR DIFERENTE DO SUPER-FAVORITO
    if winner_set1 != favorite:
        # winner_set1 é o underdog que surpreendeu, favorite foi quem perdeu o set
        return True, winner_set1, favorite
        
    return False, None, None