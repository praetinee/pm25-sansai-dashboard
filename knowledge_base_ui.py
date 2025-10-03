import streamlit as st
import random

def display_knowledge_quiz(lang, t):
    """
    Displays an interactive quiz about PM2.5 facts,
    followed by a simple infographic-style summary.
    """
    st.subheader(t[lang]['quiz_header'])
    st.markdown(t[lang]['quiz_intro'])
    st.write("---")

    quiz_items = t[lang]['quiz_content']

    # --- Session State Initialization ---
    if 'current_question_index' not in st.session_state:
        st.session_state.current_question_index = 0
    if 'user_answer' not in st.session_state:
        st.session_state.user_answer = None
    if 'quiz_order' not in st.session_state:
        st.session_state.quiz_order = random.sample(range(len(quiz_items)), len(quiz_items))


    # Get the current question based on the randomized order
    q_index = st.session_state.quiz_order[st.session_state.current_question_index]
    question_data = quiz_items[q_index]
    correct_answer = question_data['answer']

    # --- Display Question ---
    st.markdown(f"#### {t[lang]['question_title']} {st.session_state.current_question_index + 1}:")
    st.markdown(f"### {question_data['question']}")
    st.write("")

    # --- Answer Submission Logic ---
    def submit_answer(answer):
        st.session_state.user_answer = answer

    # --- Display Answer Buttons ---
    if st.session_state.user_answer is None:
        col1, col2 = st.columns(2)
        with col1:
            st.button(t[lang]['quiz_true'], on_click=submit_answer, args=(True,), use_container_width=True)
        with col2:
            st.button(t[lang]['quiz_false'], on_click=submit_answer, args=(False,), use_container_width=True)
    
    # --- Display Result and Explanation ---
    if st.session_state.user_answer is not None:
        is_correct = (st.session_state.user_answer == correct_answer)
        
        if is_correct:
            st.success(f"**{t[lang]['quiz_correct']}** {question_data['explanation']}")
        else:
            st.error(f"**{t[lang]['quiz_incorrect']}** {question_data['explanation']}")

        # --- Display Infographic ---
        st.markdown(f"""
        <div style="border: 2px solid #1E90FF; border-radius: 10px; padding: 20px; margin-top: 20px; background-color: #F0F8FF;">
            <h4 style="color: #1E90FF; text-align: center;">{question_data['infographic_title']}</h4>
            <ul style="list-style-type: '✅ '; padding-left: 20px;">
                {''.join([f"<li>{point}</li>" for point in question_data['infographic_points']])}
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("---")

        def next_question():
            next_idx = (st.session_state.current_question_index + 1) % len(quiz_items)
            st.session_state.current_question_index = next_idx
            st.session_state.user_answer = None
        
        st.button(t[lang]['quiz_next_question'], on_click=next_question, use_container_width=True)

