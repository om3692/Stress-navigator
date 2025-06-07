Mindwell Navigator
Mindwell Navigator is a comprehensive mental wellness assessment web application built with Flask. It guides users through a series of questions to evaluate their well-being across different categories and provides personalized insights, summaries, and actionable recommendations based on their responses.

About The Project
This application is designed to be a private and user-friendly tool for individuals to self-assess their mental state. It handles user sessions, obtains consent, presents a multi-step assessment, and generates a detailed results page. The backend logic interprets the assessment responses to create meaningful feedback for the user.

Key Features
User Session Management: Creates and manages a unique session for each user assessment.
Consent First: Requires users to agree to a consent and disclaimer form before beginning the assessment.
Guided Assessment: Presents a clear, multi-question assessment one question at a time.
Dynamic Result Interpretation: Analyzes user responses to calculate scores for various wellness categories (e.g., Sleep Quality, Motivation).
Personalized Feedback: Generates a custom summary, category-specific insights, and tailored recommendations based on assessment results.
Data Persistence: Saves session data and individual responses to a SQLite database.
Modular Architecture: The code is organized into distinct modules for routing (app.py), business logic (assessment_logic.py), and data models (models.py).
CLI for Database Management: Includes a command-line command to initialize the database schema.
Getting Started
Follow these instructions to set up and run the project on your local machine.

Prerequisites
Python 3.7+
pip (Python package installer)
Installation
Clone the repository:

Bash

git clone <your-repository-url>
cd mindwell-navigator
Create and activate a virtual environment (recommended):

Bash

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate

# For Windows
py -m venv venv
.\venv\Scripts\activate
Install the required dependencies:
The application relies on Flask and Flask-SQLAlchemy.

Bash

pip install Flask Flask-SQLAlchemy
Project Structure
The project follows a standard Flask application structure. The assessment questions and recommendation content are loaded from external JSON files.

/
|-- instance/
|   `-- wellness_data.db      # SQLite database file (created after init)
|-- data/
|   |-- questions.json          # Contains all assessment questions
|   `-- recommendations_content.json # Contains content for results page
|-- templates/                  # (Inferred) HTML templates for the UI
|   |-- index.html
|   |-- consent_disclaimer.html
|   |-- assessment_page.html
|   |-- results_page.html
|   |-- ...
|-- app.py                      # Main Flask application file
|-- assessment_logic.py         # Handles result interpretation
|-- models.py                   # Defines database schema
Usage
Initialize the Database:
Before running the application for the first time, you must create the database tables. Run the following command from your terminal in the project's root directory:

Bash

flask init-db
This command will create an instance folder and the wellness_data.db database file inside it.

Run the Application:
Start the Flask development server with the following command:

Bash

python app.py
The application will be running in debug mode.

Access the Tool:
Open your web browser and navigate to:

http://127.0.0.1:5000
How It Works
Session & Consent: When a user first visits the site, a new session is created in the database. They are directed to a consent page, and their agreement is recorded before they can proceed.
Assessment: The user is guided through a series of questions loaded from data/questions.json. Each response is saved to the database, linked to their session ID.
Interpretation: Once all questions are answered, the application redirects to the results page. The interpret_results function from assessment_logic.py is called, which processes the dictionary of responses. It calculates average scores for each category and uses predefined thresholds in data/recommendations_content.json to generate insights and advice.
Displaying Results: The results page (/results) displays the generated summary, category insights, and personalized recommendations. The final summary is also saved back to the UserSession table in the database.
Database Models
The application uses a SQLite database with two main tables defined in models.py.

UserSession: Represents a single, complete interaction by a user.

id (String): A unique UUID for the session.
start_time (DateTime): Timestamp when the session was created.
end_time (DateTime): Timestamp when the user viewed their results.
consent_agreed (Boolean): Stores whether the user gave consent.
assessment_summary_text (Text): Stores the final generated summary text.
Response: Represents a single answer to a single question.

id (Integer): The primary key for the response.
user_session_id (String): A foreign key linking the response to the UserSession.
question_id (String): An identifier for the question being answered.
question_text (String): The full text of the question.
answer_text (String): The text of the option chosen by the user.
answer_value (Integer): The numerical value of the answer, used for scoring.
category (String): The wellness category the question belongs to.
timestamp (DateTime): Timestamp when the answer was submitted.
