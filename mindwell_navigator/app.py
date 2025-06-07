# mindwell_navigator/app.py

import os
from flask import Flask, render_template, request, redirect, url_for, session, g, flash, jsonify # Added jsonify
from datetime import datetime

# --- App Initialization (Part 1 - Create Flask app object) ---
# We need 'app' object to exist to use app.root_path or app.instance_path
app = Flask(__name__) #
print(f"DEBUG: Flask app created. app.root_path is: {app.root_path}") #
print(f"DEBUG: Flask app.instance_path is: {app.instance_path}") #

# --- Database Directory and Path Configuration ---
instance_folder_path = os.path.join(app.root_path, 'instance') #
print(f"DEBUG: Determined instance folder path (using app.root_path): {instance_folder_path}") #

if not os.path.exists(instance_folder_path): #
    try:
        os.makedirs(instance_folder_path) #
        print(f"SUCCESS: Created instance folder at: {instance_folder_path}") #
    except OSError as e:
        print(f"CRITICAL ERROR: Could not create instance folder at {instance_folder_path}. Error: {e}") #
else:
    print(f"DEBUG: Instance folder already exists at: {instance_folder_path}") #

db_file_name = 'wellness_data.db' #
absolute_db_path = os.path.join(instance_folder_path, db_file_name) #
print(f"DEBUG: Absolute database file path determined as: {absolute_db_path}") #

# --- Flask App Configuration (Part 2 - After instance folder is handled) ---
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'dev_fallback_super_secret_key_123!@#') #
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{absolute_db_path}' #
print(f"DEBUG: SQLALCHEMY_DATABASE_URI set to: {app.config['SQLALCHEMY_DATABASE_URI']}") #
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #


# --- Import Local Modules & Initialize Extensions (AFTER app config) ---
from models import db, UserSession, Response #
from assessment_logic import ALL_QUESTIONS_LIST, interpret_results, load_assessment_data_files #

db.init_app(app) #
print("DEBUG: SQLAlchemy initialized with app.") #

@app.context_processor
def inject_now(): #
    return {'now': datetime.utcnow()} #

def get_current_user_session_record(): #
    session_id = session.get('user_session_id') #
    user_session_record = None #
    if session_id: #
        user_session_record = UserSession.query.get(session_id) #

    if not user_session_record: #
        user_session_record = UserSession() #
        db.session.add(user_session_record) #
        try:
            db.session.commit() #
            session['user_session_id'] = user_session_record.id #
            session['consent_agreed'] = False #
            session.modified = True #
            print(f"DEBUG: New UserSession created and committed: {user_session_record.id}") #
        except Exception as e:
            db.session.rollback() #
            print(f"ERROR: Creating new UserSession in DB: {e}") #
            flash("There was an issue starting your session. Please try again.", "error") #
            return None #
    return user_session_record #

@app.before_request
def ensure_session_user_and_load_data(): #
    if 'user_session_id' not in session: #
        get_current_user_session_record() #

    g.user_session = UserSession.query.get(session.get('user_session_id')) if session.get('user_session_id') else None #
    
    if not ALL_QUESTIONS_LIST: #
        load_assessment_data_files() #
        if not ALL_QUESTIONS_LIST: #
            print("CRITICAL ERROR: Assessment questions could not be loaded from assessment_logic.py.") #

@app.route('/')
def index(): #
    session.pop('current_question_index', None) #
    session.pop('assessment_responses', None) #
    return render_template('index.html') #

@app.route('/consent', methods=['GET', 'POST'])
def consent(): #
    user_session_record = get_current_user_session_record() #
    if not user_session_record: #
         flash("Your session could not be started. Please try returning to the homepage.", "error") #
         return redirect(url_for('index')) #

    if request.method == 'POST': #
        if request.form.get('consent_checkbox'): #
            user_session_record.consent_agreed = True #
            try:
                db.session.commit() #
                session['consent_agreed'] = True #
                session['current_question_index'] = 0 #
                session['assessment_responses'] = {} #
                session.modified = True #
                return redirect(url_for('assessment_question')) #
            except Exception as e:
                db.session.rollback() #
                flash("Could not save consent. Please try again.", "error") #
                print(f"ERROR: Saving consent to DB: {e}") #
        else:
            flash("You must agree to the terms to proceed.", "warning") #
    return render_template('consent_disclaimer.html') #

@app.route('/assessment', methods=['GET', 'POST'])
def assessment_question(): #
    user_session_record = get_current_user_session_record() #
    if not user_session_record: #
         flash("Session expired or not found. Please start over.", "error") #
         return redirect(url_for('index')) #

    if not session.get('consent_agreed') or not user_session_record.consent_agreed: #
        flash("Please provide consent before starting the assessment.", "info") #
        return redirect(url_for('consent')) #

    if not ALL_QUESTIONS_LIST: #
        flash("Assessment questions are currently unavailable. Please try again later.", "error") #
        return redirect(url_for('index')) #

    current_q_idx = session.get('current_question_index', 0) #

    if request.method == 'POST': #
        if 'assessment_responses' not in session: #
            session['assessment_responses'] = {} #

        answered_question_id = request.form.get('question_id') #
        answer_value_str = request.form.get('answer_value') #
        # 'Youtubeed' was a typo in the original, assuming it meant 'question_details' or similar
        question_details = next((q for q in ALL_QUESTIONS_LIST if q['id'] == answered_question_id), None) #

        if question_details and answer_value_str is not None: #
            selected_option = next((opt for opt in question_details['options'] if str(opt['value']) == answer_value_str), None) #
            if selected_option: #
                answer_text = selected_option['text'] #
                answer_value_int = int(answer_value_str) #
                session['assessment_responses'][answered_question_id] = { #
                    "value": answer_value_int, "text": answer_text, #
                    "question_text": question_details['text'], "category": question_details['category'] #
                }
                session.modified = True #
                try:
                    response_entry = Response( #
                        user_session_id=user_session_record.id, question_id=answered_question_id, #
                        question_text=question_details['text'], answer_text=answer_text, #
                        answer_value=answer_value_int, category=question_details['category'] #
                    )
                    db.session.add(response_entry) #
                    db.session.commit() #
                except Exception as e:
                    db.session.rollback(); print(f"ERROR: Saving response to DB: {e}") #
                    flash("There was an issue saving your answer. Please try again.", "error") #
            else:
                flash("Invalid answer submitted. Please select an option.", "warning") #
                question_to_redisplay_idx = session.get('current_question_index', 1) - 1 #
                if question_to_redisplay_idx < 0: question_to_redisplay_idx = 0 #
                return render_template('assessment_page.html', #
                               question=ALL_QUESTIONS_LIST[question_to_redisplay_idx], #
                               question_number=question_to_redisplay_idx + 1, #
                               total_questions=len(ALL_QUESTIONS_LIST)) #
        
        # This logic was slightly off, it should increment current_q_idx *after* processing the current question's POST
        # and then redirect. The display of the next question happens on the subsequent GET.
        # The session['current_question_index'] is set before redirecting to GET.
        
        # If current_q_idx was the one just answered, next one is current_q_idx + 1
        next_question_to_show_idx = current_q_idx 
        if next_question_to_show_idx < len(ALL_QUESTIONS_LIST): #
             # This was incrementing too early in the original leading to skipping.
             # The current_q_idx for POST is the question just answered.
             # The session variable should point to the *next* question index to be displayed on GET.
            session['current_question_index'] = current_q_idx # This will be incremented in the GET part
            return redirect(url_for('assessment_question')) #
        else: # All questions answered
            return redirect(url_for('results')) #

    # GET request part
    if current_q_idx < len(ALL_QUESTIONS_LIST): #
        question_to_display = ALL_QUESTIONS_LIST[current_q_idx] #
        session['current_question_index'] = current_q_idx + 1 # Prepare for the *next* question after this one is displayed
        session.modified = True #
        return render_template('assessment_page.html', #
                               question=question_to_display, question_number=current_q_idx + 1, #
                               total_questions=len(ALL_QUESTIONS_LIST)) #
    else: # All questions done, or index out of bounds
        return redirect(url_for('results')) #


@app.route('/results')
def results(): #
    user_session_record = get_current_user_session_record() #
    if not user_session_record: #
         flash("Session expired or not found. Please start over.", "error"); return redirect(url_for('index')) #
    if not session.get('consent_agreed') or not user_session_record.consent_agreed: #
        flash("Cannot view results without prior consent.", "warning"); return redirect(url_for('consent')) #
    assessment_responses = session.get('assessment_responses', {}) #
    if not assessment_responses: #
        flash("No assessment responses found. Please complete the assessment first.", "info"); return redirect(url_for('index')) #

    final_summary, category_insights, personalized_recommendations_dict = interpret_results(assessment_responses) #
    user_session_record.assessment_summary_text = final_summary #
    user_session_record.end_time = datetime.utcnow() #
    try:
        db.session.commit() #
    except Exception as e:
        db.session.rollback(); print(f"ERROR: Saving final summary to DB: {e}") #

    # Prepare data for Spline visualization
    # This is an example; you'll need to decide what data makes sense.
    # Let's calculate average scores per category to pass to Spline
    category_scores = {}
    category_question_counts = {}
    for resp_data in assessment_responses.values():
        category = resp_data.get('category')
        value = resp_data.get('value')
        if category and isinstance(value, int):
            category_scores[category] = category_scores.get(category, 0) + value
            category_question_counts[category] = category_question_counts.get(category, 0) + 1
    
    avg_category_scores_for_spline = {}
    overall_score_sum = 0
    overall_score_count = 0
    for cat, total_score in category_scores.items():
        count = category_question_counts.get(cat, 1)
        if count > 0:
            avg_score = total_score / count
            avg_category_scores_for_spline[cat.replace(" ", "_")] = round(avg_score, 2) # Use JS-friendly keys
            overall_score_sum += avg_score
            overall_score_count +=1
    
    overall_avg_score_for_spline = round(overall_score_sum / overall_score_count, 2) if overall_score_count > 0 else 0

    results_data_for_spline = {
        "overallScore": overall_avg_score_for_spline, # Example overall score
        "categoryScores": avg_category_scores_for_spline, # Example category scores
        # Add any other data points your Spline scene might need
    }

    return render_template('results_page.html', #
                           summary=final_summary, insights=category_insights, #
                           recommendations=personalized_recommendations_dict, #
                           results_data_for_spline=results_data_for_spline)


@app.route('/privacy') #
def privacy(): return render_template('privacy_policy.html') #
@app.route('/terms') #
def terms(): return render_template('terms_of_service.html') #

@app.cli.command("init-db") #
def init_db_command(): #
    """Ensures instance folder exists and creates the database tables.""" #
    with app.app_context(): #
        try:
            print(f"DEBUG: Attempting db.create_all() via init-db for URI: {app.config['SQLALCHEMY_DATABASE_URI']}") #
            db.create_all() #
            print("SUCCESS: Database tables created (or already exist).") #
        except Exception as e:
            print(f"CRITICAL ERROR during db.create_all() in init-db: {e}") #
            print("Please check the database URI, instance folder permissions, and path.") #
    print(f"Database initialization process complete for {app.config.get('SQLALCHEMY_DATABASE_URI')}.") #

if __name__ == '__main__': #
    with app.app_context(): #
        try:
            print(f"DEBUG: Attempting db.create_all() via __main__ for URI: {app.config['SQLALCHEMY_DATABASE_URI']}") #
            db.create_all() #
            print("DEBUG: db.create_all() in __main__ completed.") #
        except Exception as e:
            print(f"ERROR during db.create_all() in __main__: {e}") #
    app.run(debug=True) #