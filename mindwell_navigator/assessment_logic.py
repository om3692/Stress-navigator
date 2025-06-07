# mindwell_navigator/assessment_logic.py
import json

RECOMMENDATIONS_DATA = {}
ALL_QUESTIONS_LIST = []

def load_assessment_data_files():
    global RECOMMENDATIONS_DATA, ALL_QUESTIONS_LIST
    try:
        with open('data/questions.json', 'r', encoding='utf-8') as f:
            questions_data = json.load(f)
            ALL_QUESTIONS_LIST = questions_data.get("questions", [])
        with open('data/recommendations_content.json', 'r', encoding='utf-8') as f:
            RECOMMENDATIONS_DATA = json.load(f)
    except FileNotFoundError as e:
        print(f"Error loading data files: {e}. Ensure 'questions.json' and 'recommendations_content.json' are in the 'data' directory.")
        # Initialize with empty structures to prevent crashes, though functionality will be limited
        ALL_QUESTIONS_LIST = []
        RECOMMENDATIONS_DATA = {"categories": {}, "general_wellbeing_tip": "Data files not found."}
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from data files: {e}")
        ALL_QUESTIONS_LIST = []
        RECOMMENDATIONS_DATA = {"categories": {}, "general_wellbeing_tip": "Error in data file format."}


# Call it once when the module is loaded
load_assessment_data_files()


def interpret_results(responses_dict):
    """
    Interprets user responses to generate a summary and personalized recommendations.

    Args:
        responses_dict (dict): A dictionary of responses, where keys are question_ids
                               and values are dicts like:
                               {'value': int, 'text': str, 'question_text': str, 'category': str}

    Returns:
        tuple: (final_summary_str, category_insights, personalized_recommendations_dict)
    """
    category_scores = {}
    category_question_counts = {} # To count how many questions per category were answered
    overall_summary_parts = []
    category_insights_text = {} # To store more detailed text per category
    personalized_recommendations_dict = {
        "specific_by_category": [], # Will store {category_name, advice_text}
        "general_sleep_hygiene": RECOMMENDATIONS_DATA.get("sleep_hygiene_tips_general", []),
        "general_cognitive_exercises": RECOMMENDATIONS_DATA.get("cognitive_exercises_general", []),
        "general_nutrition_tips": RECOMMENDATIONS_DATA.get("nutrition_tips_general", []),
        "general_wellbeing": [RECOMMENDATIONS_DATA.get("general_wellbeing_tip", "Remember to prioritize your well-being.")]
    }

    # Calculate sum of scores and count of questions per category from responses
    for q_id, resp_data in responses_dict.items():
        category = resp_data.get('category')
        value = resp_data.get('value')
        if category and isinstance(value, int):
            category_scores[category] = category_scores.get(category, 0) + value
            category_question_counts[category] = category_question_counts.get(category, 0) + 1

    # Calculate average scores per category
    avg_category_scores = {}
    for cat, total_score in category_scores.items():
        count = category_question_counts.get(cat, 1) # Avoid division by zero
        if count > 0:
            avg_category_scores[cat] = total_score / count

    # --- Generate Summary and Recommendations based on average scores ---
    for category_name, avg_score in avg_category_scores.items():
        if category_name in RECOMMENDATIONS_DATA["categories"]:
            cat_config = RECOMMENDATIONS_DATA["categories"][category_name]
            insight_text = ""
            advice_text = ""

            # Determine level based on thresholds. Assumes higher score = more severe.
            # Thresholds are 'upper bounds' for a level.
            if avg_score <= cat_config.get("low_threshold", 1): # Default if threshold missing
                insight_text = cat_config.get("low", f"Levels of {category_name.lower()} seem to be low.")
                advice_text = cat_config.get("low")
            elif avg_score <= cat_config.get("mild_threshold", 2.5):
                insight_text = cat_config.get("mild", f"Some mild signs regarding {category_name.lower()} are indicated.")
                advice_text = cat_config.get("mild")
            elif avg_score <= cat_config.get("moderate_threshold", 4):
                insight_text = cat_config.get("moderate", f"Moderate levels concerning {category_name.lower()} are suggested.")
                advice_text = cat_config.get("moderate")
            else: # High
                insight_text = cat_config.get("high", f"High levels of {category_name.lower()} may be present.")
                advice_text = cat_config.get("high")

            # Special handling for Sleep Quality (lower score is better)
            if category_name == "Sleep Quality":
                if avg_score <= cat_config.get("good_threshold", 1): # e.g. Very Good, Good
                    insight_text = cat_config.get("good", "Sleep quality appears to be good.")
                    advice_text = cat_config.get("good")
                elif avg_score <= cat_config.get("fair_threshold", 2.5): # Fair
                    insight_text = cat_config.get("fair", "Sleep quality seems fair.")
                    advice_text = cat_config.get("fair")
                elif avg_score <= cat_config.get("poor_threshold", 4): # Poor
                    insight_text = cat_config.get("poor", "Sleep quality appears to be poor.")
                    advice_text = cat_config.get("poor")
                else: # Very Poor
                    insight_text = cat_config.get("very_poor", "Sleep quality seems very poor.")
                    advice_text = cat_config.get("very_poor")
            
            # Special handling for Motivation (higher score means MORE problem, e.g. "little interest")
            # Or Emotional Well-being "hopeful" (higher score means LESS hopeful)
            # The current questions.json values are: higher value = more problem. So this generic logic should mostly work.
            # The text in recommendations_content.json should reflect this.

            category_insights_text[category_name] = insight_text
            if advice_text:
                 personalized_recommendations_dict["specific_by_category"].append({
                    "category": category_name,
                    "advice": advice_text
                })
            
            # Construct overall summary parts from insights
            # Make it more conversational
            if "seem to be" in insight_text or "appears to be" in insight_text or "are suggested" in insight_text or "may be present" in insight_text:
                summary_friendly_insight = insight_text.lower().replace(f"{category_name.lower()} levels", "") \
                                                        .replace("your responses suggest", "") \
                                                        .replace("it seems", "") \
                                                        .replace("it appears", "") \
                                                        .replace("are indicated", "") \
                                                        .replace("are suggested", "") \
                                                        .replace("may be present", "").strip()
                if summary_friendly_insight.startswith("you"):
                     overall_summary_parts.append(f"For {category_name.lower()}, {summary_friendly_insight}.")
                else:
                    overall_summary_parts.append(f"For {category_name.lower()}, it seems {summary_friendly_insight}.")

            else: # more direct statements
                 overall_summary_parts.append(f"Regarding {category_name.lower()}, {insight_text.lower()}.")


    final_summary_str = "Based on your responses: "
    if not overall_summary_parts:
        final_summary_str = "Thank you for completing the assessment. We've gathered some general tips that you might find helpful."
    else:
        # Capitalize the first letter of each part if it makes sense, or join as is.
        # For simplicity, joining directly.
        final_summary_str += " ".join(overall_summary_parts)

    # Append general wellbeing tip to the summary if not already too long
    if len(final_summary_str) < 300 and personalized_recommendations_dict["general_wellbeing"]: # Arbitrary length
         final_summary_str += f" {personalized_recommendations_dict['general_wellbeing'][0]}"


    return final_summary_str, category_insights_text, personalized_recommendations_dict