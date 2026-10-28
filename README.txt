StudySpark — Academic Performance Predictor

HOW TO RUN (Windows + Anaconda):
1. Extract this ZIP file.
2. Open Anaconda Prompt.
3. Use File Explorer to open the Academic_Performance_Predictor folder, click the address bar, and copy the folder path.
4. In Anaconda Prompt, run: cd "PASTE-YOUR-FOLDER-PATH-HERE"
5. Install dependencies: python -m pip install -r requirements.txt
6. Start the website: python -m streamlit run app.py
7. Open the local URL shown in the terminal (usually http://localhost:8501).

FEATURES:
- Switch between Mathematics and Psychology.
- Switch between Biology and Computer Science.
- Choose a sixth subject from AI, IT, PE, Psychology, Mathematics, Biology and Computer Science; choices already selected as core subjects are filtered out.
- Predict one subject or estimate overall performance across six subjects.
- Show entered-mark percentage separately from model-estimated percentage.
- Graphs, CSV export, badges and a session-only demo leaderboard.

IMPORTANT LIMITATIONS:
- The prediction model uses synthetic demo data, not real student records. Predictions are illustrative and are not validated forecasts.
- Actual percentage = entered marks total / maximum marks total * 100.
- Percentile is a comparison against a reference group and is not calculated by this prototype.
- The leaderboard is stored only in the current session and is not a shared online ranking.
