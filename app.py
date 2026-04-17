import streamlit as st
from docx import Document
import re

st.set_page_config(page_title="Mock Test", layout="centered")

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


# ----------- EXPLANATION FUNCTION (SIMPLE VERSION) -----------
def generate_explanation(question, correct_answer):
    return f"This is correct because the answer is: {correct_answer}"


# ----------- UI -----------
st.title("📘 MCQ Practice")

uploaded_file = st.file_uploader("Upload your MCQ Word file", type=["docx"])

if uploaded_file:
    questions = extract_mcqs(uploaded_file)

    if len(questions) == 0:
        st.error("❌ No questions detected. Check format.")
        st.stop()

    # Session state
    if "q_index" not in st.session_state:
        st.session_state.q_index = 0
        st.session_state.answers = [None] * len(questions)
        st.session_state.submitted = False

    q_index = st.session_state.q_index
    q = questions[q_index]

    # ----------- QUESTION DISPLAY -----------
    st.markdown(f"### Question {q_index + 1} / {len(questions)}")
    st.write(q["question"])

    selected = st.radio(
        "Select your answer:",
        q["options"],
        index=q["options"].index(st.session_state.answers[q_index])
        if st.session_state.answers[q_index] else 0
    )

    st.session_state.answers[q_index] = selected

    # ----------- NAVIGATION -----------
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("⬅️ Prev") and q_index > 0:
            st.session_state.q_index -= 1

    with col2:
        if st.button("Next ➡️") and q_index < len(questions) - 1:
            st.session_state.q_index += 1

    with col3:
        if st.button("Submit ✅"):
            st.session_state.submitted = True

    # ----------- RESULTS -----------
    if st.session_state.submitted:
        st.write("## 📊 Results")

        score = 0

        for i, q in enumerate(questions):
            user_ans = st.session_state.answers[i]
            correct = q["correct"]

            if user_ans == correct:
                st.success(f"Q{i+1}: ✅ Correct")
                score += 1
            else:
                st.error(f"Q{i+1}: ❌ Incorrect")
                st.write(f"**Correct Answer:** {correct}")

            # Explanation
            explanation = generate_explanation(q["question"], correct)
            st.info(f"📘 Explanation: {explanation}")

        st.write(f"### 🎯 Score: {score} / {len(questions)}")
