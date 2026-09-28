def check_for_first_set_upset(match, odds_data):
    """
    Verifica se houve um upset no 1.º set, filtrando e ignorando torneios fracos (ITFs, etc.).
    """
    # 1. FILTRAGEM DE TORNEIOS: Ignorar torneios abaixo de Challenger (ITFs, W15, M15, etc.)
    tournament = match.get("tournament", "").upper()
    
    # Termos a excluir
    termos_proibidos = ["ITF", "W15", "W25", "W35", "W50", "W75", "W100", "M15", "M25", "M35"]
    if any(termo in tournament for termo in termos_proibidos):
        return False, None, None

    if not match.get("set1_finished", False):
        return False, None, None
        
    p1, p2 = match.get("player1"), match.get("player2")
    r1, r2 = match.get("rank1", 9999), match.get("rank2", 9999)
    
    if r1 == 9999 and r2 == 9999:
        return False, None, None
        
    # Identificar favorito (menor rank) e underdog (maior rank)
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
    
    # Validar critérios de super-favorito
    is_super_favorite = False
    if fav_rank <= 100 and diff >= 100:
        is_super_favorite = True
    elif 100 < fav_rank <= 200 and diff >= 150:
        is_super_favorite = True
    elif fav_rank > 200 and diff >= 200:
        is_super_favorite = True
        
    if not is_super_favorite:
        return False, None, None
        
    # Obter os sets ganhos por p1 e p2 [sets_p1, sets_p2]
    p1_sets = match.get("set1_p1", 0)
    p2_sets = match.get("set1_p2", 0)
    
    winner_set1 = None
    if p1_sets > p2_sets:
        winner_set1 = p1
    elif p2_sets > p1_sets:
        winner_set1 = p2
    else:
        return False, None, None

    # Disparar alerta se o vencedor do 1.º set foi o underdog
    if winner_set1 == underdog:
        print(f"[UPSET DETECTED!] O super-favorito {favorite} perdeu o 1.º set para o underdog {underdog} no torneio {tournament}!", flush=True)
        return True, underdog, favorite
        
    return False, None, None