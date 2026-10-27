# SWYNEX Final AI Application
## Student Announcement Intelligence System

An AI-powered application designed to help students understand college announcements by identifying important information, assigning priority levels, extracting deadlines, and generating concise summaries.

## 📌 Project Overview

College students receive many announcements about exams, assignments, events, holidays, and deadlines. Important information can sometimes be difficult to identify quickly.

The Student Announcement Intelligence System helps organize announcements and highlights information that students may need to review first.

This project was developed as part of **Task 4 – Final AI Application** for the SWYNEX internship.

## 🎯 Problem Statement

Students may miss important deadlines or spend too much time reading lengthy college announcements.

The goal of this project is to provide a simple interface that analyzes announcement text and presents useful information in an organized format.

## 💡 Solution

The application accepts announcement text and processes it to provide relevant information, such as:

- Announcement category
- Priority level
- Important dates and deadlines, where detectable
- A short summary
- Helpful error messages for invalid or empty inputs

The exact outputs depend on the features implemented in the application.

## ✨ Key Features

- **Announcement Analysis:** Processes user-provided announcement text.
- **Text Classification:** Categorizes announcements using the implemented classification method.
- **Priority Scoring:** Helps identify potentially urgent announcements.
- **Deadline Extraction:** Attempts to identify dates and deadlines.
- **Text Summarization:** Produces a concise summary using the implemented method.
- **Input Validation:** Handles empty or invalid inputs.
- **Demo Examples:** Supports testing with sample announcements.
- **Error Handling:** Displays useful messages when processing fails.

## 🛠️ Technologies Used

The technologies depend on the final implementation. A typical Python-based version may use:

- Python
- Streamlit for the web interface
- Pandas for data processing
- Scikit-learn for machine learning and text classification
- Regular expressions for date extraction
- Git and GitHub for version control

Only list libraries that are actually used in the project.

## 📂 Project Structure

Example structure:

```text
SWYNEX-Final-AI-Application/
├── app.py
├── requirements.txt
├── README.md
├── data/
├── models/
├── tests/
└── screenshots/
```

The actual folder structure may differ depending on the implementation.

## ⚙️ Installation and Setup

### Prerequisites

- Python 3.10 or another version supported by the project dependencies
- Git
- A code editor such as Antigravity

### Step 1: Clone the repository

```bash
git clone https://github.com/diya-34/SWYNEX-Final-AI-Application.git
```

### Step 2: Open the project directory

```bash
cd SWYNEX-Final-AI-Application
```

### Step 3: Create a virtual environment

Windows:

```bash
python -m venv venv
```

Activate it in PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### Step 4: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Run the application

If the main application file is `app.py` and the interface uses Streamlit:

```bash
streamlit run app.py
```

Follow the local URL displayed in the terminal to open the application in your browser.

Use the actual entry-point filename and commands from the project.

## 🧪 Example Input

```text
Notice: The Data Structures assignment must be submitted
by 30 October 2026. Late submissions may not be accepted.
```

## 📊 Expected Analysis

Depending on the implemented features, the application may identify:

- Category: Assignment
- Priority: High
- Deadline: 30 October 2026
- Summary: Students must submit the Data Structures assignment by the specified deadline.

This is an illustrative example, not a verified output or evaluation result.

## 🧑‍💻 Evaluation and Testing

The application should be tested with different types of announcements.

| Test case | Expected behavior |
|---|---|
| Normal announcement | Process the text and display available analysis |
| Assignment deadline | Attempt to identify the deadline |
| Empty input | Display an input validation message |
| Unclear announcement | Return a cautious or general result |
| Unexpected processing error | Display a useful error message |

Actual test results should be recorded after running the tests. No accuracy score should be reported unless it has been measured using an appropriate evaluation method.

## ⚠️ Limitations

- Text classification may produce incorrect categories.
- Priority scores may not reflect the actual urgency of an announcement.
- Date extraction may fail for ambiguous or unusual date formats.
- Automatically generated summaries may omit important details.
- Results depend on the quality and format of the input text.
- The application cannot guarantee that every deadline or important instruction is detected.

Students should always verify important information against official college announcements.

## 🔐 Ethical Considerations

- **Privacy:** Avoid entering confidential student information or personal data.
- **Accuracy:** Verify deadlines, exam schedules, and other critical information with official sources.
- **Fairness:** Test the application on different announcement formats and writing styles.
- **Transparency:** Explain that the output is machine-generated and may contain errors.
- **Responsible AI:** Use the application as an assistant, not as a replacement for official college communication.

## 🚀 Future Improvements

- Support multiple Indian languages.
- Improve classification using a larger, appropriately labeled dataset.
- Add notifications for upcoming deadlines.
- Improve date extraction and summary quality.
- Add a history of previously analyzed announcements.
- Evaluate model performance using labeled test data.

## 📸 Demo and Screenshots

Add screenshots of the actual working application to the `screenshots/` folder and embed them here.

Example:

```markdown
![Application Dashboard](screenshots/dashboard.png)
```

Replace the example image path with the correct screenshot filename.

## 📚 Learning Outcomes

Through this project, I aim to strengthen my understanding of:

- Python application development
- Natural Language Processing (NLP)
- Text classification and prioritization
- Input validation and error handling
- Testing and evaluation
- GitHub documentation
- Responsible and ethical AI development

## 👩‍💻 Author

**Diya Patel**

B.Tech – Artificial Intelligence and Machine Learning

GitHub: [diya-34](https://github.com/diya-34)

## 🏢 Internship

Developed for **SWYNEX Internship – Task 4: Final AI Application**.

## 📄 License

This project is intended for educational and learning purposes. Add an appropriate open-source license if you decide to distribute the project under one.
