def get_aqi_level(pm25, lang, t):
    """
    Converts a PM2.5 value into its corresponding AQI level, color, emoji, and advice
    based on the provided language and translation dictionary.
    """
    # Use the translation dictionary 't' for language-specific text
    advice_dict = t[lang]['advice']
    
    # 0-15.0: Blue (Excellent)
    if pm25 <= 15:
        level_key = 'aqi_level_1'
        advice_key = 'advice_1'
        color = "#0099FF"
        emoji = "😊"
    # 15.1-25.0: Green (Good)
    elif 15 < pm25 <= 25:
        level_key = 'aqi_level_2'
        advice_key = 'advice_2'
        color = "#2ECC71"
        emoji = "🙂"
    # 25.1-37.5: Yellow (Moderate)
    elif 25 < pm25 <= 37.5:
        level_key = 'aqi_level_3'
        advice_key = 'advice_3'
        color = "#F1C40F"
        emoji = "😐"
    # 37.6-75.0: Orange (Unhealthy for Sensitive Groups)
    elif 37.5 < pm25 <= 75:
        level_key = 'aqi_level_4'
        advice_key = 'advice_4'
        color = "#E67E22"
        emoji = "😷"
    # >75.0: Red (Unhealthy)
    else: 
        level_key = 'aqi_level_5'
        advice_key = 'advice_5'
        color = "#E74C3C"
        emoji = "🤢"
        
    level = t[lang][level_key]
    advice = advice_dict[advice_key]
    
    return level, color, emoji, advice

