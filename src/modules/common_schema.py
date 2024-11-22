from src.components.reusable_components import FileUploader, ErrorDialog
import streamlit as st
import polars as pl
import pandas as pd
import time
from datetime import datetime

pd.set_option('display.max_columns', None)


@st.dialog('Data Mapping In Progress', width='small')
def map_details():
    main_key = st.session_state.mapping_config_key_main
    mapping_key = st.session_state.mapping_config_key_mapping
    if len(main_key) > 1:
        st.session_state.master_file['Concat'] = st.session_state.master_file[main_key].astype(str).agg(''.join, axis=1)
        main_key = ['Concat']
    elif isinstance(main_key, list) and len(main_key) == 1:
        main_key = main_key[0]
    if len(mapping_key) > 1:
        st.session_state.reference_file['Concat'] = st.session_state.reference_file[mapping_key].astype(str).agg(
            ''.join,
            axis=1)
        mapping_key = ['Concat']
    elif isinstance(mapping_key, list) and len(mapping_key) == 1:
        mapping_key = mapping_key[0]
    for key in st.session_state.lookup_mapping_dict.keys():
        with st.spinner('Please Wait'):
            try:
                value = st.session_state.lookup_mapping_dict[key]
                if not pd.isna(value) and value is not None:
                    mapping_dict = st.session_state.reference_file.set_index(mapping_key)[value].to_dict()
                    file_name = st.session_state.config_mapping_file_name
                    mask = st.session_state.master_file['File Name'].isin(file_name)
                    st.session_state.master_file.loc[mask, key] = st.session_state.master_file[main_key].map(
                        mapping_dict.get)
                    st.success(f"{value} Mapped Successfully!", icon='😁')
            except Exception as e:
                st.error(f"Error {e} Occured in mapping {key} skipping..")
                st.session_state.mapping_detail_status = False
    st.success('All Details Mapped Successfully.')
    st.session_state.mapped_details_status = True


@st.dialog('Reading Files', width='large')
def read_raw_data_common_schema_em():
    with st.spinner('Plese wait while we process.....'):
        for i, file_path in enumerate(st.session_state.raw_data_to_consolidate_path):
            st.session_state.file_info_dict[f'invoice_data_{i}'] = {}
            st.session_state.file_info_dict[f'invoice_data_{i}']['name'] = str(file_path.name).split(".")[0]
            if file_path.name.endswith('csv'):
                try:
                    df = pl.read_csv(file_path, infer_schema_length=0).to_pandas()
                    st.session_state.file_info_dict[f'invoice_data_{i}']['df'] = df
                    st.success(f"Read Successfully {file_path.name}....", icon='🎉')
                except Exception as e:
                    st.error(
                        f"Unexpected {e} Error Occured While Opening Invoice Data {str(file_path.name).split('.')[0]}")
                    st.session_state.file_load_status = False
            elif file_path.name.endswith('xlsx'):
                try:
                    df = pl.read_excel(file_path, infer_schema_length=0).to_pandas()
                    st.session_state.file_info_dict[f'invoice_data_{i}']['df'] = df
                    st.success(f"Read Successfully {file_path.name}....", icon='🎉')
                except Exception as e:
                    st.error(
                        f"Unexpected {e} Error Occured While Opening Invoice Data {str(file_path.name).split('.')[0]}")
                    st.session_state.file_load_status = False
        if st.session_state.mapping_file_path.name.endswith('csv'):
            try:
                st.session_state.mapping_df = pl.read_csv(st.session_state.mapping_file_path,
                                                          infer_schema_length=0).to_pandas()
                st.session_state.mapping_df.set_index('Unified Simfoni Headers', inplace=True)
                st.success(f"Header Mapping File Read Successfully ....", icon='🎉')
                st.session_state.file_load_status = True
            except Exception as e:
                st.error(f'{e} Error Occured While Opening Mapping File')
        elif st.session_state.mapping_file_path.name.endswith('xlsx'):
            try:
                st.session_state.mapping_df = pl.read_excel(st.session_state.mapping_file_path,
                                                            infer_schema_length=0).to_pandas()
                st.session_state.mapping_df.set_index('Unified Simfoni Headers', inplace=True)
                st.success(f"Header Mapping File Read Successfully ....", icon='🎉')
                st.session_state.file_load_status = True
            except Exception as e:
                st.error(f'{e} Error Occured While Opening Mapping File')


import streamlit as st
from datetime import datetime

@st.dialog("Saving File", width='large')
def save_master_file_excel():
    with st.spinner('Please wait while we save file....'):
        if "file_saved" not in st.session_state:
            try:
                time_str = datetime.now().strftime('%H-%M-%S-%f')
                filename = f'Master File {time_str}.xlsx'
                st.session_state.master_file.to_excel(filename, index=False)
                with open(filename, 'rb') as file:
                    file_data = file.read()
                st.session_state.file_saved = {
                    "filename": filename,
                    "data": file_data
                }
                st.success("Master File Saved Successfully", icon='🎊')
            except Exception as e:
                st.error(f"{e} Error Occurred")
                return
        if "file_saved" in st.session_state:
            st.download_button(
                label="Download Excel file",
                data=st.session_state.file_saved["data"],
                file_name=st.session_state.file_saved["filename"],
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )



@st.dialog('Create Master File', width='small')
def create_master_file():
    with st.spinner('Please Wait while we process this......'):
        try:
            columns = list(st.session_state.mapping_df.index)
            appended_df = []  # Initialize empty list for DataFrames
            files = list(st.session_state.mapping_df.columns)
            for i, file in enumerate(files):
                master_df = pd.DataFrame(columns=columns)
                df = st.session_state.file_info_dict[f'invoice_data_{i}']['df']
                for key in columns:
                    if key == 'File Name':
                        master_df[key] = [file] * len(df)
                    else:
                        value = st.session_state.mapping_df.loc[key][file]
                        if value != 'None' and value is not None and not pd.isna(value):
                            if value in df.columns:
                                master_df[key] = df[value].copy()
                appended_df.append(master_df)
            # Combine all DataFrames into a single DataFrame
            st.session_state.master_file = pd.concat(appended_df, ignore_index=True)
            st.success('Master File Created', icon='😁')
        except Exception as e:
            st.error(f'Unexpected{e} Error Occured while creating the master file!')


def create_master_file():
    try:
        columns = list(st.session_state.mapping_df.index)
        appended_df = pd.DataFrame(columns=columns)  # Initialize empty DataFrame for final result
        files = list(st.session_state.mapping_df.columns)
        for i, file in enumerate(files):
            master_df = pd.DataFrame(columns=columns)
            df = st.session_state.file_info_dict[f'invoice_data_{i}']['df']
            for key in columns:
                if key == 'File Name':
                    master_df[key] = [file] * len(df)  # Assign file name for the current DataFrame
                else:
                    value = st.session_state.mapping_df.loc[key][file]
                    if value != 'None' and value is not None and not pd.isna(value):
                        master_df[key] = df[value].copy()
            appended_df = pd.concat([appended_df, master_df], axis=0, ignore_index=True)
        st.session_state.master_file = appended_df.copy()
        st.success('Master File Created', icon='😁')
        st.session_state.master_file_creation_status = True
    except Exception as e:
        st.error(f"Sorry Unexpected {e} Error Occured in file {file}")


class Common_Schema:
    def __init__(self):
        # Initialize session state variables
        session_elements = ['raw_data_to_consolidate_path', 'mapping_file_path', 'mapping_type',
                            'master_file_creation_status', 'file_names', 'mapping_config_key_main',
                            'mapping_config_key_mapping']
        for each in session_elements:
            if each not in st.session_state:
                st.session_state[f'{each}'] = None
        boolean_session_elements = ['proceed_clicked', 'file_load_status', 'column_populated',
                                    'go_to_external_mapping', 'mapped_details_status',
                                    'proceed_clicked', 'mapping_file_validation_status']
        for each in boolean_session_elements:
            if each not in st.session_state:
                st.session_state[f'{each}'] = False
        if 'file_info_dict' not in st.session_state: st.session_state['file_info_dict'] = {}
        if 'mapping_df' not in st.session_state: st.session_state['mapping_df'] = pd.DataFrame()
        if 'mapping_file_not_found_columns' not in st.session_state: st.session_state[
            'mapping_file_not_found_columns'] = {}
        if 'lookup_mapping_dict' not in st.session_state: st.session_state['lookup_mapping_dict'] = {}
        if 'master_file' not in st.session_state: st.session_state['master_file'] = pd.DataFrame()
        if 'reference_file' not in st.session_state: st.session_state['reference_file'] = pd.DataFrame()
        if 'unified_header' not in st.session_state: st.session_state.unified_headers = [
            "SrNo",
            "ActualSrNo",
            "Data Source",
            "File Name",
            "Source System",
            "Entity Code",
            "Entity Name",
            "Entity City",
            "Entity State",
            "Entity Country",
            "Entity Region",
            "Document Number",
            "Document Line Number",
            "Document Date",
            "Document Header Description",
            "Document Line Description",
            "Buyer Name",
            "Payment Terms Code",
            "Payment Terms Description",
            "Supplier Document Number",
            "Supplier Code",
            "Supplier Name",
            "Supplier Name (Normalized)",
            "Supplier City",
            "Supplier State",
            "Supplier Country",
            "Supplier Region",
            "Supplier Tax ID",
            "Document Unit price",
            "Document Quantity",
            "Document UOM",
            "Document Currency",
            "Amount in Document Currency",
            "FX Rate",
            "Spend",
            "Cost Center Code",
            "Cost Center Description",
            "General Ledger Code",
            "General Ledger Description",
            "Material Code",
            "Material Description",
            "Material Group Code",
            "Material Group Description",
            "Contract Flag",
            "Intercompany Flag",
            "Scope",
            "Supplier Commonality",
            "Supplier Group",
            "Invoice Group",
            "Transaction Group",
            "Addressability Flag",
            "Category Level 0",
            "Category Level 1",
            "Category Level 2",
            "Category Level 3",
            "Category Level 4",
            "Category Level 5",
            "Category Level 6",
            "Employee Last Name",
            "cl_qa_flag",
            "cl_training_set_flag",
            "cl_cluster_id",
            "source_name",
            "custom_field1",
            "custom_field2",
            "custom_field3",
            "custom_field4",
            "custom_field5",
            "QA flag",
            "Posted Date",
            "Sent for Payment Date",
            "Detail",
            "Batch ID",
            "Sequence",
            "Employee ID",
            "Employee First Name",
            "Expense Group ID",
            "Operating Department Code",
            "Company Name",
            "Company Code",
            "Division/Branch Name",
            "Division/Branch Code",
            "Department Name",
            "Department Code",
            "Report Name",
            "Total Approved Amount",
            "Reimbursement Currency",
            "Payment Type",
            "Project #",
            "Name on Card",
            "Last Four Account Digits",
            "Merchant Code",
            "Transaction Date"
        ]

    @staticmethod
    def common_schema_navigation():
        # Define page sequences based on mapping type
        existing_mapping = [Common_Schema.about, Common_Schema_Existing_Mapping.file_uploader_em,
                            Common_Schema_Existing_Mapping.read_file_validate_mapping,
                            Common_Schema_Existing_Mapping.external_file_data_mapping_about,
                            Common_Schema_Existing_Mapping.external_file_data_mapping]
        new_mapping = [Common_Schema.about, Common_Schema_New_Mapping.file_uploader_nm,
                       Common_Schema_New_Mapping.header_mapping_mappable,
                       Common_Schema_New_Mapping.header_mapping_userdefined_headers,
                       Common_Schema_New_Mapping.header_mapping_autocreate,
                       Common_Schema_Existing_Mapping.external_file_data_mapping_about,
                       Common_Schema_Existing_Mapping.external_file_data_mapping]

        mapping_type = st.session_state.mapping_type
        if mapping_type == 'Load Existing Mapping':
            pages = existing_mapping
        elif mapping_type == 'Begin with New Mapping':
            pages = new_mapping
        else:
            st.warning("Please select a mapping type.")
            return
        # Get the current page index
        current_page = st.session_state.page_index_cs
        # Render the current page
        pages[current_page]()
        # Navigation buttons
        cols = st.columns(4)
        #: back button
        with cols[0]:
            if st.session_state.page_index_cs != 0:
                if st.button("Back", use_container_width=True) and st.session_state.page_index_cs > 0:
                    st.session_state.page_index_cs -= 1
                    st.rerun()
        #: creating the navigation for existing mapping!
        if mapping_type == 'Load Existing Mapping':
            if st.session_state.page_index_cs == 0 and cols[3].button('Begin with Existing Mapping',
                                                                      use_container_width=True):
                st.session_state.page_index_cs += 1
                st.rerun()
            elif st.session_state.page_index_cs == 1:
                if cols[3].button("Read All Files", use_container_width=True):
                    if len(st.session_state.raw_data_to_consolidate_path) == 0 or st.session_state.mapping_file_path is None:
                        ErrorDialog.show_warning("Provide all the Necessary File!")
                    else:
                        st.session_state.page_index_cs += 1
                        st.rerun()
            elif st.session_state.page_index_cs == 2:
                if st.session_state['go_to_external_mapping']:
                    if cols[3].button('External File Map Details', use_container_width=True):
                        st.session_state.page_index_cs += 1
                        st.rerun()
                else:
                    if cols[3].button('Save Master File to Excel', use_container_width=True):
                        save_master_file_excel()
            elif st.session_state.page_index_cs == 3:
                if cols[3].button("Proceed", use_container_width=True):
                    st.session_state.page_index_cs += 1
                    st.rerun()
            elif st.session_state.page_index_cs == 4:
                if cols[3].button("Export Master File To Excel", use_container_width=True):
                    save_master_file_excel()

        #: creating the navigation for the new mapping
        elif mapping_type == 'Begin with New Mapping':
            if st.session_state.page_index_cs == 0:
                if cols[3].button('Proceed', use_container_width=True) and st.session_state.page_index_cs < len(
                        pages) - 1:
                    st.session_state.page_index_cs += 1
                    st.rerun()
            elif st.session_state.page_index_cs == 1:
                if cols[3].button('Create Header Mapping',
                                  use_container_width=True):
                    if len(st.session_state.raw_data_to_consolidate_path) == 0:
                        ErrorDialog.show_warning("No Raw File to Consolidate!")
                    else:
                        print(f"Incrementing page index from {st.session_state.page_index_cs}")
                        st.session_state.page_index_cs += 1
                        st.rerun()  # only rerun after the button click
            elif st.session_state.page_index_cs == 2:
                if cols[3].button("Create User-defined Header", use_container_width=True):
                    st.session_state.page_index_cs += 1
                    st.rerun()
            elif st.session_state.page_index_cs == 3:
                if cols[3].button('Auto-create UnMapped Headers', use_container_width=True):
                    st.session_state.page_index_cs += 1
                    st.rerun()
            elif st.session_state.page_index_cs == 4:
                if st.session_state['go_to_external_mapping']:
                    if cols[3].button('External File Map Details', use_container_width=True):
                        st.session_state.page_index_cs += 1
                        st.rerun()
                else:
                    if cols[3].button('Save Master File to Excel', use_container_width=True):
                        save_master_file_excel()
            elif st.session_state.page_index_cs == 5:
                if cols[3].button('Proceed', use_container_width=True):
                    st.session_state.page_index_cs += 1
                    st.rerun()
            elif st.session_state.page_index_cs == 6:
                if cols[3].button('Save file to Excel', use_container_width=True):
                    save_master_file_excel()

    @staticmethod
    def about():
        st.subheader(
            "Hi! We Help You Consolidate data from multiple businesses Of Client to a Unified Simfoni Format, "
            "providing you more transparency and control over data."
        )
        st.markdown("""<h4>Key Features of Data Consolidation and Assessment Automation</h4>""",
                    unsafe_allow_html=True)

        # List of key features
        st.markdown("""
            - **Multiple File Upload**: Clients and analysts can upload multiple files, including multiple raw/base invoice data.
            - **Master File Creation**: Using automation scripts, the module consolidates data from various sources into a single master file by mapping headers of raw/data to Unified Headers.
            - **Userdefined Column For Unmapped Headers**: In case client or analyst want to create a user-defined header for unmapped headers, they can do it as step 2.
            - **Automated Header Creation for Unmapped Raw Headers**: At the last step, where we are left with few unmapped headers, we create Automated Header for those headers, same as raw header.
        """)
        st.write("Please begin the consolidation by selecting the Mapping Type! 😊")


class Common_Schema_Existing_Mapping:
    @staticmethod
    def file_uploader_em():
        st.session_state['file_load_status'] = False
        st.session_state['mapping_file_validation_status'] = False
        st.session_state['master_file_creation_status'] = False
        st.session_state['column_populated'] = True
        st.subheader("Provide the Existing Header Mapping File and Raw Data to Consolidate")
        file_uploader = FileUploader(
            label='Select all the Raw Data which you want to consolidate',
            multiple_files=True,
            file_types=['xlsx', 'csv']
        )
        st.session_state['raw_data_to_consolidate_path'] = file_uploader.render()
        file_uploader = FileUploader(
            label='Select the Existing Header Mapping file',
            multiple_files=False,
            file_types=['xlsx', 'csv']
        )
        st.session_state['mapping_file_path'] = file_uploader.render()
        st.session_state['file_names'] = [file.name.split('.')[0] for file in
                                          st.session_state['raw_data_to_consolidate_path']]

    @staticmethod
    def read_file_validate_mapping():
        st.subheader("Validate and Process Mapping Files with Raw Data Integration")
        if not st.session_state['file_load_status']:
            read_raw_data_common_schema_em()
            st.session_state['mapping_file_validation_status'] = True
            with st.status('Validating Mapping File'):
                for key, value in st.session_state.file_info_dict.items():
                    file_name = value['name']
                    raw_file_columns = value['df'].columns
                    st.session_state.mapping_file_not_found_columns[file_name] = []
                    mapping_file_columns = list(st.session_state.mapping_df[file_name].unique())
                    for column in mapping_file_columns:
                        if column is not None and column not in raw_file_columns:
                            st.session_state.mapping_file_not_found_columns[file_name].append(column)
                            st.session_state.mapping_file_validation_status = False
                if st.session_state.mapping_file_validation_status:
                    st.write('Mapping File Validation Succeeded!')
                    st.write('Creating the Master file, please wait......')
                    create_master_file()
                else:
                    st.warning("Sorry Can't Proceed with selected Mapping file, following column not found.")
                    st.write(st.session_state.mapping_file_not_found_columns)
        if st.session_state.master_file_creation_status:
            calculated_columns = st.multiselect('Select the Details which you want to populate',
                                                options=['SrNo', 'ActualSrNo', 'Spend'])
            if 'Spend' in calculated_columns:
                file_uploader = FileUploader(
                    label='Select the FX Rate file',
                    multiple_files=False,
                    file_types=['xlsx']
                )
                fx_rate_file_path = file_uploader.render()
                if fx_rate_file_path:
                    fx_rate_file = pl.read_excel(fx_rate_file_path, infer_schema_length=0).to_pandas()
                    fx_rate_file['Date'] = pd.to_datetime(fx_rate_file['Date'])

                file_name = st.multiselect("Select the file name for you want to calculate the Spend",
                                           options=st.session_state['master_file']['File Name'].unique(),
                                           placeholder='File Name')
                date_format = st.selectbox("Select the Data format",
                                           options=["%Y-%m-%d",
                                                    "%Y-%d-%m",
                                                    "%m-%d-%Y",
                                                    "%m-%Y-%d",
                                                    "%d-%m-%Y",
                                                    "%d-%Y-%m"], index=None, placeholder='Date format')
            columns_populated = False
            columns = st.columns(3)
            with columns[0]:
                if calculated_columns:
                    if st.button("Populate Columns"):
                        try:
                            total_tranasctions = st.session_state.master_file.shape[0]
                            st.session_state.master_file['SrNo'] = [i + 1 for i in range(total_tranasctions)]
                            st.session_state.master_file['ActualSrNo'] = [i + 1 for i in range(total_tranasctions)]
                            if 'Spend' in calculated_columns:
                                if date_format:
                                    try:
                                        mask = st.session_state.master_file['File Name'].isin(file_name)
                                        #: removing the time stamp from the date
                                        st.session_state.master_file['Document Date'] = st.session_state.master_file[
                                            'Document Date'].apply(lambda x: str(x).replace(' 00:00:00', ''))
                                        #: converting the date column to date format
                                        st.session_state.master_file['Document Date'] = pd.to_datetime(
                                            st.session_state.master_file['Document Date'], format=date_format)
                                        #: creatting a unique key based on document date and document currency
                                        print(st.session_state.master_file['Document Date'].dtypes)
                                        st.session_state.master_file.loc[mask, 'Concat'] = (
                                                                                                   st.session_state.master_file.loc[
                                                                                                       mask, 'Document Date'] - pd.to_datetime(
                                                                                               '1900-01-01')).dt.days.astype(
                                            str) + st.session_state.master_file.loc[mask, 'Document Currency']
                                        #: cereating thje unique key in fx rate file
                                        fx_rate_file['Concat'] = (fx_rate_file['Date'] - pd.to_datetime(
                                            '1900-01-01')).dt.days.astype(str) + fx_rate_file['Currency']
                                        #: calculating the spend
                                        st.session_state.master_file.loc[mask, 'FX Rate'] = \
                                            st.session_state.master_file.loc[mask, 'Concat'].map(
                                                fx_rate_file.set_index("Concat")['Conversion Rate'])
                                        #: Mapping the conversion rate in th master file
                                        st.session_state.master_file.loc[mask, 'Spend'] = \
                                            st.session_state.master_file.loc[mask, 'FX Rate'].astype(
                                                float) * st.session_state.master_file.loc[
                                                mask, 'Amount in Document Currency'].astype(
                                                float)
                                        st.toast(f'{calculated_columns} has Been Calculated successfully', icon='🎊')
                                        st.session_state.master_file.drop(columns='Concat', inplace=True)
                                        st.session_state.column_populated = False
                                    except Exception as e:
                                        st.error(f"Invalid Date Format Provided! {e} Error Occured")
                                else:
                                    st.warning("Please provide the Date Format First")
                            st.toast(f'{calculated_columns} Populaed In Master File', icon='🎊')
                            st.session_state.column_populated = True
                        except Exception as e:
                            st.error(f"Unexpected {e} Error Occured While Populating the Fields")
            if st.button("Show Sample Data"):
                st.dataframe(st.session_state.master_file.sample(10))

            if st.session_state.column_populated:
                next_stage = st.radio('Select the Next Step', ['External File Data Mapping', 'Save File to Excel'],
                                      index=None)
                if next_stage == 'External File Data Mapping':
                    st.session_state['go_to_external_mapping'] = True
                elif next_stage == 'Save File to Excel':
                    st.session_state['go_to_external_mapping'] = False

    @staticmethod
    def external_file_data_mapping_about():
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

    @staticmethod
    def external_file_data_mapping():
        st.subheader("Fetch Data From External File Based on Primary Key!.")
        file_uploader = FileUploader(
            label='Provide the External Reference File',
            multiple_files=False,
            file_types=['xlsx', 'csv']
        )
        #: reading the external reference file for data mapping
        external_reference_file_path = file_uploader.render()
        if external_reference_file_path and external_reference_file_path.name.endswith('xlsx'):
            st.session_state['reference_file'] = pl.read_excel(external_reference_file_path,
                                                               infer_schema_length=0).to_pandas()
            st.session_state.config_mapping_file_name = st.multiselect('Select the file Main from the Master file',
                                                                       options=list(
                                                                           st.session_state.master_file[
                                                                               'File Name'].unique()) + [
                                                                                   'Select ALL'],
                                                                       placeholder='File Name',
                                                                       help='Select the file name of Invoice data for which you want to map the data from the mapping file.')
            st.session_state.mapping_config_key_main = st.multiselect(
                'Select the Mapping key(Main Key) from the Master file',
                options=list(st.session_state.master_file.columns),
                placeholder='Main Key from Master File',
                help='Column Name which can be used to map the data from the Main File.')

            st.session_state.mapping_config_key_mapping = st.multiselect(
                'Select the Mapping key(Mapping Key) from the Mapping file',
                options=list(st.session_state.reference_file.columns),
                placeholder='Mapping Key from Mapping File',
                help='Column Name which can be used to Unique key from the Mapping File.')
            st.session_state.columns_to_map = st.multiselect(
                'Select the Column Names from the Master File whose Details you want to map',
                options=st.session_state.master_file.columns,
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
                                                                background-color: #009C9C;
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
                                                      options=st.session_state.reference_file.columns,
                                                      index=None,
                                                      placeholder='Mapping column',
                                                      key=f"{column}_mapping_key",
                                                      label_visibility='hidden')

                        st.session_state.lookup_mapping_dict[column] = mapping_column
        if st.session_state.lookup_mapping_dict:
            cols = st.columns(3)
            with cols[0]:
                if st.button("Map the details", use_container_width=True):
                    map_details()
            with cols[1]:
                if st.button('New Mapping File', use_container_width=True):
                    st.session_state.mapping_file_load_status = False
        if st.button("Show DataFrame"):
            st.dataframe(st.session_state.master_file.sample(10))

class Common_Schema_New_Mapping:
    def __init__(self):
        pass

    @staticmethod
    def file_uploader_nm():
        st.subheader('Select the Raw Data which you want to Consolidate!')
        file_uploader = FileUploader(
            label='Select all the Raw Data which you want to consolidate',
            multiple_files=True,
            file_types=['xlsx', 'csv']
        )
        st.session_state['raw_data_to_consolidate_path'] = file_uploader.render()
        st.session_state.file_names = [str(file.name).split(".")[0] for file in
                                       st.session_state.raw_data_to_consolidate_path]
        st.session_state.mapping_df = pd.DataFrame(columns=st.session_state.file_names,
                                                   index=st.session_state.unified_headers)
        st.session_state.mapping_df.index.name = 'Unified Simfoni Headers'

    @staticmethod
    def header_mapping_mappable():
        st.subheader(
            "Hi! As second step of Consolidation we will be mapping the headers of raw invoice data to Unified Simfoni Headers.")
        if not st.session_state.file_load_status:
            with st.spinner('Please wait while we process.....'):
                for i, file_path in enumerate(st.session_state.raw_data_to_consolidate_path):
                    st.session_state.file_info_dict[f'invoice_data_{i}'] = {}
                    st.session_state.file_info_dict[f'invoice_data_{i}']['name'] = str(file_path.name).split(".")[0]
                    if file_path.name.endswith('csv'):
                        try:
                            df = pl.read_csv(file_path, infer_schema_length=0).to_pandas()
                            st.session_state.file_info_dict[f'invoice_data_{i}']['df'] = df
                            st.success(f"Read Successfully {file_path.name}....", icon='🎉')
                            st.session_state.file_load_status = True
                        except Exception as e:
                            st.error(
                                f"Unexpected {e} Error Occured While Opening Invoice Data {str(file_path.name).split('.')[0]}")
                            st.session_state.file_load_status = False
                    elif file_path.name.endswith('xlsx'):
                        try:
                            df = pl.read_excel(file_path, infer_schema_length=0).to_pandas()
                            st.session_state.file_info_dict[f'invoice_data_{i}']['df'] = df
                            st.success(f"Read Successfully {file_path.name}....", icon='🎉')
                            st.session_state.file_load_status = True
                        except Exception as e:
                            st.error(
                                f"Unexpected {e} Error Occured While Opening Invoice Data {str(file_path.name).split('.')[0]}")
                            st.session_state.file_load_status = False
        # begin header mapping when the file is loaded!..
        if st.session_state.file_load_status:
            #: creating columns for header mapping, one extra column for showing the unified headers.
            cols = st.columns(len(st.session_state.file_info_dict) + 1)
            with cols[0]:
                st.write("**Simfoni Unified Headers**")
            for idx, (key, value) in enumerate(st.session_state.file_info_dict.items(), start=1):
                with cols[idx]:
                    st.write(f"**{value['name']}**")
            #: creating a column headers, ie simfoni headers, and files names on top of each column names!
            for column in st.session_state.mapping_df.index:
                cols = st.columns(len(st.session_state.file_info_dict) + 1)

                with cols[0]:
                    #: unified header custom css
                    st.markdown(
                        f"""
                                    <div style="display: flex; align-items: center; border: 1px solid #ccc; 
                                                background-color: #009C9C;
                                                margin-top: 30px;
                                                color: #ffff;
                                                padding: 5px; border-radius: 5px; height: 38px; text-align: center;">
                                        <strong>{column}</strong>
                                    </div>
                                    """,
                        unsafe_allow_html=True
                    )
                    #: select box custom css
                select_box_custom_css = """
                            <style>
                                div[data-testid="stSelectbox"] * {
                                color: #ffff !important;
                                }
                                </style>   
                            """
                # Inject custom CSS
                st.markdown(select_box_custom_css, unsafe_allow_html=True)
                #: iterating over each raw invoice data df which is stored inside the file into dict.
                for idx, (key, value) in enumerate(st.session_state.file_info_dict.items(), start=1):
                    with (cols[idx]):
                        options = value['df'].columns.tolist() + [None]
                        #: check if it's not mapped with any column yet.
                        mapped_column = st.session_state.mapping_df.loc[column, value['name']]
                        if pd.isna(mapped_column) or mapped_column is None or mapped_column not in options:
                            default_index = options.index(None)

                        else:
                            default_index = options.index(mapped_column)
                        if column != 'File Name':
                            #: creating a select-box for selecting the mapping columns from each file:
                            choice = st.selectbox(
                                label='',
                                options=options,
                                index=default_index,
                                key=f"{column}_{value['name']}_select",
                                label_visibility="hidden"
                            )
                            #: saving the mapping column in mapping df:
                            st.session_state.mapping_df.loc[column, value['name']] = choice
                        #: mapping for the file name header:
                        else:
                            choice = st.selectbox(
                                label="",
                                options=st.session_state.file_names,
                                index=None,
                                key=f"{column}_{value['name']}_select",
                                placeholder=f"Select file for '{column}'",
                                label_visibility="hidden"
                            )
                            #: saving the mapping in the mapping df:
                            st.session_state.mapping_df.loc[column, value['name']] = choice

    @staticmethod
    def header_mapping_userdefined_headers():
        if 'autocreate_header_dict' not in st.session_state:
            st.session_state.autocreate_header_dict = {}
        else:
            st.session_state.autocreate_header_dict = {}
        unmapped_dict = {}
        st.subheader("Creating Analyst or Client defined column name for unmapped headers")
        #: iterating over all the columns of each invoice data and storing all the column names which are not in mapping df,
        #: from each file we saved the unmapped headers/column names inside the unmapped_dict
        for key, value in st.session_state.file_info_dict.items():
            raw_data_columns = value['df'].columns
            mapping_df_columns = list(st.session_state.mapping_df[value['name']].unique())
            unmapped_dict[f'{value["name"]}'] = []
            #: iterating over each columns of raw headers and saving it in other dict if they are not found in mapping df
            for column in raw_data_columns:
                if column not in mapping_df_columns:
                    unmapped_dict[f'{value["name"]}'].append(column)
        st.markdown("""<h5>Following are the unmapped header details.</h5>""", unsafe_allow_html=True)
        st.write(unmapped_dict)
        st.markdown("""<h5>Provide New Column Header Name For Unmapped columns.</h5>""", unsafe_allow_html=True)
        user_defined_column_names = st.text_input('Provide Column Name for Unmapped headers', value=None)
        if user_defined_column_names is not None:
            user_defined_column_names = [each.strip() for each in user_defined_column_names.split(",")]
            #: header for the columns
            headers = st.columns(len(st.session_state.file_info_dict) + 1)
            with headers[0]:
                st.write("**Simfoni Unified Headers**")

            for idx, (key, value) in enumerate(st.session_state.file_info_dict.items(), start=1):
                with headers[idx]:
                    st.write(f"**{value['name']}**")
            #: iterating each custom column and  creating select-boxes!
            for column in user_defined_column_names:
                cols = st.columns(len(st.session_state.file_info_dict) + 1)
                with cols[0]:
                    #: unified header custom css
                    st.markdown(
                        f"""
                        <div style="display: flex; align-items: center; border: 1px solid #ccc; 
                                    background-color: #009C9C;
                                    margin-top: 30px;
                                    color: #ffff;
                                    padding: 5px; border-radius: 5px; height: 38px; text-align: center;">
                            <strong>{column}</strong>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    #: select box custom css
                select_box_custom_css = """
                <style>
                    div[data-testid="stSelectbox"] * {
                    color: #ffff !important;
                    }
                    </style>   
                """
                # Inject custom CSS
                st.markdown(select_box_custom_css, unsafe_allow_html=True)
                #: iterating over each raw invoice data df which is stored inside the file into dict.
                for idx, (key, value) in enumerate(st.session_state.file_info_dict.items(), start=1):
                    #: list of columns invoice data have
                    options = value['df'].columns.tolist() + [None]
                    #: creating a custom header inside the mapping df
                    if column not in st.session_state.mapping_df.index:
                        st.session_state.mapping_df.loc[column, f'{value["name"]}'] = None
                    mapped_column = st.session_state.mapping_df.loc[column, f"{value['name']}"]
                    if pd.isna(mapped_column) or mapped_column is None:
                        default_index = options.index(None)
                    else:
                        default_index = options.index(mapped_column)
                    with (cols[idx]):
                        choice = st.selectbox(
                            label='Select',
                            options=options,
                            index=default_index,
                            key=f"{column}_{value['name']}_select",
                            label_visibility="hidden"
                        )
                        st.session_state.mapping_df.loc[column, f'{value["name"]}'] = choice

    @staticmethod
    def header_mapping_autocreate():
        #: this dictonery will save the unmapped headers, file name wise
        if 'autocreate_header_dict' not in st.session_state:
            st.session_state.autocreate_header_dict = {}
        st.subheader('In this last step, we can create header same as Raw Header which are still unmapped.')
        unmapped_dict = {}
        for key, value in st.session_state.file_info_dict.items():
            unmapped_dict[f'{value["name"]}'] = []
            raw_data_headers = list(value['df'].columns)
            mapped_headers = list(st.session_state.mapping_df[value['name']])
            for column in raw_data_headers:
                if column not in mapped_headers:
                    unmapped_dict[f'{value["name"]}'].append(column)
        st.markdown("<h5>Following are the list of unmapped Headers</h5>", unsafe_allow_html=True)
        st.write(unmapped_dict)
        st.markdown("<h5>Select Header For Appending at end of Master File.</h5>", unsafe_allow_html=True)
        for each in unmapped_dict:
            st.session_state.autocreate_header_dict[each] = []
            option = st.multiselect(
                f'Select the Column from {each} for Appending at end', options=unmapped_dict[each] + ['Select-All'])
            if 'Select-All' in option:
                st.session_state.autocreate_header_dict[each] = unmapped_dict[each]
            else:
                st.session_state.autocreate_header_dict[each] = option
        columns = st.columns(4)
        if not st.session_state.master_file_creation_status:
            if columns[0].button('Create Master File', use_container_width=True):
                create_master_file()

        if st.session_state.master_file_creation_status:
            st.markdown('<h5>Populating the Calculated Fields..</h5>', unsafe_allow_html=True)
            calculated_columns = st.multiselect('Select the Details which you want to populate',
                                                options=['SrNo', 'ActualSrNo', 'Spend'])
            if 'Spend' in calculated_columns:
                file_uploader = FileUploader(
                    label='Select the FX Rate file',
                    multiple_files=False,
                    file_types=['xlsx']
                )
                fx_rate_file_path = file_uploader.render()
                if fx_rate_file_path:
                    fx_rate_file = pl.read_excel(fx_rate_file_path, infer_schema_length=0).to_pandas()
                    fx_rate_file['Date'] = pd.to_datetime(fx_rate_file['Date'])

                file_name = st.multiselect("Select the file name for you want to calculate the Spend",
                                           options=st.session_state['master_file']['File Name'].unique(),
                                           placeholder='File Name')
                date_format = st.selectbox("Select the Data format",
                                           options=["%Y-%m-%d",
                                                    "%Y-%d-%m",
                                                    "%m-%d-%Y",
                                                    "%m-%Y-%d",
                                                    "%d-%m-%Y",
                                                    "%d-%Y-%m"], index=None, placeholder='Date format')
            columns_populated = False
            columns = st.columns(3)
            with columns[0]:
                if calculated_columns:
                    if st.button("Populate Columns"):
                        try:
                            total_tranasctions = st.session_state.master_file.shape[0]
                            st.session_state.master_file['SrNo'] = [i + 1 for i in range(total_tranasctions)]
                            st.session_state.master_file['ActualSrNo'] = [i + 1 for i in range(total_tranasctions)]
                            if 'Spend' in calculated_columns:
                                if date_format:
                                    try:
                                        mask = st.session_state.master_file['File Name'].isin(file_name)
                                        #: removing the time stamp from the date
                                        st.session_state.master_file['Document Date'] = st.session_state.master_file[
                                            'Document Date'].apply(lambda x: str(x).replace(' 00:00:00', ''))
                                        #: converting the date column to date format
                                        st.session_state.master_file['Document Date'] = pd.to_datetime(
                                            st.session_state.master_file['Document Date'], format=date_format)
                                        #: creatting a unique key based on document date and document currency
                                        print(st.session_state.master_file['Document Date'].dtypes)
                                        st.session_state.master_file.loc[mask, 'Concat'] = (
                                                                                                   st.session_state.master_file.loc[
                                                                                                       mask, 'Document Date'] - pd.to_datetime(
                                                                                               '1900-01-01')).dt.days.astype(
                                            str) + st.session_state.master_file.loc[mask, 'Document Currency']
                                        #: cereating thje unique key in fx rate file
                                        fx_rate_file['Concat'] = (fx_rate_file['Date'] - pd.to_datetime(
                                            '1900-01-01')).dt.days.astype(str) + fx_rate_file['Currency']
                                        #: calculating the spend
                                        st.session_state.master_file.loc[mask, 'FX Rate'] = \
                                            st.session_state.master_file.loc[mask, 'Concat'].map(
                                                fx_rate_file.set_index("Concat")['Conversion Rate'])
                                        #: Mapping the conversion rate in th master file
                                        st.session_state.master_file.loc[mask, 'Spend'] = \
                                            st.session_state.master_file.loc[mask, 'FX Rate'].astype(
                                                float) * st.session_state.master_file.loc[
                                                mask, 'Amount in Document Currency'].astype(
                                                float)
                                        st.toast(f'{calculated_columns} has Been Calculated successfully', icon='🎊')
                                        st.session_state.master_file.drop(columns='Concat', inplace=True)
                                        st.session_state.column_populated = False
                                    except Exception as e:
                                        st.error(f"Invalid Date Format Provided! {e} Error Occured")
                                else:
                                    st.warning("Please provide the Date Format First")
                            st.toast(f'{calculated_columns} Populaed In Master File', icon='🎊')
                            st.session_state.column_populated = True
                        except Exception as e:
                            st.error(f"Unexpected {e} Error Occured While Populating the Fields")
            if st.button("Show Sample Data"):
                st.dataframe(st.session_state.master_file.sample(10))

            next_stage = st.radio('Select the Next Step', ['External File Data Mapping', 'Save File to Excel'],
                                  index=None)
            if next_stage == 'External File Data Mapping':
                st.session_state['go_to_external_mapping'] = True
            elif next_stage == 'Save File to Excel':
                st.session_state['go_to_external_mapping'] = False
