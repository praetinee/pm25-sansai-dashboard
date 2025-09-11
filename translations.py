# -*- coding: utf-8 -*-

TRANSLATIONS = {
    'th': {
        # General
        'page_title': "รายงานค่าฝุ่น PM2.5",
        'header': "รายงานค่าฝุ่น PM2.5 ณ จุดตรวจวัด รพ.สันทราย",
        'latest_data': "ข้อมูลล่าสุดเมื่อ:",
        'pm25_unit': "PM2.5 (μg/m³)",
        'avg_pm25_unit': "ค่าเฉลี่ย PM2.5 (μg/m³)",
        'month_names': ["มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน", "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"],


        # Realtime Section
        'current_pm25': "ค่า PM2.5 ปัจจุบัน",
        'advice_header': "คำแนะนำในการปฏิบัติตัว",
        'general_public': "ประชาชนทั่วไป",
        'risk_group': "กลุ่มเสี่ยง",

        # AQI Levels & Advice
        'aqi_level_1': "ดีมาก",
        'aqi_level_2': "ดี",
        'aqi_level_3': "ปานกลาง",
        'aqi_level_4': "เริ่มมีผลกระทบต่อสุขภาพ",
        'aqi_level_5': "มีผลกระทบต่อสุขภาพ",
        'advice_1_general': "สนุกกับกิจกรรมกลางแจ้งได้เต็มที่",
        'advice_1_risk': "สามารถทำกิจกรรมกลางแจ้งได้ตามปกติ",
        'advice_2_general': "ทำกิจกรรมกลางแจ้งได้ตามปกติ",
        'advice_2_risk': "ควรสังเกตอาการผิดปกติ เช่น ไอ หรือหายใจลำบาก",
        'advice_3_general': "ควรลดการทำกิจกรรมหรือออกกำลังกายกลางแจ้งที่ใช้แรงมาก",
        'advice_3_risk': "ควรลดระยะเวลาการทำกิจกรรมกลางแจ้ง และสวมหน้ากากป้องกันฝุ่น",
        'advice_4_general': "ควรลดระยะเวลาการทำกิจกรรมกลางแจ้ง และสวมหน้ากากป้องกันฝุ่น",
        'advice_4_risk': "ควรงดการทำกิจกรรมกลางแจ้ง หากจำเป็นให้ใช้อุปกรณ์ป้องกันตนเอง",
        'advice_5_general': "ควรงดกิจกรรมกลางแจ้ง และสวมหน้ากากป้องกันฝุ่นเมื่ออยู่นอกอาคาร",
        'advice_5_risk': "ควรงดออกจากอาคารโดยเด็ดขาด และอยู่ในห้องปลอดฝุ่น",
        
        # Health Impact Section
        'health_impact_title': "สรุปผลกระทบต่อสุขภาพ (จากข้อมูลทั้งหมด)",
        'unhealthy_days_text': "จำนวนวันที่ค่าฝุ่นเกินเกณฑ์ (>37.5 µg/m³)",
        'cigarette_equivalent_text': "เทียบเท่าการสูบบุหรี่สะสม",
        'health_impact_explanation': "หมายเหตุ: คำนวณจากค่าเฉลี่ยฝุ่นสะสมทั้งหมด โดยเทียบว่าการได้รับ PM2.5 เฉลี่ย 22 µg/m³ ตลอด 24 ชั่วโมง เทียบเท่าการสูบบุหรี่ 1 มวน (เป็นการเปรียบเทียบเพื่อให้เห็นภาพผลกระทบ)",
        'days_unit': "วัน",
        'cigarettes_unit': "มวน",

        # Charts
        'hourly_trend_today': "แนวโน้มค่า PM2.5 รายชั่วโมงของวันนี้",
        'no_data_today': "ยังไม่มีข้อมูลสำหรับวันนี้",
        'daily_avg_chart_title': "ค่าเฉลี่ย PM2.5 รายวัน",

        # Calendar
        'monthly_calendar_header': "ปฏิทินค่าฝุ่น PM2.5 รายวัน",
        'date_picker_label': "เลือกเดือนและปีที่ต้องการดู",
        'days_header': ["จันทร์", "อังคาร", "พุธ", "พฤหัส", "ศุกร์", "เสาร์", "อาทิตย์"],

        # Historical Data
        'historical_expander': "📊 ดูข้อมูลย้อนหลัง (คลิกเพื่อเลือกช่วงวัน)",
        'start_date': "วันที่เริ่มต้น",
        'end_date': "สิ้นสุด",
        'date_error': "วันที่เริ่มต้นต้องมาก่อนวันที่สิ้นสุด",
        'no_data_in_range': "ไม่พบข้อมูลในช่วงวันที่ที่เลือก",
        'metric_avg': "ค่าเฉลี่ย",
        'metric_max': "ค่าสูงสุด",
        'metric_min': "ค่าต่ำสุด",

        # Knowledge Tabs
        'knowledge_header': "💡 เกร็ดความรู้เกี่ยวกับ PM2.5",
        'tabs': ["PM2.5 คืออะไร?", "ความเข้าใจผิด", "DIY ป้องกันฝุ่น", "การเลือกหน้ากาก"]
    },
    'en': {
        # General
        'page_title': "PM2.5 Report",
        'header': "PM2.5 Report @ San Sai Hospital Station",
        'latest_data': "Last updated:",
        'pm25_unit': "PM2.5 (μg/m³)",
        'avg_pm25_unit': "Average PM2.5 (μg/m³)",
        'month_names': ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],

        # Realtime Section
        'current_pm25': "Current PM2.5",
        'advice_header': "Health Recommendations",
        'general_public': "General Public",
        'risk_group': "Sensitive Groups",

        # AQI Levels & Advice
        'aqi_level_1': "Very Good",
        'aqi_level_2': "Good",
        'aqi_level_3': "Moderate",
        'aqi_level_4': "Unhealthy for Sensitive Groups",
        'aqi_level_5': "Unhealthy",
        'advice_1_general': "Enjoy outdoor activities freely.",
        'advice_1_risk': "Normal outdoor activities are fine.",
        'advice_2_general': "You can do outdoor activities normally.",
        'advice_2_risk': "Monitor for symptoms like coughing or difficulty breathing.",
        'advice_3_general': "Reduce strenuous outdoor activities.",
        'advice_3_risk': "Limit time outdoors and wear a protective mask.",
        'advice_4_general': "Limit time outdoors and wear a protective mask.",
        'advice_4_risk': "Avoid outdoor activities. Use personal protective equipment if necessary.",
        'advice_5_general': "Avoid outdoor activities and wear a mask if you must go out.",
        'advice_5_risk': "Stay indoors in a clean or air-purified room.",
        
        # Health Impact Section
        'health_impact_title': "Health Impact Summary (All-time Data)",
        'unhealthy_days_text': "Days Above Guideline (>37.5 µg/m³)",
        'cigarette_equivalent_text': "Cumulative Cigarette Equivalent",
        'health_impact_explanation': "Note: Calculated from total cumulative exposure, where an average daily exposure of 22 µg/m³ is roughly equivalent to smoking 1 cigarette (This is an approximation to illustrate the health impact).",
        'days_unit': "days",
        'cigarettes_unit': "cigarettes",

        # Charts
        'hourly_trend_today': "Today's Hourly PM2.5 Trend",
        'no_data_today': "No data available for today yet.",
        'daily_avg_chart_title': "Daily Average PM2.5",

        # Calendar
        'monthly_calendar_header': "Daily PM2.5 Calendar",
        'date_picker_label': "Select month and year to view",
        'days_header': ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],

        # Historical Data
        'historical_expander': "📊 View Historical Data (Click to select date range)",
        'start_date': "Start Date",
        'end_date': "End Date",
        'date_error': "Start date must be before end date.",
        'no_data_in_range': "No data found for the selected range.",
        'metric_avg': "Average",
        'metric_max': "Maximum",
        'metric_min': "Minimum",

        # Knowledge Tabs
        'knowledge_header': "💡 PM2.5 Knowledge Base",
        'tabs': ["What is PM2.5?", "Misconceptions", "DIY Air Purifier", "Mask Selection"]
    }
}

