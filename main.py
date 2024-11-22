import streamlit as st
from src.modules.about import DAD_About
from src.modules.common_schema import Common_Schema
from src.modules.cross_file_mapping import lookup_data
from src.modules.file_validation import file_validation

st.set_page_config(layout='wide')


def main():
    session_elements = ['current_page', 'mapping_type','prev_mapping_type']
    for each in session_elements:
        if each not in st.session_state:
            st.session_state[f'{each}'] = None
    if 'page_index_cs' not in st.session_state:
        st.session_state.page_index_cs = 0

    custom_css = """
        <style>
            section[data-testid="stSidebar"] * {
                color: white !important;
            }
        </style>
    """
    #: navigation bar to navigate to different modules of DAD
    st.markdown(custom_css, unsafe_allow_html=True)
    st.sidebar.title('Navigation')
    pages = st.sidebar.radio('Go To', ['About', 'Individual File Validation', 'Common-Schema', 'Cross-File Data Mapping'])
    st.session_state.current_page = pages
    if st.session_state.current_page == 'About':
        a1 = DAD_About()
        a1.About()
    elif st.session_state.current_page == 'Common-Schema':
        # Add radio button for mapping type selection
        st.sidebar.subheader("Mapping Type Selection")
        selected_mapping_type = st.sidebar.radio(
            'Select the Header Mapping Type:',
            ['Load Existing Mapping', 'Begin with New Mapping'],
            index=0
        )
        if st.session_state.prev_mapping_type != selected_mapping_type:
            st.session_state.page_index_cs = 0
            st.session_state.prev_mapping_type = selected_mapping_type

        # Update the mapping type in session state
        st.session_state.mapping_type = selected_mapping_type
        # Call the Common Schema navigation
        common_schema = Common_Schema()
        common_schema.common_schema_navigation()
    elif st.session_state.current_page == 'Cross-File Data Mapping':
        lookup_data()
    elif st.session_state.current_page == 'Individual File Validation':
        file_validation()


if __name__ == '__main__':
    main()
