import streamlit as st
from docx import Document

st.set_page_config(page_title="Mock Test", layout="centered")

def extract_mcqs(file):
    import re
    from docx import Document

    doc = Document(file)
    questions = []
    current_q = None

    for para in doc.paragraphs:
        text = para.text.strip()

        if not text:
            continue

        # Detect question (more flexible)
        if re.match(r"^(Q\d+|Question\s*\d+|\d+\.)", text, re.IGNORECASE):
            if current_q:
                questions.append(current_q)

            current_q = {
                "question": text,
                "options": [],
                "correct": None
            }

        # Detect options
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


st.title("📘 MCQ Mock Test")

uploaded_file = st.file_uploader("Upload your MCQ Word file", type=["docx"])

if uploaded_file:
    questions = extract_mcqs(uploaded_file)

    score = 0

    for i, q in enumerate(questions):
        st.subheader(q["question"])

        choice = st.radio("Choose answer:", q["options"], key=i)

        if st.button(f"Submit Q{i+1}", key=f"btn{i}"):
            if choice == q["correct"]:
                st.success("✅ Correct!")
                score += 1
            else:
                st.error(f"❌ Incorrect! Correct: {q['correct']}")

    st.write("### 🎯 Your Score will be calculated manually for now")
st.write("Total Questions Detected:", len(questions))
