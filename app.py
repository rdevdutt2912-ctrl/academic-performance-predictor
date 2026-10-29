import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

st.set_page_config(page_title="StudySpark | Academic Predictor", page_icon="🎓", layout="wide")

SUBJECT_MAX = {
    # Senior-secondary demonstration maximums; confirm school-specific assessment schemes.
    "English": 80, "Physics": 70, "Chemistry": 70, "Biology": 70,
    "Mathematics": 70, "Applied Mathematics": 80, "Computer Science": 70,
    "Psychology": 80, "Information Technology (IT)": 70,
    "Physical Education (PE)": 70, "Artificial Intelligence (AI)": 50,
    "Accountancy": 80, "Business Studies": 80, "Economics": 80,
    "Entrepreneurship": 80, "Informatics Practices (IP)": 70,
    "History": 80, "Political Science": 80, "Geography": 80,
    "Sociology": 80, "Legal Studies": 80, "Philosophy": 80,
    "Biotechnology": 70, "Engineering Graphics": 70,
    "Home Science": 70, "Fashion Studies": 70, "Mass Media Studies": 70,
    "Yoga": 70, "Web Applications": 70, "Fine Arts / Painting": 70,
    "Music": 70, "Dance / Theatre": 70, "French": 80, "Sanskrit": 80,
    "Hindi": 80, "Urdu": 80, "Japanese": 80,
}

GRADE_GROUPS = ["Classes 1–5", "Classes 6–9", "Class 10", "Classes 11–12"]
PRIMARY_SUBJECTS = [
    "English", "Hindi", "Other Language", "Mathematics",
    "Environmental Studies (EVS)", "Computer Studies", "Art Education",
    "Physical Education (PE)", "General Knowledge", "Music",
]
MIDDLE_SUBJECTS = [
    "English", "Hindi", "Sanskrit", "Other Language", "Mathematics",
    "Science", "Social Science", "Computer Studies", "Computer Applications (Code 165)",
    "Information Technology (Code 402)", "Artificial Intelligence (Code 417)",
    "Art Education", "Physical Education (PE)", "Home Science (Code 064)",
    "Economics", "Music", "Third Language",
]
CLASS10_CORE = ["Language 1", "Language 2", "Mathematics", "Science", "Social Science"]
CLASS10_OPTIONALS = [
    "Artificial Intelligence (Code 417)", "Information Technology (Code 402)",
    "Introduction to Financial Markets (Code 405)", "Tourism (Code 406)",
    "Data Science", "Healthcare", "Retail", "Design Thinking", "Kaushal Vikas",
    "Other NSQF-certified vocational subject", "Computer Applications (Code 165)",
    "Home Science (Code 064)", "Fine Arts / Painting", "Music",
    "NCC (Code 076)", "Sanskrit", "French", "German", "Spanish",
    "Regional Indian Language",
]
SENIOR_STREAM_SUBJECTS = {
    "Science": [
        "English", "Hindi", "Physics", "Chemistry", "Biology", "Mathematics",
        "Applied Mathematics", "Computer Science", "Informatics Practices (IP)",
        "Psychology", "Economics", "Physical Education (PE)", "Entrepreneurship",
        "Artificial Intelligence (AI)", "Data Science", "Biotechnology",
        "Engineering Graphics", "Home Science", "Fine Arts / Painting", "Music",
        "French", "Sanskrit", "Japanese",
    ],
    "Commerce": [
        "English", "Hindi", "Accountancy", "Business Studies", "Economics",
        "Mathematics", "Applied Mathematics", "Entrepreneurship",
        "Informatics Practices (IP)", "Computer Science", "Psychology",
        "Physical Education (PE)", "Artificial Intelligence (AI)", "Data Science",
        "Legal Studies", "Fashion Studies", "Home Science", "Mass Media Studies",
        "Yoga", "Web Applications", "Fine Arts / Painting", "Music", "French", "Sanskrit",
    ],
    "Humanities": [
        "English", "Hindi", "History", "Political Science", "Geography", "Economics",
        "Psychology", "Sociology", "Philosophy", "Legal Studies", "Mathematics",
        "Applied Mathematics", "Computer Science", "Informatics Practices (IP)",
        "Physical Education (PE)", "Entrepreneurship", "Artificial Intelligence (AI)",
        "Data Science", "Home Science", "Fashion Studies", "Mass Media Studies",
        "Yoga", "Fine Arts / Painting", "Music", "Dance / Theatre", "French", "Sanskrit", "Urdu",
    ],
}

DEFAULT_SUBJECTS = {
    "Classes 1–5": ["English", "Hindi", "Mathematics", "Environmental Studies (EVS)", "Computer Studies", "Art Education"],
    "Classes 6–9": ["English", "Hindi", "Mathematics", "Science", "Social Science", "Computer Studies"],
    "Class 10": CLASS10_CORE + ["Artificial Intelligence (Code 417)"],
    "Science": ["English", "Physics", "Chemistry", "Biology", "Mathematics", "Computer Science"],
    "Commerce": ["English", "Accountancy", "Business Studies", "Economics", "Mathematics", "Entrepreneurship"],
    "Humanities": ["English", "History", "Political Science", "Geography", "Economics", "Psychology"],
}

# CBSE offerings and assessment schemes vary by class, school, and academic year.
# Subject choices and marks here are configurable demonstration options, not an official guarantee.
def subject_maximum(subject, grade_group):
    if grade_group in ("Classes 1–5", "Classes 6–9", "Class 10"):
        return 100  # simple demonstration scale; schools may use different assessment schemes
    return SUBJECT_MAX.get(subject, 70)

st.markdown("""
<style>
.block-container {padding-top:1.5rem}
/* Metric cards: use dark text on a light background so values stay readable in every theme. */
div[data-testid="stMetric"] {
    background: #f3f4f6 !important;
    color: #111827 !important;
    border: 1px solid #d1d5db !important;
    padding: 12px !important;
    border-radius: 14px !important;
}
div[data-testid="stMetric"] label,
div[data-testid="stMetric"] [data-testid="stMetricLabel"],
div[data-testid="stMetric"] [data-testid="stMetricValue"],
div[data-testid="stMetric"] [data-testid="stMetricDelta"],
div[data-testid="stMetric"] p,
div[data-testid="stMetric"] span,
div[data-testid="stMetric"] svg {
    color: #111827 !important;
    fill: #111827 !important;
}
.hero {background:linear-gradient(120deg,#352a86,#6558d3,#a78bfa);color:white;padding:26px;border-radius:18px}
</style>
""", unsafe_allow_html=True)

st.sidebar.title("🎓 StudySpark")
st.sidebar.caption("Academic Performance Predictor")
page = st.sidebar.radio("Choose a page", ["🏠 Home", "📘 Predict one subject", "📊 Overall performance", "🏆 Leaderboard", "ℹ️ About"])
st.sidebar.caption("Class XII AI project prototype")

def subject_choices(prefix):
    """Choose a grade group, then a stream or age-appropriate subject combination."""
    grade_group = st.selectbox(
        "Choose your class group", GRADE_GROUPS, key=f"{prefix}_grade_group",
        help="Choose Classes 1–5, Classes 6–9, Class 10, or Classes 11–12.",
    )

    if grade_group == "Classes 11–12":
        stream = st.selectbox(
            "Choose your stream", list(SENIOR_STREAM_SUBJECTS.keys()),
            key=f"{prefix}_stream", help="Choose Science, Commerce, or Humanities.",
        )
        available = SENIOR_STREAM_SUBJECTS[stream]
        default_key = stream
        state_key = f"{prefix}_subjects"
        current = st.session_state.get(state_key, DEFAULT_SUBJECTS[default_key])
        current = [x for x in current if x in available]
        for x in DEFAULT_SUBJECTS[default_key]:
            if len(current) >= 6:
                break
            if x in available and x not in current:
                current.append(x)
        st.session_state[state_key] = current[:6]
        subjects = st.multiselect(
            "Select subjects for your report (choose 5–7)", available, key=state_key,
            help="Actual subject combinations depend on school offerings and CBSE rules.",
        )
        if not 5 <= len(subjects) <= 7:
            st.warning(f"Select between 5 and 7 subjects. Currently selected: {len(subjects)}.")
        return subjects, grade_group

    if grade_group == "Class 10":
        st.caption("Class 10 core subjects are included automatically. Choose any additional elective(s) offered by your school.")
        lang1 = st.selectbox("Language 1", ["English", "Hindi", "Sanskrit", "Other Language"], key=f"{prefix}_lang1")
        lang2_options = ["Hindi", "Sanskrit", "French", "German", "Spanish", "Regional Indian Language", "Other Language", "English"]
        lang2 = st.selectbox("Language 2", [x for x in lang2_options if x != lang1], key=f"{prefix}_lang2")
        optionals = st.multiselect(
            "Optional 6th/7th subject(s)", CLASS10_OPTIONALS,
            default=["Artificial Intelligence (Code 417)"], key=f"{prefix}_class10_optionals",
            help="Select only subjects your school offers. Some options may have specific CBSE codes or availability requirements.",
        )
        subjects = [f"Language 1 — {lang1}", f"Language 2 — {lang2}", "Mathematics", "Science", "Social Science"] + optionals
        return subjects, grade_group

    available = PRIMARY_SUBJECTS if grade_group == "Classes 1–5" else MIDDLE_SUBJECTS
    default_key = grade_group
    state_key = f"{prefix}_subjects"
    current = st.session_state.get(state_key, DEFAULT_SUBJECTS[default_key])
    current = [x for x in current if x in available]
    for x in DEFAULT_SUBJECTS[default_key]:
        if len(current) >= 6:
            break
        if x in available and x not in current:
            current.append(x)
    st.session_state[state_key] = current[:6]
    subjects = st.multiselect(
        "Select subjects for your report", available, key=state_key,
        help="These are broad example options. Your school's exact curriculum may differ.",
    )
    if not subjects:
        st.warning("Select at least one subject to continue.")
    st.caption("Subject names and assessment methods can vary between schools. Confirm the exact list with your school.")
    return subjects, grade_group

def build_model(subject, grade_group):
    # Synthetic demo data only. Not real student records.
    rng = np.random.default_rng(2026 + sum(ord(c) for c in subject))
    maximum = subject_maximum(subject, grade_group)
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

def predict(subject, previous, hours, attendance, assignments, grade_group):
    model = build_model(subject, grade_group)
    x = pd.DataFrame([{"previous": previous, "hours": hours, "attendance": attendance, "assignments": assignments}])
    return float(np.clip(model.predict(x)[0], 0, subject_maximum(subject, grade_group)))

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
    subjects, grade_group = subject_choices("one")
    if not 5 <= len(subjects) <= 7:
        st.info("Select between five and seven subjects above to continue.")
    else:
        subject = st.selectbox("Subject to predict", subjects)
        maximum = subject_maximum(subject, grade_group)
        st.caption(f"Maximum marks for {subject}: {maximum}")
        with st.form("one_form"):
            previous = st.number_input(f"Previous marks (out of {maximum})", 0.0, float(maximum), float(round(maximum*.65)), 1.0)
            hours = st.slider("Study hours per day", 0.0, 12.0, 3.0, .5)
            attendance = st.slider("Attendance (%)", 0, 100, 85)
            assignments = st.slider("Assignments completed (%)", 0, 100, 80)
            go = st.form_submit_button("✨ Predict my marks", type="primary", use_container_width=True)
        if go:
            score = predict(subject, previous, hours, attendance, assignments, grade_group)
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
    subjects, grade_group = subject_choices("all")
    if not 5 <= len(subjects) <= 7:
        st.info("Select between five and seven subjects above to enter marks and calculate your overall performance.")
    else:
        st.write("Enter previous marks for each selected subject. The maximum is shown beside each subject.")
        with st.form("overall_form"):
            hours = st.slider("Average study hours per day", 0.0, 12.0, 3.0, .5)
            attendance = st.slider("Attendance (%)", 0, 100, 85)
            assignments = st.slider("Assignments completed (%)", 0, 100, 80)
            marks = {}
            left, right = st.columns(2)
            for i, subject in enumerate(subjects):
                with (left if i % 2 == 0 else right):
                    maximum = subject_maximum(subject, grade_group)
                    marks[subject] = st.number_input(f"{subject} (out of {maximum})", 0.0, float(maximum), float(round(maximum*.65)), 1.0, key="marks_"+subject)
            go = st.form_submit_button("🏆 Calculate my overall estimate", type="primary", use_container_width=True)
        if go:
            rows = []
            for subject in subjects:
                maximum = subject_maximum(subject, grade_group)
                score = predict(subject, marks[subject], hours, attendance, assignments, grade_group)
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
    st.write("Subject selection: choose Class 1 through Class 12. Classes 11–12 include Science, Commerce, and Humanities stream options. Class 10 includes five core subjects and optional/elective choices based on the supplied CBSE subject list. These are configurable examples; confirm exact offerings and assessment patterns with your school.")
    st.info("For Classes 1–10, this prototype uses a 100-mark demo scale per subject. For Classes 11–12, it uses configured illustrative subject maximums. Actual school and CBSE assessment schemes may differ. Percentage is marks obtained divided by total maximum marks, multiplied by 100; percentile is not calculated.")
    st.subheader("Limitations")
    st.markdown("- Synthetic data only; no real student records are included.\n- Predictions are illustrative, not guaranteed.\n- Leaderboard is session-only in this starter version.\n- Obtain permission and protect privacy before collecting real student data.")
    st.dataframe(pd.DataFrame([{"Subject":s,"Maximum marks":m} for s,m in SUBJECT_MAX.items()]), hide_index=True, use_container_width=True)
