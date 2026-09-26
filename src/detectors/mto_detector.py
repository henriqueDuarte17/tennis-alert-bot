import time

# Dicionário em memória para memorizar o último score e o momento exato em que foi visto
# Formato: {match_id: {"score": str, "timestamp": float}}
match_state_cache = {}

def check_for_mto(match):
    """
    Deteta MTOs combinando duas frentes:
    1. Análise explícita de incidentes médicos no feed (se disponíveis).
    2. Heurística de paragem prolongada (se o score ficar congelado por mais de X minutos).
    Retorna: (mto_detected: bool, player_affected: str)
    """
    match_id = match.get("match_id")
    incidents = match.get("incidents", [])
    current_score = match.get("score_summary", "")
    player1 = match.get("player1", "Jogador 1")
    player2 = match.get("player2", "Jogador 2")
    
    # -------------------------------------------------------------------------
    # 1. ABORDAGEM EXPLÍCITA (Análise de incidentes da API)
    # -------------------------------------------------------------------------
    if incidents and isinstance(incidents, list):
        mto_keywords = ["medical", "mto", "physio", "trainer", "injury", "treatment"]
        for incident in incidents:
            incident_text = ""
            player_affected = "Jogador Afetado"
            
            if isinstance(incident, dict):
                incident_text = str(incident.get("text", "")).lower()
                player_affected = incident.get("player", "Jogador Afetado")
            elif isinstance(incident, str):
                incident_text = incident.lower()
                
            if any(keyword in incident_text for keyword in mto_keywords):
                return True, player_affected

    # -------------------------------------------------------------------------
    # 2. ABORDAGEM HEURÍSTICA (Tempo / Congelamento de Placares)
    # -------------------------------------------------------------------------
    current_time = time.time()
    
    if match_id not in match_state_cache:
        # Primeiro registo deste jogo
        match_state_cache[match_id] = {
            "score": current_score,
            "timestamp": current_time
        }
        return False, None
        
    stored_state = match_state_cache[match_id]
    
    # Se o placar mudou, resetamos o cronómetro para este jogo
    if stored_state["score"] != current_score:
        match_state_cache[match_id] = {
            "score": current_score,
            "timestamp": current_time
        }
        return False, None
        
    # Se o placar NÃO mudou, calculamos há quantos segundos está estagnado
    elapsed_seconds = current_time - stored_state["timestamp"]
    
    # Limiar: Se passar de 240 segundos (4 minutos) sem mexer no score, 
    # assume-se uma paragem prolongada / tratamento médico.
    MTO_TIME_THRESHOLD_SECONDS = 240
    
    if elapsed_seconds > MTO_TIME_THRESHOLD_SECONDS:
        # Atribuímos cautelosamente ao primeiro jogador ou geramos aviso de paragem
        return True, f"{player1} (Paragem prolongada > 4m)"
        
    return False, None