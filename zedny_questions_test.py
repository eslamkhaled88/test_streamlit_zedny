import streamlit as st
import numpy as np
import pandas as pd
import os
import platform

# Get the user's home directory dynamically
user_home_directory = os.path.expanduser("~")

# Define the directory path for saving edited files based on the operating system
if platform.system() == "Linux":
    save_directory = os.path.join(
        user_home_directory, "Downloads", "Updated Quizzes")
elif platform.system() == "Darwin":  # Check for Apple (macOS)
    save_directory = os.path.join(
        user_home_directory, "Downloads", "Updated Quizzes")
else:
    save_directory = os.path.join(
        user_home_directory, "Downloads", "Updated Quizzes")

# Create the save directory if it does not exist
os.makedirs(save_directory, exist_ok=True)

# Define the CSS for styling with text-align set to "right" and custom input styling
app_alignment_css = """
<style>
    .stContainer {
    border: none !important;
    }
    body {
        direction: rtl;
        display: flex;
        flex-direction: column;
        border-top: 2px solid #ccc; /* Adjust color and width as needed */
        border-bottom: 2px solid #ccc;
        height: 90vh; /* Set the height to 90% of the viewport height */
        margin: 0; /* Remove default body margin */
        overflow-y: hidden; /* Hide vertical scrollbar */
    }
    input[type="text"] {
        width: max-content;
        margin-right: 5px;
        margin-left: 5px;
    }
    .main-container {
        width: 90% !important;
        margin: 0 auto !important;
        flex: 1; /* Allows container to expand and consume available space */
        display: flex;
        flex-direction: column;
    }
    .element-container {
        width: 100% !important;
    }
    .stTextArea, .stText{
        width: 100% !important;
    }
    .stButton>button {
        width: max-content;
        width: 100%;
    }
    .header, .subheader {
        margin-top: 0; /* Remove default top margin from headers */
    }
    /* Your additional CSS rules... */
</style>
"""

# Apply the CSS style to the entire app
st.markdown(app_alignment_css, unsafe_allow_html=True)


def upload_page():
    st.header("رفع ملف الإكسل")
    st.write("Please upload an Excel file containing questions and answers.")

    # Add a file uploader for Excel file with a unique key
    uploaded_file = st.file_uploader(
        "رفع ملف الإكسل", key="file_uploader", type=["xls", "xlsx"])

    if uploaded_file is not None:
        # Check if the file extension is valid
        file_extension = uploaded_file.name.split(".")[-1].lower()
        if file_extension not in ["xls", "xlsx"]:
            st.error(
                "Invalid file extension. Please upload an Excel file with .xls or .xlsx extension.")
            return

        # Save the uploaded file to a temporary location
        with open(uploaded_file.name, "wb") as f:
            f.write(uploaded_file.getvalue())

        # Redirect to the questions page
        st.session_state["file_path"] = uploaded_file.name
        questions_page()  # Directly call the questions page after uploading

# Page for displaying and editing questions


def questions_page():
    file_path = st.session_state.get("file_path")
    if file_path is None or not os.path.exists(file_path):
        st.error("رجاءًا رفع فايل الإكسل")
        return

    try:
        # Read the Excel file data
        data = pd.read_excel(file_path)

        # Check if the required columns exist in the DataFrame
        required_columns = ['Course Name', 'V', 'P', 'Question', 'Choice 1',
                            'Choice 2', 'Choice 3', 'Choice 4', 'Choice 5', 'Choice 6', 'Right Answer']
        missing_columns = [
            col for col in required_columns if col not in data.columns]
        if missing_columns:
            st.error(
                f"الملف الذي تم رفعه يحتوي على خطأ في تسمية اعمدة البيانات وتحديدًا في القيمة  {', '.join(missing_columns)}  رجاءًا عدل الملف وأعد رفعه")
            return

        # Function to save changes to the Excel file
        def save_changes_to_excel(data, file_path):
            try:
                data.to_excel(file_path, index=False)
                # Save the edited file to the appropriate directory based on the operating system
                edited_file_path = os.path.join(
                    save_directory, os.path.basename(file_path))
                data.to_excel(edited_file_path, index=False)
                st.success(f"تم حفظ الملف المعدل في:  {edited_file_path}")
            except Exception as e:
                st.error(f"An error occurred while saving changes: {e}")

        # Page for displaying questions

        def page2(data):
            # Ensure the current_question_idx is initialized and within bounds
            current_question_idx = st.session_state.get(
                "current_question_idx", 0)
            current_question_idx = max(
                0, min(current_question_idx, len(data) - 1))

            # Fetch necessary data
            course_name = data.iloc[current_question_idx]['Course Name']
            v_value = data.iloc[current_question_idx]['V']
            p_value = data.iloc[current_question_idx]['P']

            # Render header and subheader at the top
            st.markdown(
                f"<h1 class='header'>{course_name}</h1>", unsafe_allow_html=True)
            st.markdown(
                f"<h5 class='subheader'>الفيديو {v_value} في الفقرة {p_value}</div>", unsafe_allow_html=True)

            # Dropdown to select question index number (1-based index)
            question_indices = list(range(1, len(data) + 1))
            selected_question_idx = st.selectbox(
                "توجه للسؤال الذي تريده:", question_indices, index=current_question_idx)

            # Update the current_question_idx based on the selected index (0-based index)
            current_question_idx = selected_question_idx - 1
            st.session_state["current_question_idx"] = current_question_idx

            # Display the question and choices with the selected question index
            question_container = st.container()
            with question_container:
                question_text = data.iloc[current_question_idx]['Question']
                # Calculate the required height
                text_height = len(question_text.split('\n')) * 25
                question = st.text_area(
                    f"السؤال رقم {selected_question_idx}",
                    question_text,
                    key=f"Question_{selected_question_idx}",
                    height=text_height
                )

                # Create two columns to display answer choices 1 & 2 in the same row and 3 & 4 in the same row
                col1, col2, col3 = st.columns(3)

                # Initialize an empty list to store the edited choices
                edited_choices = []

                # Define a function to display choices in a column
                def display_choices(column, start_idx, end_idx):
                    nonlocal edited_choices  # Allow the function to modify the variable outside its scope
                    choices = [data.iloc[current_question_idx][f'Choice {i}']
                               for i in range(start_idx, end_idx + 1)]
                    for i, choice in enumerate(choices, start=start_idx):
                        # Replace NaN with an empty string
                        choice_value = "" if pd.isna(choice) else choice
                        edited_choice = column.text_input(
                            f"الإجابة رقم {i}", choice_value, key=f"Choice_{i}")
                        edited_choices.append(edited_choice)

                # Displaying answer choices 1 & 2 in the first column
                display_choices(col1, 1, 2)

                # Displaying answer choices 3 & 4 in the second column
                display_choices(col2, 3, 4)

                # Displaying answer choices 5 & 6 in the third column
                display_choices(col3, 5, 6)

            # Display the correct answer (editable field)
            correct_answer = st.text_input(
                "الاختيار الصحيح", data.iloc[current_question_idx]['Right Answer'], key=f"Correct_Answer_{current_question_idx}")

            # Button handlers
            button_container = st.container()
            with button_container:
                # Adjust the column proportions as needed
                col1, col2, col3, col4 = st.columns([1, 3, 1, 1])

                if col1.button("السؤال السابق") and current_question_idx > 0:
                    with st.spinner("Loading..."):
                        current_question_idx -= 1
                        st.session_state["current_question_idx"] = current_question_idx

                col2.empty()  # Empty column to create space
                if col4.button("احفظ التعديلات"):
                    try:
                        # Update the DataFrame with edited question, answer choices, and correct answer
                        data.at[current_question_idx, 'Question'] = question
                        data.at[current_question_idx,
                                'Choice 1'] = edited_choices[0]
                        data.at[current_question_idx,
                                'Choice 2'] = edited_choices[1]
                        data.at[current_question_idx,
                                'Choice 3'] = edited_choices[2]
                        data.at[current_question_idx,
                                'Choice 4'] = edited_choices[3]
                        data.at[current_question_idx,
                                'Choice 5'] = edited_choices[4]
                        data.at[current_question_idx,
                                'Choice 6'] = edited_choices[5]
                        data.at[current_question_idx,
                                'Right Answer'] = correct_answer

                        # Drop the "Choice 0" column if it exists
                        if 'Choice 0' in data.columns:
                            data = data.drop(columns=['Choice 0'])

                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")

                    # Save all changes to the Excel file
                    save_changes_to_excel(data, file_path)

                if col3.button("السؤال التالي") and current_question_idx < len(data) - 1:
                    with st.spinner("Loading..."):
                        current_question_idx += 1
                        st.session_state["current_question_idx"] = current_question_idx

                if current_question_idx == len(data) - 1:
                    st.markdown(
                        "<div class='header'>End of questions.</div>", unsafe_allow_html=True)

        # Initially display the questions page if an Excel file is uploaded
        page2(data)

    except pd.errors.EmptyDataError:
        st.error("The uploaded file is empty. Please upload a file with data.")
    except pd.errors.ParserError:
        st.error(
            "An error occurred while parsing the Excel file. Please make sure it is a valid Excel file.")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")


# Check which page to display based on user's choice
pages = {
    "Upload Excel File": upload_page,
    "Show Data": questions_page
}

user_choice = st.sidebar.selectbox("Choose your page:", list(pages.keys()))

# Main app container
main_container = st.container()
with main_container:
    pages[user_choice]()
