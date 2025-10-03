import streamlit as st
import random
import markdown

def display_knowledge_base(lang, t):
    st.header(t[lang]['quiz_header'])
    st.write(t[lang]['quiz_intro'])
    st.divider()

    # --- Initialize session state for the quiz ---
    if 'quiz_started' not in st.session_state:
        st.session_state.quiz_started = False
    if 'quiz_finished' not in st.session_state:
        st.session_state.quiz_finished = False
    if 'quiz_score' not in st.session_state:
        st.session_state.quiz_score = 0
    if 'questions_answered' not in st.session_state:
        st.session_state.questions_answered = 0
    if 'asked_question_ids' not in st.session_state:
        st.session_state.asked_question_ids = []
    if 'current_question' not in st.session_state:
        st.session_state.current_question = None
    if 'answer_submitted' not in st.session_state:
        st.session_state.answer_submitted = False
    
    QUIZ_LENGTH = 5

    # --- Callback function to start/restart the quiz ---
    def start_quiz():
        st.session_state.quiz_started = True
        st.session_state.quiz_finished = False
        st.session_state.quiz_score = 0
        st.session_state.questions_answered = 0
        st.session_state.asked_question_ids = []
        st.session_state.answer_submitted = False
        select_new_question()

    # --- Select a new, unasked question ---
    def select_new_question():
        available_questions = [q for q in t[lang]['quiz_questions'] if q['id'] not in st.session_state.asked_question_ids]
        if available_questions:
            st.session_state.current_question = random.choice(available_questions)
            st.session_state.asked_question_ids.append(st.session_state.current_question['id'])
        else:
            # If all questions have been asked, but quiz is not finished (rare case), finish it.
            st.session_state.quiz_finished = True
        st.session_state.answer_submitted = False

    # --- Handle user's answer ---
    def handle_answer(user_answer):
        st.session_state.answer_submitted = True
        st.session_state.user_answer = user_answer
        if user_answer == st.session_state.current_question['answer']:
            st.session_state.quiz_score += 1

    # --- Handle moving to the next question ---
    def next_question():
        st.session_state.questions_answered += 1
        if st.session_state.questions_answered >= QUIZ_LENGTH:
            st.session_state.quiz_finished = True
        else:
            select_new_question()

    # --- UI Logic ---
    if not st.session_state.quiz_started or st.session_state.quiz_finished:
        if st.session_state.quiz_finished:
            # --- Display final score and evaluation ---
            score = st.session_state.quiz_score
            total = QUIZ_LENGTH
            st.subheader(t[lang]['score_summary'].format(score=score, total=total))

            percentage = score / total
            if percentage >= 0.8: # 4-5 correct answers
                evaluation_text = t[lang]['eval_high']
                st.success(evaluation_text)
            elif percentage >= 0.5: # 2-3 correct answers
                evaluation_text = t[lang]['eval_medium']
                st.info(evaluation_text)
            else: # 0-1 correct answers
                evaluation_text = t[lang]['eval_low']
                st.warning(evaluation_text)
            
            st.caption(t[lang]['quiz_disclaimer'])
            st.divider()
        
        button_text = t[lang]['start_quiz'] if not st.session_state.quiz_finished else t[lang]['restart_quiz']
        st.button(button_text, on_click=start_quiz, use_container_width=True)

    else:
        # --- Display the current question ---
        q = st.session_state.current_question
        if q:
            st.subheader(f"{t[lang]['quiz_question_title']} ({st.session_state.questions_answered + 1}/{QUIZ_LENGTH})")
            st.write(q['question'])

            if not st.session_state.answer_submitted:
                col1, col2 = st.columns(2)
                with col1:
                    st.button(t[lang]['quiz_true'], on_click=handle_answer, args=(True,), use_container_width=True)
                with col2:
                    st.button(t[lang]['quiz_false'], on_click=handle_answer, args=(False,), use_container_width=True)
            else:
                # --- Display feedback after answer ---
                is_correct = (st.session_state.user_answer == q['answer'])
                if is_correct:
                    st.success(t[lang]['correct_feedback'])
                else:
                    st.error(t[lang]['incorrect_feedback'])

                st.markdown(q['explanation'])
                
                # --- Display Infographic ---
                if 'infographic_key' in q and q['infographic_key'] in t[lang]['infographics']:
                    st.divider()
                    st.subheader(t[lang]['infographic_title'])
                    info_data = t[lang]['infographics'][q['infographic_key']]
                    
                    # Using a more robust card-like structure for infographics
                    info_html = f"<div class='infographic-card'><h4>{info_data['title']}</h4><ul>"
                    for point in info_data['points']:
                        info_html += f"<li><span class='icon'>{point['icon']}</span> {point['text']}</li>"
                    info_html += "</ul></div>"
                    
                    st.markdown(info_html, unsafe_allow_html=True)
                
                st.divider()
                st.button(t[lang]['quiz_next_question'], on_click=next_question, use_container_width=True)

