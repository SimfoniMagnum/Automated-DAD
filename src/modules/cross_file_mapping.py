import pandas as pd
import streamlit as st
import polars as pl
import time


@st.dialog('No mapping provided', width='small')
def no_mapping_provided():
    st.error("All the fields are required!", icon='😭')


@st.dialog('Save Master File', width='small')
def save_file_dialog_box():
    file_name = st.text_input('Provide a file name tos save the data ')
    if file_name:
        with st.spinner('Please Wait'):
            master_df = pl.from_pandas(st.session_state.main_df)
            master_df.write_excel(f'{file_name}.xlsx')
            st.success('Master data Saved Successfully In Current Working Directory!', icon='😎')


@st.dialog('Data Mapping In Progress', width='small')
def map_details():
    main_key = st.session_state.mapping_config_key_main
    mapping_key = st.session_state.mapping_config_key_mapping
    if len(main_key) > 1:
        st.session_state.main_df['Concat'] = st.session_state.main_df[main_key].astype(str).agg(''.join, axis=1)
        main_key = ['Concat']
    elif isinstance(main_key, list) and len(main_key) == 1:
        main_key = main_key[0]
    if len(mapping_key) > 1:
        st.session_state.mapping_df['Concat'] = st.session_state.mapping_df[mapping_key].astype(str).agg(''.join,
                                                                                                         axis=1)
        mapping_key = ['Concat']
    elif isinstance(mapping_key, list) and len(mapping_key) == 1:
        mapping_key = mapping_key[0]
    for key in st.session_state.lookup_mapping_dict.keys():
        with st.spinner('Please Wait'):
            try:
                value = st.session_state.lookup_mapping_dict[key]
                if not pd.isna(value) and value is not None:
                    mapping_dict = st.session_state.mapping_df.set_index(mapping_key)[value].to_dict()
                    file_name = st.session_state.config_mapping_file_name
                    mask = st.session_state.main_df['File Name'].isin(file_name)
                    st.session_state.main_df.loc[mask, key] = st.session_state.main_df[main_key].map(mapping_dict.get)
                    st.success(f"{value} Mapped Successfully!", icon='😁')
                    time.sleep(2)
            except Exception as e:
                st.error(f"Error {e} Occured in mapping {key} skipping..")
                st.session_state.mapping_detail_status = False
    st.success('All Details Mapped Successfully.')
    st.session_state.mapped_details_status = True


def lookup_data_about():
    st.subheader(
        "Hi! This module of DAD helps you map multiple data from various mapping file based on unique keys from main file and mapping file")
    st.markdown("""<h4>Instructions:</h4 >""",
                unsafe_allow_html=True)

    # List of key features
    st.markdown("""
                    - **Selecting Data**: Select the Master File first. 
                    - **Provide Mapping File**: Select Mapping File.
                    - **File Name**: Select the file name from Master Data, correspondance to Mapping File.
                    - **Main Key**: Select the unique key from the Main File, based on which data can be mapped.
                    - **Mapping Key**: Select the unique key from the Mapping file.
                    - **Column Information**: Provide all the columns names which we want to map the data from the mapping file.
                    - **Save Data**: Once all the details are mapped, provide a file name and save the results.
                    """)
    st.write("Please Nagivate to Next Page to Begin the Conslidation Process😊")


def lookup_data_form():
    st.markdown("<h4>Provide the Master Data and Mapping File</h4>", unsafe_allow_html=True)
    main_file_path = st.file_uploader('Select the Master Invoice data', type=['XLSX', 'csv'])
    mapping_file_path = st.file_uploader("Select the Mapping File for invoice data", type=['XLSX', 'CSV'])

    if main_file_path and not st.session_state.master_file_load_status:
        if main_file_path.name.endswith('.xlsx'):
            try:
                main_df = pl.read_excel(main_file_path, infer_schema_length=0).to_pandas()
                st.session_state.main_df = main_df.copy()
                st.session_state.master_file_load_status = True

            except Exception as e:
                st.error(f'{e} Error Occured while opening the master data')
        elif main_file_path.name.endswith('.csv'):
            try:
                main_df = pl.read_csv(main_file_path, infer_schema_length=0).to_pandas()
                st.session_state.main_df = main_df.copy()
                st.session_state.master_file_load_status = True

            except Exception as e:
                st.error(f'{e} Error Occured while opening the master data')

    elif mapping_file_path and not st.session_state.mapping_file_load_status:
        if mapping_file_path.name.endswith('.xlsx'):
            try:
                mapping_df = pl.read_excel(mapping_file_path, infer_schema_length=0).to_pandas()
                st.session_state.mapping_df = mapping_df.copy()
                st.session_state.mapping_file_load_status = True

            except Exception as e:
                st.error(f'{e} Error Occured while opening the master data')
        elif mapping_file_path.name.endswith('.csv'):
            try:
                mapping_df = pl.read_csv(mapping_file_path, infer_schema_length=0).to_pandas()
                st.session_state.mapping_df = mapping_df.copy()
                st.session_state.mapping_file_load_status = True

            except Exception as e:
                st.error(f'{e} Error Occured while opening the master data')

    if not st.session_state.main_df.shape[0] == 0 and not st.session_state.mapping_df.shape[0] == 0:
        st.markdown("<h4>Provide the Mapping Details!</h4>", unsafe_allow_html=True)
        st.session_state.config_mapping_file_name = st.multiselect('Select the file Main from the Master file',
                                                                   options=list(
                                                                       st.session_state.main_df[
                                                                           'File Name'].unique()) + [
                                                                               'Select ALL'],
                                                                   placeholder='File Name',
                                                                   help='Select the file name of Invoice data for which you want to map the data from the mapping file.')
        st.session_state.mapping_config_key_main = st.multiselect(
            'Select the Mapping key(Main Key) from the Master file',
            options=list(st.session_state.main_df.columns),
            placeholder='Main Key from Master File',
            help='Column Name which can be used to map the data from the Mapping File.')

        st.session_state.mapping_config_key_mapping = st.multiselect(
            'Select the Mapping key(Mapping Key) from the Mapping file',
            options=list(st.session_state.mapping_df.columns),
            placeholder='Mapping Key from Mapping File',
            help='Column Name which can be used to Unique key from the Mapping File.')
        st.session_state.columns_to_map = st.multiselect(
            'Select the Column Names from the Master File whose Details you want to map',
            options=st.session_state.main_df.columns,
            placeholder='Columns to map')
    if st.session_state.mapping_config_key_main and st.session_state.mapping_config_key_mapping:
        if 'proceed_clicked' not in st.session_state:
            st.session_state.proceed_clicked = False

        if st.button("Show Form"):
            st.session_state.proceed_clicked = True

        if st.session_state.proceed_clicked:
            st.markdown("<h4>Select Columns to Map</h4>", unsafe_allow_html=True)
            cols = st.columns(2)
            with cols[0]:
                st.markdown("<h5><strong>Main File Headers<strong></h5>", unsafe_allow_html=True)
            with cols[1]:
                st.markdown("<h5><strong>Mapping File Headers<strong></h5>", unsafe_allow_html=True)
            for column in st.session_state.columns_to_map:
                if column not in st.session_state.lookup_mapping_dict.keys():
                    st.session_state.lookup_mapping_dict[column] = None
                col1 = st.columns(2)
                with col1[0]:
                    st.markdown(
                        f"""
                                        <div style="display: flex; align-items: center; border: 1px solid #ccc; 
                                                    background-color: #316F98;
                                                    margin-top: 30px;
                                                    color: #ffff;
                                                    padding: 5px; border-radius: 5px; height: 38px; text-align: center;">
                                            <strong>{column}</strong>
                                        </div>
                                        """,
                        unsafe_allow_html=True)
                select_box_custom_css = """
                            <style>
                                div[data-testid="stSelectbox"] * {
                                color: #ffff !important;
                                }
                                </style>   
                            """
                st.markdown(select_box_custom_css, unsafe_allow_html=True)
                with col1[1]:
                    mapping_column = st.selectbox(label=f"Column to map with {column} from mapping file",
                                                  options=st.session_state.mapping_df.columns,
                                                  index=None,
                                                  placeholder='Mapping column',
                                                  key=f"{column}_mapping_key",
                                                  label_visibility='hidden')

                    st.session_state.lookup_mapping_dict[column] = mapping_column
    if st.session_state.lookup_mapping_dict:
        cols = st.columns(3)
        with cols[0]:
            if st.button("Map the details",use_container_width = True):
                map_details()
        with cols[1]:
            if st.button('New Mapping File',use_container_width= True):
                st.session_state.mapping_file_load_status = False


def lookup_data():
    if 'lookup_mapping_dict' not in st.session_state:
        st.session_state.lookup_mapping_dict = {}
    if 'main_df' not in st.session_state:
        st.session_state.main_df = pd.DataFrame()
    if 'mapping_df' not in st.session_state:
        st.session_state.mapping_df = pd.DataFrame()
    if 'config_mapping_file_name' in st.session_state:
        st.session_state.config_mapping_file_name = None
    if 'mapping_config_key_main' not in st.session_state:
        st.session_state.mapping_config_key_main = None
    if 'mapping_config_key_mapping' not in st.session_state:
        st.session_state.mapping_config_key_mapping = None
    if 'columns_to_map' not in st.session_state:
        st.session_state.columns_to_map = None
    if 'mapped_details_status' not in st.session_state:
        st.session_state['mapped_details_status'] = False
    if 'master_file_load_status' not in st.session_state:
        st.session_state['master_file_load_status'] = False
    if 'mapping_file_load_status' not in st.session_state:
        st.session_state['mapping_file_load_status'] = False

    sub_pages = [lookup_data_about, lookup_data_form]
    if 'page_index_lookup' not in st.session_state:
        st.session_state.page_index_lookup = 0
    current_index = st.session_state.page_index_lookup
    sub_pages[current_index]()
    col1, col3, col2 = st.columns([6, 8, 6])
    with col1:
        if st.session_state.page_index_lookup != 0:
            print(st.session_state.page_index_lookup)
            if st.button('Previous', use_container_width=True) and st.session_state.page_index_lookup > 0:
                st.session_state.page_index_lookup -= 1
                st.rerun()

    with col2:
        if st.session_state.page_index_lookup == 1 and st.session_state.mapped_details_status:
            if st.button('Save Data In Excel', use_container_width=True):
                save_file_dialog_box()
        if st.session_state.page_index_lookup < len(sub_pages)-1:
            if st.button('Next',use_container_width = True):
                st.session_state.page_index_lookup += 1
                st.rerun()