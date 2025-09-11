# -*- coding: utf-8 -*-

def get_aqi_level(pm25, lang, t):
    """
    Converts PM2.5 value to an AQI level, color, emoji, and advice in the selected language.
    """
    if pm25 <= 15:
        level = t[lang]['aqi_level_1']
        color = "#0099FF"
        emoji = "😊"
        advice = f"<strong>{t[lang]['general_public']}:</strong> {t[lang]['advice_1_general']}<br><strong>{t[lang]['risk_group']}:</strong> {t[lang]['advice_1_risk']}"
    elif 15 < pm25 <= 25:
        level = t[lang]['aqi_level_2']
        color = "#2ECC71"
        emoji = "🙂"
        advice = f"<strong>{t[lang]['general_public']}:</strong> {t[lang]['advice_2_general']}<br><strong>{t[lang]['risk_group']}:</strong> {t[lang]['advice_2_risk']}"
    elif 25 < pm25 <= 37.5:
        level = t[lang]['aqi_level_3']
        color = "#F1C40F"
        emoji = "😐"
        advice = f"<strong>{t[lang]['general_public']}:</strong> {t[lang]['advice_3_general']}<br><strong>{t[lang]['risk_group']}:</strong> {t[lang]['advice_3_risk']}"
    elif 37.5 < pm25 <= 75:
        level = t[lang]['aqi_level_4']
        color = "#E67E22"
        emoji = "😷"
        advice = f"<strong>{t[lang]['general_public']}:</strong> {t[lang]['advice_4_general']}<br><strong>{t[lang]['risk_group']}:</strong> {t[lang]['advice_4_risk']}"
    else: 
        level = t[lang]['aqi_level_5']
        color = "#E74C3C"
        emoji = "🤢"
        advice = f"<strong>{t[lang]['general_public']}:</strong> {t[lang]['advice_5_general']}<br><strong>{t[lang]['risk_group']}:</strong> {t[lang]['advice_5_risk']}"
    
    return level, color, emoji, advice

