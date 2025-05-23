import csv
import asyncio
from src.utils import ainvoke_llm, read_text_file # read_text_file is synchronous
from src.prompts import SCORE_JOBS_PROMPT
from src.structured_outputs import JobScores, JobScore # Assuming JobScore might be useful if JobScores is a list

# Helper function to read jobs from CSV
def read_jobs_from_csv(filename: str) -> list[dict]:
    jobs = []
    try:
        with open(filename, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                jobs.append(row)
    except FileNotFoundError:
        # Handled by the caller, but good to be aware
        raise
    except Exception as e:
        print(f"Error reading CSV file {filename}: {e}")
        return [] # Return empty list on other read errors
    return jobs

# Helper function to format a single job dictionary into a string for the LLM
def format_job_for_scoring(job_dict: dict) -> str:
    # Adapt this based on the fields present in your CSV and required by the prompt
    # This is similar to format_scraped_job_for_scoring but for a single job dict
    title = job_dict.get('title', '')
    description = job_dict.get('description', '')
    # skills = job_dict.get('skills', '') # Assuming 'skills' is a comma-separated string or similar
    # experience_level = job_dict.get('experience_level', '')
    # budget = job_dict.get('budget', '')
    # payment_rate = job_dict.get('payment_rate', '')
    
    # Construct a detailed string. Adjust fields as necessary.
    # Example:
    job_text = f"Title: {title}\n"
    job_text += f"Description: {description}\n"
    # if skills:
    #     job_text += f"Skills: {skills}\n"
    # if experience_level:
    #     job_text += f"Experience Level: {experience_level}\n"
    # if budget:
    #     job_text += f"Budget: {budget}\n"
    # if payment_rate:
    #     job_text += f"Payment Rate: {payment_rate}\n"
    
    # For simplicity, using only title and description as per the implied use in score_scraped_jobs
    # which calls format_scraped_job_for_scoring -> which is not shown but assumed to produce a list of strings
    # where each string is a job representation.
    # The user_message in src/nodes.py for SCORE_JOBS_PROMPT was:
    # user_message=f"Evaluate these Jobs:\n\n{jobs_list}"
    # where jobs_list was a string representation of multiple jobs.
    # Here, we are sending one job at a time.
    
    return job_text.strip()

# Helper function to write graded jobs (including scores) to CSV
def write_graded_jobs_to_csv(graded_jobs_data: list[dict], filename: str):
    if not graded_jobs_data:
        print("No graded job data to write.")
        return

    # Dynamically get fieldnames from the first dictionary to include all original and new fields
    # (e.g., 'score', 'reason' if added)
    try:
        fieldnames = list(graded_jobs_data[0].keys())
    except IndexError:
        print("Cannot determine CSV headers, no data in graded_jobs_data.")
        return
    
    # Ensure 'score' and 'reason' are part of fieldnames if they might exist
    # This handles cases where the first job might have failed scoring
    if 'score' not in fieldnames:
        fieldnames.append('score')
    if 'reasoning' not in fieldnames: # Assuming the Pydantic model uses 'reasoning'
        fieldnames.append('reasoning')


    try:
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for job_dict in graded_jobs_data:
                # Fill missing keys for rows that might not have all fields (e.g., failed scoring)
                for field_name in fieldnames:
                    job_dict.setdefault(field_name, None)
                writer.writerow(job_dict)
        print(f"Successfully wrote {len(graded_jobs_data)} graded jobs to {filename}")
    except IOError as e:
        print(f"I/O error writing CSV to {filename}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while writing graded jobs to CSV: {e}")


async def grade_and_save_jobs(input_csv_filename: str, output_csv_filename: str):
    print(f"Grading jobs from '{input_csv_filename}'. Output to: '{output_csv_filename}'")
    
    try:
        jobs_to_grade = read_jobs_from_csv(input_csv_filename)
        if not jobs_to_grade:
            print(f"No jobs found in '{input_csv_filename}' or the file is empty/corrupt.")
            return
    except FileNotFoundError:
        print(f"Error: Input CSV file not found: {input_csv_filename}")
        return
    
    try:
        profile_content = read_text_file("./files/profile.md")
    except FileNotFoundError:
        print("Error: Profile file (files/profile.md) not found. Using default empty profile.")
        profile_content = "No profile provided." # Default or error handling

    graded_jobs = []
    # Prepare the system prompt once
    # The original SCORE_JOBS_PROMPT is formatted with profile content.
    # The user message then contains the job(s) to evaluate.
    scoring_system_prompt = SCORE_JOBS_PROMPT.format(profile=profile_content)

    for job_dict in jobs_to_grade:
        job_text_for_scoring = format_job_for_scoring(job_dict)
        
        title_for_logging = job_dict.get('title', job_dict.get('job_id', 'Unknown Job')) # Use job_id if title missing
        print(f"Grading job: {title_for_logging}")
        
        try:
            # The JobScores model expects a list of scores.
            # The prompt SCORE_JOBS_PROMPT is designed for a list of jobs.
            # We adapt by sending a "list" containing just one job.
            score_response = await ainvoke_llm(
                system_prompt=scoring_system_prompt,
                user_message=f"Evaluate this Job:\n\n{job_text_for_scoring}", # Sending one job as a string
                model="openai/gpt-4o-mini", # Or your preferred model
                response_format=JobScores 
            )
            
            if score_response and score_response.scores and len(score_response.scores) > 0:
                # Assuming the JobScore model has 'score' and 'reasoning' fields
                # The 'id' field in JobScore referred to the index if multiple jobs were sent;
                # here it's less relevant as we process one by one, but it might be part of the model.
                single_score_data = score_response.scores[0] # Take the first (and only) score object
                job_dict['score'] = single_score_data.score
                # Assuming JobScore has a 'reasoning' field, adjust if it's named differently (e.g., 'reason')
                job_dict['reasoning'] = getattr(single_score_data, 'reasoning', "N/A") # Safely get reasoning
            else:
                print(f"Could not retrieve a valid score for job: {title_for_logging}")
                job_dict['score'] = None 
                job_dict['reasoning'] = "Scoring failed or no score provided by LLM."

        except Exception as e:
            print(f"Error scoring job {title_for_logging}: {e}")
            # This will catch OpenAI API key errors if not set, among other things.
            job_dict['score'] = None 
            job_dict['reasoning'] = f"Exception during scoring: {str(e)}"
        
        graded_jobs.append(job_dict)

    write_graded_jobs_to_csv(graded_jobs, output_csv_filename)
    print(f"Job grading complete. Results saved to {output_csv_filename}")
