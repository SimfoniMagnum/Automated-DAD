import streamlit as st


class DAD_About:
    def About(self):
        st.title("About Data Assessment Automation")

        # Overview
        st.subheader("Project Overview")
        st.markdown("""
            **Data Assessment Automation** is a tool designed to simplify and automate the process of data consolidation.
            This project assists users in transforming and standardizing data from multiple sources into a unified format,
            which helps streamline analysis, reporting, and integration tasks.
            """)

        # Purpose and Goals
        st.subheader("Purpose and Goals")
        st.markdown("""
            Data is often scattered across multiple files and systems, each with different structures, headers, and formats.
            Manually consolidating this data is time-consuming and error-prone. This tool aims to:
            - **Automate Data Consolidation**: Bring data from various sources to a consistent structure.
            - **Enhance Data Quality**: Ensure accurate, validated data with consistent headers and formats.
            - **Provide High-Level Insights**: Quickly assess key statistics and metadata for better understanding.
            """)

        # Key Modules and Features
        st.subheader("Key Modules and Features")
        st.markdown("""
            **1. Common Schema Module**  
            The Common Schema Module enables users to merge multiple files into a unified schema, ensuring consistency in headers and data format. 
            This module is essential for creating a consolidated master file with standardized column names, which simplifies analysis and further processing.

            **2. Data Mapping Module**  
            When you need to combine data from multiple sources based on common fields, the Data Mapping Module can be used. 
            This module allows users to specify key fields and column mappings, enabling easy linking and enrichment of data between files. 
            It simplifies the task of combining information across datasets while maintaining data integrity.

            **3. File Validation Module**  
            The File Validation Module provides users with a high-level structural check of individual files, ensuring that 
            critical headers are present and data is consistently populated. This module displays the top and bottom rows to highlight potential 
            formatting issues or misaligned data, making it easier to identify errors before further processing.

            **4. Population Statistics and Analysis**  
            At the end of the validation and mapping process, users can generate high-level population statistics 
            for key columns. This feature provides insights into data completeness, uniqueness, and overall quality, allowing users to assess 
            data readiness and identify gaps or inconsistencies.
            """)

        # How It Works
        st.subheader("How It Works")
        st.markdown("""
            - **Step 1**: Upload individual files (Excel or CSV formats) to the tool for validation and consolidation.
            - **Step 2**: Use the **File Validation Module** to check each file’s structure, ensuring that all required headers and data alignments are in place.
            - **Step 3**: If multiple files need to be merged, use the **Common Schema Module** to standardize headers across all files and create a master file.
            - **Step 4**: When combining data from different sources, apply the **Data Mapping Module** to link datasets based on shared keys.
            - **Step 5**: Finally, analyze the consolidated master file for population statistics, such as missing values, unique counts, and other metrics, to assess data quality.
            """)

        # Technologies Used
        st.subheader("Technologies Used")
        st.markdown("""
            - **Streamlit**: Provides a user-friendly interface for interacting with the data and modules.
            - **Pandas & Polars**: Used for data processing, reading/writing files, and performing data transformations.
            - **Python**: Core programming language powering the logic and functionality of each module.
            """)

        # Summary
        st.subheader("Summary")
        st.write("""
            **Data Assessment Automation** is an all-in-one solution for data consolidation, mapping, validation, and analysis.
            By automating these processes, the tool helps users save time, reduce errors, and gain actionable insights from their data.
            """)
