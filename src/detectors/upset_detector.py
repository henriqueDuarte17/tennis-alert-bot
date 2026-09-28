def check_for_first_set_upset(match, odds_data):
    """
    Verifica se houve um upset no 1.º set:
    1. Confirma se o 1.º set terminou (através do set1_finished).
    2. Identifica o super-favorito e o underdog pela diferença de ranking.
    3. Verifica quem venceu o 1.º set através do acumulado de sets ([1, 0] ou [0, 1]).
    4. Dispara o alerta se o vencedor do 1.º set foi o underdog (ou seja, se o super-favorito perdeu).
    """
    if not match.get("set1_finished", False):
        return False, None, None
        
    p1, p2 = match.get("player1"), match.get("player2")
    r1, r2 = match.get("rank1", 9999), match.get("rank2", 9999)
    
    if r1 == 9999 and r2 == 9999:
        return False, None, None
        
    # 1. Identificar favorito (menor rank) e underdog (maior rank)
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
    
    # 2. Validar se cumpre a tua tabela de super-favorito estrita
    is_super_favorite = False
    if fav_rank <= 100 and diff >= 100:
        is_super_favorite = True
    elif 100 < fav_rank <= 200 and diff >= 150:
        is_super_favorite = True
    elif fav_rank > 200 and diff >= 200:
        is_super_favorite = True
    # DIAGNÓSTICO: Mostra nos logs quem o bot considerou favorito, underdog e se passou o crivo
    print(f"[FAVOURITE CHECK] Favorito: {favorite} (Rank {fav_rank}) vs Underdog: {underdog} (Rank {und_rank}) | Dif: {diff} | É Super-Favorito: {is_super_favorite}", flush=True)
        
    if not is_super_favorite:
        return False, None, None
        
    # 3. Descobrir quem ganhou o 1.º set com base no array de sets [sets_p1, sets_p2]
    # set1_p1 e set1_p2 guardam agora os sets ganhos globais (ex: 1 para quem ganhou o 1.º set)
    p1_sets = match.get("set1_p1", 0)
    p2_sets = match.get("set1_p2", 0)
    
    # Se p1_sets for 1, o player1 ganhou o 1.º set. Se p2_sets for 1, foi o player2.
    if p1_sets > p2_sets:
        winner_set1 = p1
    elif p2_sets > p1_sets:
        winner_set1 = p2
    else:
        return False, None, None

    # 4. DISPARAR O ALERTA SE O VENCEDOR DO 1.º SET FOI O UNDERDOG (o super-favorito perdeu)
    if winner_set1 == underdog:
        return True, underdog, favorite
        
    return False, None, None