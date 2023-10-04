import streamlit as st
import pandas as pd
import os
import openpyxl
# Define the CSS for styling with text-align set to "right" and custom input styling
app_alignment_css = """
<style>
    body {
        direction: rtl;
    }
    input[type="text"] {
        width: max-content;
        margin-right: 5px;  /* Adjust the margin as needed */
        margin-left: 5px;   /* Adjust the margin as needed */
    }
</style>
"""

# Apply the CSS style to the entire app
st.markdown(app_alignment_css, unsafe_allow_html=True)

# Page for uploading the Excel file
def upload_page():
    st.header("رفع ملف الإكسل")
    st.write("Please upload an Excel file containing questions and answers.")
    
    # Add a file uploader for Excel file with a unique key
    uploaded_file = st.file_uploader("رفع ملف الإكسل", key="file_uploader", type=["xls", "xlsx"])
    
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
        st.error("ؤجاءًا رفع فايل الإكسل")
        return
    
    # Read the Excel file data
    data = pd.read_excel(file_path, engine="openpyxl")


    # Function to save changes to the Excel file
    def save_changes_to_excel(data, file_path):
        try:
            data.to_excel(file_path, index=False)
            st.success("تم حفظ التغييرات")
        except Exception as e:
            st.error(f"An error occurred while saving changes: {e}")

    # Check if the file exists; if not, create it
    if not os.path.exists(file_path):
        st.error(f"The file '{file_path}' does not exist.")
    else:
        data = pd.read_excel(file_path)
        # Page for displaying questions
        def page2(data):
            # Current question index
            current_question_idx = st.session_state.get("current_question_idx", 0)

            # Dropdown to select question index number
            question_indices = list(range(1, len(data) + 1))  # Assuming 1-based index
            selected_question_idx = st.selectbox("Select Question Index:", question_indices, index=current_question_idx)

            # Update the current_question_idx based on the selected index
            current_question_idx = selected_question_idx - 1  # Adjust for 0-based index
            st.session_state["current_question_idx"] = current_question_idx

            # Display the question and choices with the selected question index
            course_name = data.iloc[current_question_idx]['Course Name']
            v_value = data.iloc[current_question_idx]['V']
            p_value = data.iloc[current_question_idx]['P']
            l_value = data.iloc[current_question_idx]['L']
            s_value = data.iloc[current_question_idx]['S']

            # Header
            st.markdown(f"<h1 class='header'>{course_name}</h1>", unsafe_allow_html=True)
            st.markdown(f"<h5 class='subheader'>الفيديو {v_value} في الفقرة {p_value}</div>",
                        unsafe_allow_html=True)

            # Display the question and choices with the selected question index
            question_container = st.container()
            with question_container:
                question_idx = current_question_idx + 1  # Add 1 to make it 1-based index
                # Calculate the height required for the text
                question_text = data.iloc[current_question_idx]['Question']
                text_height = len(question_text.split('\n')) * 25  # You can adjust the factor as needed
                # Set the text-align property for the text_area to "right"
                question = st.text_area(
                    f"السؤال رقم {question_idx}",
                    question_text,
                    key=f"Question_{question_idx}",
                    height=text_height  # Set the height based on the calculated height
                )

                # Create two columns to display answer choices 1 & 2 in the same row and 3 & 4 in the same row
                col1, col2 , col3 = st.columns(3)

                # Displaying answer choices 1 & 2 in the same row
                with col1:
                    choices = [data.iloc[current_question_idx][f'Choice {i}'] for i in range(1, 3) if
                               not pd.isna(data.iloc[current_question_idx][f'Choice {i}'])]
                    edited_choices = []
                    for i, choice in enumerate(choices, start=1):
                        # Set the text-align property for the text_input to "right"
                        edited_choice = st.text_input(f"الإجابة رقم {i}", choice, key=f"Choice_{i}")
                        edited_choices.append(edited_choice)

                # Displaying answer choices 3 & 4 in the same row
                with col2:
                    choices = [data.iloc[current_question_idx][f'Choice {i}'] for i in range(3, 5) if
                               not pd.isna(data.iloc[current_question_idx][f'Choice {i}'])]
                    edited_choices += [None] * (4 - len(edited_choices))  # Ensure 'edited_choices' has at least 4 elements
                    for i, choice in enumerate(choices, start=3):
                        # Set the text-align property for the text_input to "right"
                        edited_choice = st.text_input(f"الإجابة رقم {i}", choice, key=f"Choice_{i}")
                        edited_choices.append(edited_choice)

                # Displaying answer choices 5 & 6 in the same row (if they exist)
                with col3:
                    for i in range(5, 7):
                        choice_value = data.iloc[current_question_idx][f'Choice {i}']
                        if not pd.isna(choice_value):
                            # Set the text-align property for the text_input to " right"
                            edited_choice = st.text_input(f"الإجابة رقم {i}", choice_value, key=f"Choice_{i}")
                            edited_choices.append(edited_choice)

            # Display the correct answer (editable field)
            correct_answer = st.text_input("الاختيار الصحيح", data.iloc[current_question_idx]['Right Answer'], key=f"Correct_Answer_{question_idx}")

            # Button handlers
            button_container = st.container()
            with button_container:
                col1, col2, col3, col4 = st.columns([10, 1, 2, 2])  # Adjust the column proportions as needed

                if col1.button("السؤال السابق") and current_question_idx > 0:
                    with st.spinner("Loading..."):
                        current_question_idx -= 1
                        st.session_state["current_question_idx"] = current_question_idx

                col2.empty()  # Empty column to create space
                if col4.button("احفظ التعديلات"):
                    try:
                        # Update the DataFrame with edited question, answer choices, and correct answer
                        data.at[current_question_idx, 'Question'] = question
                        data.at[current_question_idx, 'Choice 1'] = edited_choices[0]
                        data.at[current_question_idx, 'Choice 2'] = edited_choices[1]
                        data.at[current_question_idx, 'Choice 3'] = edited_choices[2]
                        data.at[current_question_idx, 'Choice 4'] = edited_choices[3]
                        data.at[current_question_idx, 'Choice 5'] = edited_choices[4]
                        data.at[current_question_idx, 'Choice 6'] = edited_choices[5]
                        data.at[current_question_idx, 'Right Answer'] = correct_answer

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
