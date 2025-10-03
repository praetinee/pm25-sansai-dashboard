import streamlit as st
import random

def display_infographic(infographic_data, lang, t):
    """
    Displays a styled infographic card based on the provided data.
    """
    st.write("") # Spacer
    st.subheader(t[lang]['infographic_title'])

    # CSS for the infographic card, embedded here to keep the component self-contained
    st.markdown(f"""
    <style>
        .infographic-card {{
            background-color: #f0f8ff; /* Light AliceBlue background */
            border-left: 5px solid #1e90ff; /* DodgerBlue accent */
            border-radius: 8px;
            padding: 20px;
            margin-top: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        }}
        .infographic-card h4 {{
            margin-top: 0;
            margin-bottom: 15px;
            color: #1e40af;
        }}
        .infographic-card ul {{
            list-style-type: none;
            padding-left: 0;
        }}
        .infographic-card li {{
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            font-size: 1.05rem;
        }}
        .infographic-card .icon {{
            font-size: 1.5rem;
            margin-right: 15px;
            width: 30px; /* Ensures text alignment */
            text-align: center;
        }}
    </style>
    """, unsafe_allow_html=True)

    # Build the list of points for the infographic
    html_points = "<ul>"
    for point in infographic_data.get('points', []):
        icon = point.get('icon', '🔹') 
        text = point.get('text', '')
        html_points += f"<li><span class='icon'>{icon}</span><span>{text}</span></li>"
    html_points += "</ul>"

    # Display the final infographic card
    st.markdown(f"""
    <div class="infographic-card">
        <h4>{infographic_data.get('title', '')}</h4>
        {html_points}
    </div>
    """, unsafe_allow_html=True)

def display_knowledge_quiz(lang, t):
    """
    Displays an interactive "Fact or Myth" quiz about PM2.5.
    After answering, it shows an explanation and a related infographic.
    """
    st.header(t[lang]['quiz_header'])
    st.markdown(t[lang]['quiz_intro'])

    # Initialize session state for quiz
    if 'quiz_question_id' not in st.session_state:
        st.session_state.quiz_question_id = None
        st.session_state.quiz_answered = False

    # Get the list of questions
    questions = t[lang]['quiz_questions']
    
    # --- Question Selection ---
    if st.session_state.quiz_question_id is None:
        st.session_state.quiz_question_id = random.choice([q['id'] for q in questions])

    # Find the current question from the list
    current_q = next((q for q in questions if q['id'] == st.session_state.quiz_question_id), None)
    if not current_q: # Fallback if ID not found
        st.error("Error loading question.")
        return
        
    st.subheader(t[lang]['quiz_question_title'])
    st.markdown(f"### {current_q['question']}")

    # --- Answer Buttons ---
    col1, col2, col3 = st.columns([1,1,5])
    
    def handle_answer(user_answer):
        st.session_state.user_answer = user_answer
        st.session_state.quiz_answered = True

    with col1:
        st.button(f"👍 {t[lang]['quiz_true']}", on_click=handle_answer, args=(True,), use_container_width=True, disabled=st.session_state.quiz_answered)
    with col2:
        st.button(f"👎 {t[lang]['quiz_false']}", on_click=handle_answer, args=(False,), use_container_width=True, disabled=st.session_state.quiz_answered)

    # --- Display Result and Infographic ---
    if st.session_state.quiz_answered:
        is_correct = (st.session_state.user_answer == current_q['answer'])
        
        if is_correct:
            st.success(f"**ถูกต้องครับ!** {current_q['explanation']}")
        else:
            st.error(f"**ยังไม่ถูกนะครับ** {current_q['explanation']}")
        
        # Display Infographic if it exists for this question
        infographic_key = current_q.get('infographic_key')
        if infographic_key:
            infographic_data = t[lang].get('infographics', {}).get(infographic_key)
            if infographic_data:
                display_infographic(infographic_data, lang, t)

        st.write("") # Spacer
        if st.button(f"🔁 {t[lang]['quiz_next_question']}"):
            st.session_state.quiz_question_id = None
            st.session_state.quiz_answered = False
            st.session_state.user_answer = None
            st.rerun()
