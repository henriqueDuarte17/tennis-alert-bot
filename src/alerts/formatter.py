def format_mto_alert(match_data, player_name):
    """Formata a mensagem de Medical Timeout para o Telegram."""
    return (
        f"🚑 **MEDICAL TIMEOUT**\n"
        f"🎾 {match_data.get('player1')} vs. {match_data.get('player2')}\n"
        f"👤 **Jogador Afetado:** {player_name}\n"
        f"📊 {match_data.get('score_summary', 'N/A')}\n"
        f"⏱️ Set {match_data.get('current_set', 1)}\n"
        f"🏆 {match_data.get('tournament', 'ATP Challenger')}"
    )

def format_upset_alert(match_data, underdog_name, favorite_name, odds_favorite, odds_underdog):
    """Formata a mensagem de alerta quando o favorito perde o 1.º set."""
    return (
        f"⚠️ **RESULTADO INESPERADO (1.º SET)**\n"
        f"🎾 {match_data.get('player1')} vs. {match_data.get('player2')}\n"
        f"📊 **{underdog_name}** venceu o 1.º set!\n"
        f"📈 **Odds Pré-Live:** {favorite_name} ({odds_favorite}) vs {underdog_name} ({odds_underdog})\n"
        f"🏆 {match_data.get('tournament', 'ATP Challenger')}"
    )