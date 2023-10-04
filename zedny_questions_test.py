# %%writefile zedny_questions.py

import streamlit as st
import pandas as pd
import os

# Create a Streamlit app
st.title("Zedny Questions Editor")

# Page for uploading the Excel file
def upload_page():
    st.header("Upload Excel File")
    st.write("Please upload an Excel file containing questions and answers.")
    
    # Add a file uploader for Excel file with a unique key
    uploaded_file = st.file_uploader("Upload an Excel file", key="file_uploader", type=["xls", "xlsx"])
    
    if uploaded_file is not None:
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
        st.error("Please upload an Excel file first.")
        return
    
    # Read the Excel file data
    data = pd.read_excel(file_path)

    # Function to save changes to the Excel file
    def save_changes_to_excel(data, file_path):
        try:
            data.to_excel(file_path, index=False)
            st.success("Changes Saved!")
        except Exception as e:
            st.error(f"An error occurred while saving changes: {e}")

    # Check if the file exists; if not, create it
    if not os.path.exists(file_path):
        st.error(f"The file '{file_path}' does not exist.")
    else:
        data = pd.read_excel(file_path)

        # Define the CSS for styling
        page_css = """
            <style>
                body {
                    font-family: Arial, sans-serif;
                }
                .header {
                    font-size: 24px;
                    font-weight: bold;
                    margin-bottom: 20px;
                }
                .question-container {
                    background-color: #f5f5f5;
                    border: 1px solid #ddd;
                    padding: 20px;
                    border-radius: 5px;
                    margin-bottom: 20px;
                    text-align: right; /* Align text to the right */
                }
                .button-container {
                    margin-top: 10px;
                }
                .editable-answer {
                    border: 1px solid #ddd;
                    padding: 10px;
                    border-radius: 5px;
                }
            </style>
        """

        # Add the CSS to the Streamlit app
        st.markdown(page_css, unsafe_allow_html=True)

        # Page for displaying questions
        def page2(data):
            # Current question index
            current_question_idx = st.session_state.get("current_question_idx", 0)
            course_name = data.iloc[current_question_idx]['Course Name']
            v_value = data.iloc[current_question_idx]['V']
            p_value = data.iloc[current_question_idx]['P']
            l_value = data.iloc[current_question_idx]['L']
            s_value = data.iloc[current_question_idx]['S']

            # Header
            st.markdown(f"<h1 class='header'>{course_name}</h1>", unsafe_allow_html=True)
            st.markdown(f"<h5 class='subheader'>Video is: {v_value}, Paragraph is: {p_value}</div>",
                        unsafe_allow_html=True)

            # Display the question and choices with the question index
            question_container = st.container()
            with question_container:
                question_idx = current_question_idx + 1  # Add 1 to make it 1-based index
                question = st.text_area(f"Question {question_idx}:", data.iloc[current_question_idx]['Question'])

                # Create two columns to display answer choices 1 & 2 in the same row and 3 & 4 in the same row
                col1, col2 = st.columns(2)

                # Displaying answer choices 1 & 2 in the same row
                with col1:
                    choices = [data.iloc[current_question_idx][f'Choice {i}'] for i in range(1, 3) if
                               not pd.isna(data.iloc[current_question_idx][f'Choice {i}'])]
                    edited_choices = []
                    for i, choice in enumerate(choices, start=1):
                        edited_choice = st.text_input(f"الإجابة رقم {i}", choice)
                        edited_choices.append(edited_choice)

                # Displaying answer choices 3 & 4 in the same row
                with col2:
                    choices = [data.iloc[current_question_idx][f'Choice {i}'] for i in range(3, 5) if
                               not pd.isna(data.iloc[current_question_idx][f'Choice {i}'])]
                    edited_choices += [None] * (4 - len(edited_choices))  # Ensure 'edited_choices' has at least 4 elements
                    for i, choice in enumerate(choices, start=3):
                        edited_choice = st.text_input(f"الإجابة رقم {i}", choice)
                        edited_choices.append(edited_choice)

            # Display the correct answer (editable field)
            correct_answer = st.text_input("الاختيار الصحيح", data.iloc[current_question_idx]['Right Answer'])

            # Button handlers
            button_container = st.container()
            with button_container:
                col1, col2, col3 = st.columns(3)
                if col1.button("Previous") and current_question_idx > 0:
                    with st.spinner("Loading..."):
                        current_question_idx -= 1
                        st.session_state["current_question_idx"] = current_question_idx
                col2.empty()
                if col3.button("Next") and current_question_idx < len(data) - 1:
                    with st.spinner("Loading..."):
                        current_question_idx += 1
                        st.session_state["current_question_idx"] = current_question_idx

                if col1.button("Save Changes"):
                    try:
                        # Update the DataFrame with edited question, answer choices, and correct answer
                        data.at[current_question_idx, 'Question'] = question
                        data.at[current_question_idx, 'Choice 1'] = edited_choices[0]
                        data.at[current_question_idx, 'Choice 2'] = edited_choices[1]
                        data.at[current_question_idx, 'Choice 3'] = edited_choices[2]
                        data.at[current_question_idx, 'Choice 4'] = edited_choices[3]
                        data.at[current_question_idx, 'Right Answer'] = correct_answer

                        # Drop the "Choice 0" column if it exists
                        if 'Choice 0' in data.columns:
                            data = data.drop(columns=['Choice 0'])

                        st.success("Changes saved successfully")
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")

                    # Save all changes to the Excel file
                    save_changes_to_excel(data, file_path)

                if current_question_idx == len(data) - 1:
                    st.markdown("<div class='header'>End of questions.</div>", unsafe_allow_html=True)

        # Initially display the questions page if an Excel file is uploaded
        page2(data)

# Check which page to display based on user's choice
pages = {
    "Upload Excel File": upload_page,
    "Show Data": questions_page  # Added "Show Data" page directly to the navigation
}

user_choice = st.sidebar.selectbox("Choose your page:", list(pages.keys()))
pages[user_choice]()
