from typing import List, Optional

import pandas as pd
import streamlit as st
from datetime import datetime


class ErrorDialog:
    @staticmethod
    @st.dialog('Alert!')
    def show_error(message: str):
        st.error(message,icon='😭')

    @staticmethod
    @st.dialog('Warning!')
    def show_warning(message: str):
        st.warning(message)

    @staticmethod
    @st.dialog("Success!")
    def show_success(message: str):
        st.success(message, icon='🎉')

    @st.dialog('Saving file')
    def save_analysis_result(df: pd.DataFrame):
        with st.spinner('Saving File'):
            try:
                time_str = datetime.now().strftime('%H-%M-%S-%f')  # '%H-%M-%S-%f' formats time in a safe way
                filename = f'Analysis Result {time_str}.xlsx'
                df.to_excel(filename)
                st.success("File saved successfully!",icon='🎉')
            except Exception as e:
                st.error(f"{e} Error Occured while saving file")


class FileUploader:
    def __init__(self, label: str, multiple_files: bool = False, file_types: Optional[List[str]] = None):
        """
                Initializes the file uploader component.
                Args:
                    label (str): The label displayed for the file uploader.
                    multiple_files (bool): Whether to allow multiple file uploads.
                    file_types (Optional[List[str]]): List of allowed file types (e.g., ["csv", "txt", "xlsx"]).
                """
        self.label = label
        self.multiple_files = multiple_files
        self.file_types = file_types or ["csv", "xlsx"]
        self.uploaded_files = None

    def render(self):
        self.uploaded_files = st.file_uploader(
            label=self.label,
            accept_multiple_files=self.multiple_files,
            type=self.file_types
        )
        return self.uploaded_files
