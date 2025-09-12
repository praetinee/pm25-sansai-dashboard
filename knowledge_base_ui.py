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
    # This part of the code is not needed as the Streamlit button widget
    # handles the active state automatically. The button 'key' is sufficient
    # to maintain state. We will remove this for a cleaner solution.

    # Display the filtered cards
    st.write("")  # Add some space

    num_cols = 3
    cols = st.columns(num_cols)
    col_index = 0

    for item in t[lang]['knowledge_content']:
        if st.session_state.selected_category == 'all' or item['category'] == st.session_state.selected_category:
            with cols[col_index]:
                # Use markdown.markdown() to render the Markdown syntax correctly
                card_body_html = markdown.markdown(item['body'])
                
                st.markdown(f"""
                <div class="knowledge-card">
                    <h4>{item['title']}</h4>
                    {card_body_html}
                </div>
                """, unsafe_allow_html=True)
                col_index = (col_index + 1) % num_cols
