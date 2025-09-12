import streamlit as st
import markdown

def display_knowledge_base(lang, t):
    """
    Displays the knowledge base section with filterable cards.
    Separated into its own module for better code organization.
    """
    st.subheader(t[lang]['knowledge_header'])

    # Use session state to handle the selected category
    if 'selected_category' not in st.session_state:
        st.session_state.selected_category = 'all'

    # Create a function to update the session state
    def set_category(cat):
        st.session_state.selected_category = cat
        st.rerun()

    # Create the buttons with a unique key and on_click handler
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.button(t[lang]['filter_all'], on_click=set_category, args=('all',), use_container_width=True, key='btn_all')
    with col2:
        st.button(t[lang]['filter_info'], on_click=set_category, args=('info',), use_container_width=True, key='btn_info')
    with col3:
        st.button(t[lang]['filter_danger'], on_click=set_category, args=('danger',), use_container_width=True, key='btn_danger')
    with col4:
        st.button(t[lang]['filter_prevention'], on_click=set_category, args=('prevention',), use_container_width=True, key='btn_prevention')
    with col5:
        st.button(t[lang]['filter_health'], on_click=set_category, args=('health',), use_container_width=True, key='btn_health')

    # Add custom CSS to style the active button
    active_button_style = f"""
    <style>
    div[data-testid="stButton"] > button[key="btn_{st.session_state.selected_category}"] {{
        background-color: #1e40af;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transform: translateY(-2px);
    }}
    </style>
    """
    st.markdown(active_button_style, unsafe_allow_html=True)

    # Display the filtered cards
    st.write("")  # Add some space

    num_cols = 3
    cols = st.columns(num_cols)
    col_index = 0

    for item in t[lang]['knowledge_content']:
        if st.session_state.selected_category == 'all' or item['category'] == st.session_state.selected_category:
            with cols[col_index]:
                # Use markdown to render the body content correctly
                st.markdown(f"<h4>{item['title']}</h4>", unsafe_allow_html=True)
                st.markdown(item['body'])
                col_index = (col_index + 1) % num_cols
