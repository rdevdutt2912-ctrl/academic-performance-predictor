import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

st.set_page_config(page_title="StudySpark | Academic Predictor", page_icon="🎓", layout="wide")

SUBJECT_MAX = {
    "English": 80, "Physics": 70, "Chemistry": 70, "Biology": 70,
    "Mathematics": 70, "Computer Science": 70, "Psychology": 70,
    "Information Technology (IT)": 70, "Physical Education (PE)": 70,
    "Artificial Intelligence (AI)": 50
}
COMMON_SUBJECTS = ["English", "Physics", "Chemistry"]
MATH_PSYCHOLOGY_OPTIONS = ["Mathematics", "Psychology"]
BIOLOGY_CS_OPTIONS = ["Biology", "Computer Science"]
SIXTH_OPTIONS = [
    "Artificial Intelligence (AI)",
    "Information Technology (IT)",
    "Physical Education (PE)",
    "Psychology",
    "Mathematics",
    "Biology",
    "Computer Science",
]

st.markdown("""
<style>
.block-container {padding-top:1.5rem}
div[data-testid="stMetric"] {background:#fff; border:1px solid #e6e8f0; padding:12px; border-radius:14px}
.hero {background:linear-gradient(120deg,#352a86,#6558d3,#a78bfa);color:white;padding:26px;border-radius:18px}
</style>
""", unsafe_allow_html=True)

st.sidebar.title("🎓 StudySpark")
st.sidebar.caption("Academic Performance Predictor")
page = st.sidebar.radio("Choose a page", ["🏠 Home", "📘 Predict one subject", "📊 Overall performance", "🏆 Leaderboard", "ℹ️ About"])
st.sidebar.caption("Class XII AI project prototype")

def get_subjects(math_psychology, biology_cs, sixth):
    # Prevent duplicate subjects if a core choice also appears in the sixth-subject menu.
    subjects = COMMON_SUBJECTS + [math_psychology, biology_cs]
    if sixth not in subjects:
        subjects.append(sixth)
    return subjects

def subject_choices(prefix):
    col1, col2 = st.columns(2)
    with col1:
        math_psychology = st.selectbox(
            "Switch 1: Mathematics or Psychology",
            MATH_PSYCHOLOGY_OPTIONS,
            key=f"{prefix}_math_psychology",
        )
    with col2:
        biology_cs = st.selectbox(
            "Switch 2: Biology or Computer Science",
            BIOLOGY_CS_OPTIONS,
            key=f"{prefix}_biology_cs",
        )
    unavailable = COMMON_SUBJECTS + [math_psychology, biology_cs]
    available_sixth = [s for s in SIXTH_OPTIONS if s not in unavailable]
    sixth = st.selectbox(
        "Choose your sixth subject",
        available_sixth,
        key=f"{prefix}_sixth",
    )
    return get_subjects(math_psychology, biology_cs, sixth)

def build_model(subject):
    # Synthetic demo data only. Not real student records.
    rng = np.random.default_rng(2026 + sum(ord(c) for c in subject))
    maximum = SUBJECT_MAX[subject]
    n = 240
    previous = rng.uniform(maximum * .25, maximum * .95, n)
    hours = rng.uniform(0, 8, n)
    attendance = rng.uniform(45, 100, n)
    assignments = rng.uniform(20, 100, n)
    target = (.62 * previous + (hours / 8) * maximum * .18
              + (attendance / 100) * maximum * .10
              + (assignments / 100) * maximum * .10
              + rng.normal(0, maximum * .045, n))
    target = np.clip(target, 0, maximum)
    X = pd.DataFrame({"previous": previous, "hours": hours, "attendance": attendance, "assignments": assignments})
    model = LinearRegression().fit(X, target)
    return model

def predict(subject, previous, hours, attendance, assignments):
    model = build_model(subject)
    x = pd.DataFrame([{"previous": previous, "hours": hours, "attendance": attendance, "assignments": assignments}])
    return float(np.clip(model.predict(x)[0], 0, SUBJECT_MAX[subject]))

def badge(percent):
    if percent >= 90: return "💎 Diamond"
    if percent >= 80: return "🥇 Gold"
    if percent >= 70: return "🥈 Silver"
    if percent >= 60: return "🥉 Bronze"
    return "🌱 Starter"

def message(percent):
    if percent >= 90: return "Outstanding! 🌟 Keep it up."
    if percent >= 80: return "Excellent progress! 🚀"
    if percent >= 70: return "Great work—keep building! 💪"
    if percent >= 60: return "Good effort. Small, steady steps help. 🌱"
    return "A fresh study plan can help you improve. 🧭"

if "leaderboard" not in st.session_state:
    st.session_state.leaderboard = [
        {"Nickname":"StudyNinja","Stream":"Mathematics + Biology","Percentage":94.2},
        {"Nickname":"PixelScholar","Stream":"Psychology + Biology","Percentage":91.6},
        {"Nickname":"ChemChampion","Stream":"Mathematics + Computer Science","Percentage":88.4},
        {"Nickname":"BioBlazer","Stream":"Mathematics + Biology","Percentage":84.7},
        {"Nickname":"PhysicsPro","Stream":"Psychology + Biology","Percentage":81.3},
    ]

if page == "🏠 Home":
    st.markdown('<div class="hero"><h1>🎓 Welcome to StudySpark!</h1><h3>Predict. Improve. Celebrate progress.</h3><p>Explore estimated marks, understand your subject mix, and turn study goals into small wins.</p></div>', unsafe_allow_html=True)
    a,b,c = st.columns(3)
    a.markdown("### 📘 One subject"); a.write("Estimate marks out of the selected subject maximum.")
    b.markdown("### 📊 Overall performance"); b.write("See six-subject totals, percentage and graphs.")
    c.markdown("### 🏆 Leaderboard"); c.write("Explore sample rankings and achievement badges.")
    st.info("Demo notice: the prediction model uses synthetic data. Results are illustrative, not validated forecasts.")
    st.subheader("Maximum marks")
    st.dataframe(pd.DataFrame([{"Subject":s,"Maximum marks":m} for s,m in SUBJECT_MAX.items()]), hide_index=True, use_container_width=True)

elif page == "📘 Predict one subject":
    st.title("📘 Predict one subject")
    subjects = subject_choices("one")
    subject = st.selectbox("Subject to predict", subjects)
    maximum = SUBJECT_MAX[subject]
    st.caption(f"Maximum marks for {subject}: {maximum}")
    with st.form("one_form"):
        previous = st.number_input(f"Previous marks (out of {maximum})", 0.0, float(maximum), float(round(maximum*.65)), 1.0)
        hours = st.slider("Study hours per day", 0.0, 12.0, 3.0, .5)
        attendance = st.slider("Attendance (%)", 0, 100, 85)
        assignments = st.slider("Assignments completed (%)", 0, 100, 80)
        go = st.form_submit_button("✨ Predict my marks", type="primary", use_container_width=True)
    if go:
        score = predict(subject, previous, hours, attendance, assignments)
        pct = score / maximum * 100
        a,b,c = st.columns(3)
        a.metric("Estimated marks", f"{score:.1f} / {maximum}")
        b.metric("Estimated percentage", f"{pct:.1f}%")
        c.metric("Achievement badge", badge(pct))
        st.progress(min(max(pct/100,0),1))
        st.success(message(pct))
        st.bar_chart(pd.DataFrame({"Marks":[previous,score]}, index=["Previous marks","Model estimate"]))
        st.caption("This estimate comes from synthetic demo data and has not been validated against real exam outcomes.")

elif page == "📊 Overall performance":
    st.title("📊 Overall performance")
    subjects = subject_choices("all")
    st.write("Enter previous marks for all six subjects. The maximum is shown beside each subject.")
    with st.form("overall_form"):
        hours = st.slider("Average study hours per day", 0.0, 12.0, 3.0, .5)
        attendance = st.slider("Attendance (%)", 0, 100, 85)
        assignments = st.slider("Assignments completed (%)", 0, 100, 80)
        marks = {}
        left, right = st.columns(2)
        for i, subject in enumerate(subjects):
            with (left if i % 2 == 0 else right):
                maximum = SUBJECT_MAX[subject]
                marks[subject] = st.number_input(f"{subject} (out of {maximum})", 0.0, float(maximum), float(round(maximum*.65)), 1.0, key="marks_"+subject)
        go = st.form_submit_button("🏆 Calculate my overall estimate", type="primary", use_container_width=True)
    if go:
        rows = []
        for subject in subjects:
            maximum = SUBJECT_MAX[subject]
            score = predict(subject, marks[subject], hours, attendance, assignments)
            rows.append({"Subject":subject,"Previous marks":marks[subject],"Estimated marks":round(score,1),"Maximum marks":maximum,"Estimated %":round(score/maximum*100,1)})
        df = pd.DataFrame(rows)
        estimated_total = df["Estimated marks"].sum()
        max_total = int(df["Maximum marks"].sum())
        entered_total = df["Previous marks"].sum()
        entered_pct = entered_total / max_total * 100
        estimated_pct = estimated_total / max_total * 100
        a, b, c, d = st.columns(4)
        a.metric("Entered marks total", f"{entered_total:.1f} / {max_total}")
        b.metric("Actual percentage", f"{entered_pct:.2f}%")
        c.metric("Model-estimated total", f"{estimated_total:.1f} / {max_total}")
        d.metric("Estimated percentage", f"{estimated_pct:.2f}%")
        st.caption("Actual percentage is calculated from the marks you entered. Estimated percentage comes from the illustrative ML model.")
        st.success(message(entered_pct))
        st.dataframe(df, hide_index=True, use_container_width=True)
        st.subheader("📈 Subject comparison")
        st.bar_chart(df.set_index("Subject")[["Previous marks","Estimated marks"]])
        st.download_button("⬇️ Download results as CSV", df.to_csv(index=False).encode("utf-8"), "studyspark_summary.csv", "text/csv")
        st.caption("Predictions use synthetic demo data. Actual percentage uses entered marks; estimated percentage uses model-generated marks. The model has not been validated against real exam outcomes.")

elif page == "🏆 Leaderboard":
    st.title("🏆 StudySpark leaderboard")
    st.warning("Use nicknames only, not full names. This starter version stores entries only in the current session and does not save them permanently or share them globally.")
    st.caption("The starter entries are fictional examples for demonstrating the leaderboard.")
    with st.form("leader_form"):
        nickname = st.text_input("Nickname (no full names)", max_chars=20, placeholder="e.g. BioBlazer")
        stream = st.selectbox("Subject combination", [
            "Mathematics + Biology", "Mathematics + Computer Science",
            "Psychology + Biology", "Psychology + Computer Science"
        ], key="leader_stream")
        percentage = st.number_input("Overall percentage", 0.0, 100.0, 75.0, .5)
        add = st.form_submit_button("🌟 Add my demo score", type="primary", use_container_width=True)
    if add:
        if nickname.strip():
            st.session_state.leaderboard.append({"Nickname":nickname.strip(),"Stream":stream,"Percentage":round(float(percentage),1)})
            st.success("Added to this session's leaderboard!")
        else:
            st.error("Enter a nickname first.")
    board = pd.DataFrame(st.session_state.leaderboard).sort_values("Percentage", ascending=False).drop_duplicates("Nickname", keep="last").reset_index(drop=True)
    board.insert(0, "Rank", range(1,len(board)+1))
    board["Badge"] = board["Percentage"].apply(badge)
    cols = st.columns(3)
    medals = ["🥇 1st place","🥈 2nd place","🥉 3rd place"]
    for i, col in enumerate(cols):
        if i < len(board):
            row = board.iloc[i]
            col.metric(medals[i], row["Nickname"], f'{row["Percentage"]:.1f}%')
    st.dataframe(board, hide_index=True, use_container_width=True)
    st.caption("A shared leaderboard across different users/devices requires a database and extra privacy safeguards.")

else:
    st.title("ℹ️ About this project")
    st.markdown("**Project:** Academic Performance Predictor Using Machine Learning  \n**School:** Bharatiya Vidya Bhavan  \n**Class:** XII  \n**AI teacher:** Murali Sankar V.K.  \n**Team:** R. Devdutt, Rishabh Nair, Kashinath JS, Abhiram S")
    st.subheader("How it works")
    st.write("The prototype uses Linear Regression from scikit-learn. A separate model is created for each subject using generated synthetic example records.")
    st.write("Subject selection: English, Physics and Chemistry are common; choose Mathematics or Psychology, choose Biology or Computer Science, then choose a sixth subject. Duplicate choices are removed from the sixth-subject menu.")
    st.info("Percentage is marks obtained divided by total maximum marks, multiplied by 100. Percentile compares a student's result with a reference group and is not calculated by this prototype.")
    st.subheader("Limitations")
    st.markdown("- Synthetic data only; no real student records are included.\n- Predictions are illustrative, not guaranteed.\n- Leaderboard is session-only in this starter version.\n- Obtain permission and protect privacy before collecting real student data.")
    st.dataframe(pd.DataFrame([{"Subject":s,"Maximum marks":m} for s,m in SUBJECT_MAX.items()]), hide_index=True, use_container_width=True)
