import streamlit as st
import markdown

def display_knowledge_base(lang, t):
    """
    Displays the knowledge base section with filterable cards.
    Separated into its own module for better code organization.
    """
    # Add specific CSS to ensure Sarabun font is used for card titles and content.
    st.markdown("""
        <style>
            .knowledge-card h4, .knowledge-card p, .knowledge-card li, .knowledge-card strong {
                font-family: 'Sarabun', sans-serif !important;
            }
        </style>
    """, unsafe_allow_html=True)

    st.subheader(t[lang]['knowledge_header'])

    # Use session state to handle the selected category
    if 'selected_category' not in st.session_state:
        st.session_state.selected_category = 'all'

    # Create a function to update the session state.
    # This function now also sets the active_tab state to ensure
    # the correct tab remains visible after a button click.
    def set_category(cat):
        st.session_state.selected_category = cat
        st.session_state.active_tab = "เกร็ดความรู้" 

    # We use a key to make each button unique and properly handle the on_click callback
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
    
    st.write("")  # Add some space

    num_cols = 2 # Changed from 3 to 2 columns
    cols = st.columns(num_cols)
    col_index = 0

    for item in t[lang]['knowledge_content']:
        if st.session_state.selected_category == 'all' or item['category'] == st.session_state.selected_category:
            with cols[col_index]:
                st.markdown(f"""
                <div class="knowledge-card">
                    <h4>{item['title']}</h4>
                    <p>{markdown.markdown(item['body'], extensions=['nl2br'])}</p>
                </div>
                """, unsafe_allow_html=True)
                col_index = (col_index + 1) % num_cols

