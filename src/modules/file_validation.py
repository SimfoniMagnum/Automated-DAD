import streamlit as st
import polars as pl
import pandas as pd
import time
import re


@st.dialog('Loading File')
def load_file():
    with st.spinner('Reading the file...'):
        time.sleep(2)  # Reduced wait time for testing
        df = None
        file_path = st.session_state.invoice_file_path_to_validate
        file_name = file_path.name
        # Check file type and load accordingly
        try:
            if file_name.endswith('xlsx'):
                st.session_state.validation_df = pl.read_excel(file_path, infer_schema_length=0).to_pandas()
                st.success('File Read Successfully.')
            elif file_name.endswith('csv'):
                st.session_state.validation_df = pl.read_csv(file_path, infer_schema_length=0).to_pandas()
                st.success('File Read Successfully.')
            else:
                st.error("Unsupported file format! Please upload an Excel or CSV file.")
                return
            # Success message and update session state
            st.toast(f"{file_name} loaded successfully!", icon='🎉')
            st.session_state.file_load_status = True
        except Exception as e:
            st.error(f"Error: {e}. Unable to open the file.")
            st.session_state.file_load_status = False
            return


@st.dialog('Alert!')
def no_file_provided(message):
    st.error(f'{message}', icon='😭')


def validation_analysis_result():
    st.subheader(f' **"{st.session_state.invoice_file_path_to_validate.name.split(".")[0]}"** Population Stats')
    st.dataframe(st.session_state.result_df, use_container_width=True, height=700)


def validation_analysis_form():
    st.subheader('Please fill the form below for the analysis of file!')
    columns = st.session_state.validation_df.columns
    date_col = st.selectbox("Select the Date Column", options=columns, index=None, placeholder="Date Column",
                            help="Select NONE if No Mapping Column Available")
    spend_col = st.selectbox("Select the Spend Column", options=columns, index=None, placeholder="Spend Column",
                             help="Select NONE if No Mapping Column Available")
    currency_col = st.selectbox("Select the Currency Column", options=columns, index=None,
                                placeholder="Currency Column", help="Select NONE if No Mapping Column Available")
    invoice_number_col = st.selectbox("Select the Invoice Number Column", options=columns, index=None,
                                      placeholder="Invoice Number Column",
                                      help="Select NONE if No Mapping Column Available")
    invoice_line_number_col = st.selectbox("Select the Invoice Line Number Column", options=columns, index=None,
                                           placeholder="Invoice Line Number Column",
                                           help="Select NONE if No Mapping Column Available")
    supplier_name_col = st.selectbox("Select the Supplier Name Column", options=columns, index=None,
                                     placeholder="Supplier Name Column",
                                     help="Select NONE if No Mapping Column Available")
    all_description_col = st.multiselect('Select all the Description Columns', options=columns,
                                         placeholder='Description Columns',
                                         help="Select NONE if No Mapping Column Available")
    if st.button("Begin Analysis!", use_container_width=True):
        # Check if all necessary fields are filled
        if all([date_col, spend_col, currency_col, invoice_number_col, invoice_line_number_col,
                supplier_name_col]) and all_description_col:
            st.session_state.mapping_dict = {
                'Date': date_col,
                "Spend": spend_col,
                "Currency": currency_col,
                'Invoice Number': invoice_number_col,
                'Invoice Line Number': invoice_line_number_col,
                'Supplier Name': supplier_name_col,
                'All Description': all_description_col
            }
            began_analysis()
        else:
            # Display warning if any fields are not filled
            no_file_provided("Please fill all the fields!")
            # st.warning('Please fill all the necessary fields!', icon='😒')


def check_content(value):
    if isinstance(value, str):
        # Check if the string is purely numeric
        if value.isdigit():
            return None
        # Check if the string contains only special characters
        if re.fullmatch(r'[^a-zA-Z0-9]+', value):
            return None
        # Check if the string contains both numbers and special characters, but no letters
        if re.search(r'[0-9]', value) and not re.search(r'[a-zA-Z]', value):
            return None
    # If it's a valid string with letters, symbols, or numbers, return it as-is
    return value


@st.dialog('Analysing..', width='small')
def began_analysis():
    with st.spinner('Wait for it...'):
        st.write('Initializing analysis...')
        result = {}
        df = st.session_state.validation_df.copy()
        total_transaction = df.shape[0]
        invalids = ["#N/A", 'N/A', 'NA', 'NULL', 'NONE', 'NOT ASSIGNED', 'NOT AVAILABLE', " ", '0', ' ', '']
        for key in st.session_state.mapping_dict:

            #: analysis of the description columns
            if key == 'All Description':
                desc_cols = st.session_state.mapping_dict[key]
                for column in desc_cols:
                    df[column] = df[column].apply(
                        lambda x: x.upper() if isinstance(x, str) else x
                    )
                    df[column] = df[column].replace(invalids, None)
                    df[column] = df[column].apply(check_content)
                    na_count = df[column].isna().sum()
                    percentage_na = ((total_transaction - na_count) / total_transaction) * 100
                    result[column] = {'Percentage Population': percentage_na, 'Comment': None,
                                      'Blank Rows Count': na_count,
                                      'Column Type': 'Important'}

            #: analysis of the date column
            elif key == "Date":
                upper_range = 2024
                lower_range = 2024
                date_col = st.session_state.mapping_dict[key]
                # Handle "NONE" case for the date column
                if result.get(date_col) == "NONE":
                    result[key] = {
                        'Percentage Population': None,
                        'Comment': 'No mapping column for this column',
                        'Blank Rows Count': None,
                        'Column Type': 'Important'
                    }
                else:
                    df[date_col] = pd.to_datetime(df[date_col], infer_datetime_format=True)
                    df['year'] = df[date_col].dt.year
                    out_of_range = df[(df['year'] > upper_range) | (df['year'] < lower_range)].shape[0]
                    out_of_range_percent = ((total_transaction - out_of_range) / total_transaction) * 100
                    result[date_col] = {
                        'Percentage Population': out_of_range_percent,
                        'Comment': f'Total {out_of_range} Outlier Document Dates found in Data',
                        'Blank Rows Count': out_of_range,
                        'Column Type': 'Important'
                    }

            #: analysis of the Spend column
            elif key == 'Spend':
                spend_col = st.session_state.mapping_dict[key]
                # Handle "NONE" case for the spend column
                if result.get(spend_col) == "NONE":
                    result[key] = {
                        'Percentage Population': None,
                        'Comment': 'No mapping column for this column',
                        'Blank Rows Count': None,
                        'Column Type': 'Important'
                    }
                else:
                    df[spend_col] = df[spend_col].astype(float)
                    Q1 = df[spend_col].quantile(0.25)
                    Q3 = df[spend_col].quantile(0.75)
                    IQR = Q3 - Q1
                    # Define outliers as values outside of 1.5 * IQR
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    print('lower bound q1,', lower_bound)
                    print('upper bound q2', upper_bound)
                    # Identify outliers
                    outliers = df[(df[spend_col] < lower_bound) | (df[spend_col] > upper_bound)][spend_col]
                    total_outlier_spend = outliers.sum()

                    # Filter out outliers before calculating positive and negative spend
                    df_no_outliers = df[(df[spend_col] >= lower_bound) & (df[spend_col] <= upper_bound)]
                    no_spend = df[spend_col].isna().sum()
                    negative_spend = df_no_outliers[df_no_outliers[spend_col] < 0][spend_col].sum()
                    positive_spend = df_no_outliers[df_no_outliers[spend_col] > 0][spend_col].sum()

                    # Calculate percentage of non-NA spend values
                    percentage_spend_na = ((total_transaction - no_spend) / total_transaction) * 100
                    result[key] = {
                        'Percentage Population': percentage_spend_na,
                        'Comment': f'Total negative Spend {negative_spend} and Positive Spend {positive_spend} and Total Outliers Spend is {total_outlier_spend}',
                        'Blank Rows Count': no_spend,
                        'Column Type': 'Important'
                    }

            #: analysing the currency column
            elif key == "Currency":
                currency_col = st.session_state.mapping_dict[key]
                # Handle "NONE" case for the currency column
                if result.get(currency_col) == "NONE":
                    result[key] = {
                        'Percentage Population': None,
                        'Comment': 'No mapping column for this column',
                        'Blank Rows Count': None,
                        'Column Type': 'Important'
                    }
                else:
                    null_currency = df[currency_col].isna().sum()
                    value_counts = list(df[currency_col].unique())
                    percentage_na = ((total_transaction - null_currency) / total_transaction) * 100
                    result[key] = {
                        'Percentage Population': percentage_na,
                        'Comment': f"Distinct Currencies :- {str(value_counts)}",
                        'Blank Rows Count': null_currency,
                        'Column Type': 'Important'
                    }

            #: analysis of the rest of the columns
            else:
                value = st.session_state.mapping_dict[key]
                nas = df[value].isna().sum()
                percentage = ((total_transaction - nas) / total_transaction) * 100
                result[key] = {'Percentage Population': percentage, 'Comment': None,
                               'Blank Rows Count': nas,
                               'Column Type': 'Important'}

        #: analysis of columns other than important, ie good to have columns
        for column in df.columns:
            if column not in list(st.session_state.mapping_dict.values()):
                nas = df[column].isna().sum()
                percentage = ((total_transaction - nas) / total_transaction) * 100
                result[column] = {'Percentage Population': percentage, 'Comment': None,
                                  'Blank Rows Count': nas,
                                  'Column Type': 'Good to have'}
        st.session_state.result_df = pd.DataFrame.from_records(result)
        st.session_state.result_df = st.session_state.result_df.transpose()
        st.session_state.result_df.reset_index(inplace=True)
        st.session_state['analysis_status'] = True
        st.success('Results Calculated Navigate to next page to checks the results!', icon='🎉')


def validation_validate_file():
    st.subheader('Individual file validation')
    # Check if the file has already been loaded
    if not st.session_state.file_load_status:
        load_file()
    # Proceed with validation if file has been loaded successfully
    if st.session_state.file_load_status:
        option = st.radio('Display option', ['Top 100', 'Last 100', 'Sample 100'])
        if option == 'Top 100':
            st.markdown("<h4><strong>Top 100 Rows</strong></h4>", unsafe_allow_html=True)
            st.dataframe(st.session_state.validation_df.head(100), height=700)
        elif option == 'Last 100':
            st.markdown("<h4><strong>Last 100 Rows</strong></h4>", unsafe_allow_html=True)
            st.dataframe(st.session_state.validation_df.tail(100), height=700)
        elif option == 'Sample 100':
            st.markdown("<h4><strong>Sample 100 Rows</strong></h4>", unsafe_allow_html=True)
            st.dataframe(st.session_state.validation_df.sample(100), height=700)


def validation_file_uploader():
    st.subheader("Please upload the file which you want to validate!")
    invoice_file_path_to_validate = st.file_uploader('Select the Raw/Invoice data to validate', type=['xlsx', 'csv'])
    st.session_state['invoice_file_path_to_validate'] = invoice_file_path_to_validate
    st.session_state.file_load_status = False


def validation_about():
    st.subheader("Hi! In this section of DAD we help you validate the structure of file on higher level.")
    st.markdown("""<h4>Instructions:</h4>""", unsafe_allow_html=True)

    # Instructions for individual file validation module
    st.markdown("""
                    - **Selecting Data**: Select the file you wish to validate.  
                    - **File Structure Validation**: This module allows you to validate the structure of an individual file before converting it to a common schema.  
                    - **View Top and Bottom Rows**: To ensure all important headers are present, this feature displays the top 100 rows and bottom 100 rows of the file.  
                    - **Data Consistency Check**: Check if there are any shifts or inconsistencies in data alignment across rows.
                    - **Population Stats Check**: Check the population stats of important colums.
                """)
    st.write("Please Nagivate to Next Page to Begin the File Validation Process😊")


def file_validation():
    if 'file_load_status' not in st.session_state:
        st.session_state.file_load_status = False
    if 'validation_df' not in st.session_state:
        st.session_state.validation_df = pd.DataFrame()
    if 'result_df' not in st.session_state:
        st.session_state.result_df = pd.DataFrame()
    if 'fv_page_index' not in st.session_state:
        st.session_state.fv_page_index = 0
    pages = [validation_about, validation_file_uploader, validation_validate_file, validation_analysis_form,
             validation_analysis_result]
    current_page = st.session_state.fv_page_index
    pages[current_page]()

    navigation_cols = st.columns(3)
    with navigation_cols[0]:
        #: not displaying the previous button on the first page
        if st.session_state.fv_page_index != 0:
            if st.button('Previous', use_container_width=True) and current_page > 0:
                st.session_state.fv_page_index -= 1
                st.rerun()

    with navigation_cols[2]:
        #: not dispalying the next button for the last pagecls
        if st.session_state.fv_page_index != 4:
            if st.button('Next', use_container_width=True):
                if st.session_state.fv_page_index == 1 and st.session_state.invoice_file_path_to_validate is None:
                    no_file_provided("No file Selected")
                elif st.session_state.fv_page_index == 3 and len(st.session_state.result_df) == 0:
                    no_file_provided('File not analyzed yet, analyse the file first!')
                elif st.session_state.fv_page_index < len(pages) - 1:
                    st.session_state.fv_page_index += 1
                    st.rerun()
