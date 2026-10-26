"""
SWYNEX Final AI Application - Standalone Flask Web Server & REST API
Provides a clean, modern web application running on http://127.0.0.1:5000
with interactive AJAX analysis, sample announcement loaders, and live benchmark evaluation.
"""

import sys
from pathlib import Path
from flask import Flask, render_template, request, jsonify

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src import analyze_announcement, CATEGORIES
from evaluation.evaluate import run_evaluation, load_evaluation_cases

app = Flask(__name__)


# Curated presets for one-click UI testing
PRESET_ANNOUNCEMENTS = {
    "exam": {
        "title": "Semester 5 End-Semester Exam Timetable",
        "category": "Exam",
        "text": (
            "The End-Semester Examination timetable for B.Tech Semester 5 is officially released. "
            "All students must download admit cards before Friday 5:00 PM at https://exam.university.edu. "
            "Students without printed hall tickets will be debarred from entering the examination hall."
        ),
    },
    "assignment": {
        "title": "Machine Learning Assignment 3 Cutoff",
        "category": "Assignment",
        "text": (
            "Submission of Machine Learning Assignment 3 on Neural Networks is due tomorrow by 11:59 PM "
            "on Google Classroom. Late submissions will receive zero marks. Please ensure your code runs cleanly."
        ),
    },
    "placement": {
        "title": "Microsoft Campus Recruitment Drive",
        "category": "Placement",
        "text": (
            "Microsoft Campus Placement Drive 2026: Eligible B.Tech 7th semester students with CGPA >= 8.0 "
            "must register on the CDC portal before tomorrow 12:00 PM. Technical interviews commence Thursday 9:00 AM."
        ),
    },
    "internship": {
        "title": "Tech Mahindra 6-Month Stipend Internship",
        "category": "Internship",
        "text": (
            "Winter Internship Opportunity at Tech Mahindra: 6-month industrial internship with a stipend of "
            "Rs 25,000/month. Apply before November 10 at intern@techmahindra.com. Open to 3rd and 4th year students."
        ),
    },
    "holiday": {
        "title": "Severe Cyclone Alert - Emergency Closure",
        "category": "Holiday",
        "text": (
            "Emergency Closure: Due to severe cyclone alert issued by disaster management authorities, "
            "the campus will be evacuated today by 2:00 PM. All evening laboratories and sports activities are cancelled."
        ),
    },
    "event": {
        "title": "National Hackathon 'HackSphere 2026'",
        "category": "Event",
        "text": (
            "Annual Inter-College Hackathon 'HackSphere 2026' registration is now open! Win cash prizes up to "
            "Rs 1,00,000. Register your team at https://hacksphere.dev before November 5."
        ),
    },
    "general": {
        "title": "Biometric Smart ID Card Collection",
        "category": "General",
        "text": (
            "All students must collect their renewed biometric smart ID cards from the administrative office "
            "counter 4 between 10:00 AM and 1:00 PM on working days."
        ),
    },
    "edge_case": {
        "title": "Routine Health Clinic (Urgent Care)",
        "category": "General",
        "text": (
            "The urgent care first-aid health clinic is located on the ground floor next to the student cafeteria. "
            "Regular doctor consultation hours are 9:00 AM to 5:00 PM on weekdays."
        ),
    },
}


@app.route("/")
def index():
    """Serves the main application landing page."""
    return render_template("index.html", categories=CATEGORIES, samples=PRESET_ANNOUNCEMENTS)


@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    """Analyzes announcement text received as JSON or form data."""
    if request.is_json:
        data = request.get_json(silent=True) or {}
        text = data.get("text", "")
    else:
        text = request.form.get("text", "")

    result = analyze_announcement(text)
    return jsonify(result)


@app.route("/api/samples", methods=["GET"])
def api_samples():
    """Returns preset sample announcements."""
    return jsonify(PRESET_ANNOUNCEMENTS)


@app.route("/api/evaluate", methods=["GET"])
def api_evaluate():
    """Executes benchmark evaluation across all test cases and returns metrics."""
    try:
        eval_result = run_evaluation()
        # Convert dataframe to records for JSON serialization
        df_records = eval_result["results_dataframe"].to_dict(orient="records")
        response = {
            "success": True,
            "total_test_cases": eval_result["total_test_cases"],
            "standard_cases_count": eval_result["standard_cases_count"],
            "edge_cases_count": eval_result["edge_cases_count"],
            "category_accuracy": eval_result["category_accuracy"],
            "standard_category_accuracy": eval_result["standard_category_accuracy"],
            "edge_case_accuracy": eval_result["edge_case_accuracy"],
            "priority_accuracy": eval_result["priority_accuracy"],
            "deadline_accuracy": eval_result["deadline_accuracy"],
            "weighted_f1": eval_result["weighted_f1"],
            "classification_report": eval_result["classification_report"],
            "cases": df_records,
        }
        return jsonify(response)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    print("===============================================================")
    print(" SWYNEX Final AI Application - Student Announcement Intelligence")
    print(" Web Server running at: http://127.0.0.1:5000")
    print(" Press Ctrl+C to stop.")
    print("===============================================================")
    app.run(host="127.0.0.1", port=5000, debug=False)
