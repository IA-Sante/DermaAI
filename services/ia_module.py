def analyze_symptoms(duration: str, pain: int, itching: int, bleeding: int):
    # Simulation du Module NLP (Extraction de signaux)
    score = 0.0
    if pain == 1: 
        score += 0.3
    if bleeding == 1: 
        score += 0.4
    if itching == 1: 
        score += 0.2
    
    # On s'assure que le score ne dépasse pas 1.0
    return min(score, 1.0)

def calculate_fusion(score_image: float, score_symptoms: float):
    # Formule officielle de fusion (0.6 * Vision + 0.4 * NLP)
    return (0.6 * score_image) + (0.4 * score_symptoms)

def get_risk_level(score_global: float):
    # Détermination du risque et recommandation
    if score_global <= 0.33:
        return "faible", "Risque faible. Surveillez l'évolution de la lésion."
    elif score_global <= 0.66:
        return "modéré", "Risque modéré. Une consultation dermatologique est conseillée."
    else:
        return "élevé", "Risque élevé. Consultez un dermatologue rapidement."