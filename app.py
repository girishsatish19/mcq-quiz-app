import streamlit as st
from docx import Document
import re

st.set_page_config(page_title="MCQ Practice", layout="centered")

# ----------- PARSE WORD FILE -----------
def extract_mcqs(file):
    doc = Document(file)
    questions = []
    current_q = None

    for para in doc.paragraphs:
        text = para.text.strip()

        if not text:
            continue

        if re.match(r"^(Q\d+|Question\s*\d+|\d+\.)", text, re.IGNORECASE):
            if current_q:
                questions.append(current_q)

            current_q = {
                "question": text,
                "options": [],
                "correct": None
            }

        elif text.startswith(("A.", "B.", "C.", "D.")):
            if current_q is None:
                continue

            is_correct = any(run.font.highlight_color for run in para.runs)

            current_q["options"].append(text)

            if is_correct:
                current_q["correct"] = text

    if current_q:
        questions.append(current_q)

    return questions


# ----------- SIMPLE FREE EXPLANATION (NO API KEY) -----------
def generate_explanation(question, correct_answer):
    return f"The correct answer is {correct_answer}. This best matches the question requirements compared to other options."


# ----------- UI -----------
st.title("📘 MCQ Practice Mode")

uploaded_file = st.file_uploader("Upload your MCQ Word file", type=["docx"])

if uploaded_file:
    questions = extract_mcqs(uploaded_file)

    if len(questions) == 0:
        st.error("❌ No questions detected. Check format.")
        st.stop()

    # Session state
    if "q_index" not in st.session_state:
        st.session_state.q_index = 0
        st.session_state.submitted = False

    q_index = st.session_state.q_index
    q = questions[q_index]

    st.markdown(f"### Question {q_index + 1} / {len(questions)}")
    st.write(q["question"])

    selected = st.radio(
        "Select your answer:",
        q["options"],
        key=f"q_{q_index}"
    )

    # ----------- SUBMIT PER QUESTION -----------
    if st.button("Submit Answer ✅"):
        st.session_state.submitted = True

    # ----------- SHOW RESULT -----------
    if st.session_state.submitted:
        if selected == q["correct"]:
            st.success("✅ Correct!")
        else:
            st.error(f"❌ Incorrect! Correct: {q['correct']}")

        explanation = generate_explanation(q["question"], q["correct"])
        st.info(f"📘 Explanation: {explanation}")

    # ----------- NAVIGATION -----------
    col1, col2 = st.columns(2)

    with col1:
        if st.button("⬅️ Previous") and q_index > 0:
            st.session_state.q_index -= 1
            st.session_state.submitted = False

    with col2:
        if st.button("Next ➡️") and q_index < len(questions) - 1:
            st.session_state.q_index += 1
            st.session_state.submitted = False
