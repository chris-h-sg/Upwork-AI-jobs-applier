import asyncio
import csv
from datetime import datetime
from src.utils import ainvoke_llm, read_text_file # read_text_file is synchronous
from src.prompts import (
    PROFILE_ANALYZER_PROMPT,
    GENERATE_COVER_LETTER_PROMPT,
    GENERATE_INTERVIEW_PREPARATION_PROMPT
)
from src.structured_outputs import JobApplication, CoverLetter, CallScript

# Helper function to read graded jobs from CSV
def read_graded_jobs_from_csv(filename: str) -> list[dict]:
    jobs = []
    try:
        with open(filename, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                jobs.append(row)
    except FileNotFoundError:
        raise # Handled by the caller
    except Exception as e:
        print(f"Error reading CSV file {filename}: {e}")
        return []
    return jobs

# Helper function to save applications to a file
def save_applications_to_file(applications_data: list[JobApplication], filename: str, timestamp: str):
    if not applications_data:
        print("No application data to save.")
        return

    try:
        with open(filename, "a", encoding="utf-8") as file: # Append mode
            file.write("\n" + "=" * 80 + "\n")
            file.write(f"DATE: {timestamp}\n")
            file.write("=" * 80 + "\n\n")

            for application in applications_data:
                # Assuming application is an instance of JobApplication Pydantic model
                file.write("### Job Description\n")
                # JobApplication model might store job_description directly if passed,
                # or you might need to access it from the original job_dict if it was part of JobApplication.
                # Based on the plan, JobApplication stores job_description.
                file.write(application.job_description + "\n\n")

                file.write("### Cover Letter\n")
                file.write(application.cover_letter + "\n\n")

                file.write("### Interview Preparation\n")
                file.write(application.interview_preparation + "\n\n")

                file.write("\n" + "/" * 100 + "\n\n") # Added extra newline for separation
        print(f"Successfully appended {len(applications_data)} application(s) to {filename}")
    except IOError as e:
        print(f"I/O error writing to file {filename}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while saving applications: {e}")


async def generate_application_for_job(job_dict: dict, profile_content: str) -> JobApplication:
    """
    Generates cover letter and interview preparation for a single job.
    """
    job_description = job_dict.get('description', 'No description provided.') # Ensure description exists
    job_title = job_dict.get('title', 'Unknown Job') # For logging

    print(f"Analyzing profile for job: {job_title}")
    relevant_infos = await ainvoke_llm(
        system_prompt=PROFILE_ANALYZER_PROMPT.format(profile=profile_content),
        user_message=job_description,
        model="openai/gpt-4o-mini" # Or your preferred model
    )

    print(f"Generating cover letter for job: {job_title}")
    cover_letter_result = await ainvoke_llm(
        system_prompt=GENERATE_COVER_LETTER_PROMPT.format(profile=relevant_infos),
        user_message=f"Write a cover letter for the job described below:\n\n{job_description}",
        response_format=CoverLetter, # Expects CoverLetter Pydantic model
        model="openai/gpt-4o-mini"
    )
    # Ensure cover_letter_result.letter is accessed if CoverLetter model is used
    generated_cover_letter = cover_letter_result.letter if cover_letter_result else "Could not generate cover letter."

    print(f"Generating interview preparation for job: {job_title}")
    interview_prep_result = await ainvoke_llm(
        system_prompt=GENERATE_INTERVIEW_PREPARATION_PROMPT.format(profile=relevant_infos),
        user_message=f"Create preparation for the job described below:\n\n{job_description}",
        response_format=CallScript, # Expects CallScript Pydantic model
        model="openai/gpt-4o-mini"
    )
    # Ensure interview_prep_result.script is accessed if CallScript model is used
    generated_interview_prep = interview_prep_result.script if interview_prep_result else "Could not generate interview preparation."

    return JobApplication(
        job_description=job_description, # Store the original job description
        cover_letter=generated_cover_letter,
        interview_preparation=generated_interview_prep
    )


async def create_applications_and_save(input_csv_filename: str, output_md_filename: str):
    print(f"Preparing applications from '{input_csv_filename}'. Output to: '{output_md_filename}'")
    
    try:
        graded_jobs = read_graded_jobs_from_csv(input_csv_filename)
        if not graded_jobs:
            print(f"No graded jobs found in '{input_csv_filename}' or the file is empty/corrupt.")
            return
    except FileNotFoundError:
        print(f"Error: Input CSV file not found: {input_csv_filename}")
        return

    try:
        profile_content = read_text_file("./files/profile.md")
    except FileNotFoundError:
        print("Warning: Profile file (files/profile.md) not found. Using default empty profile.")
        profile_content = "No profile provided."

    # Filter jobs (e.g., only those with score >= 7)
    # The prompt suggests this was in MainGraphNodes.check_for_job_matches
    # We'll add a simple filter here. Assuming 'score' column exists and is numeric.
    
    eligible_jobs = []
    for job in graded_jobs:
        try:
            score = float(job.get('score', 0)) # Default to 0 if score is missing or invalid
            if score >= 7.0: # Example threshold
                eligible_jobs.append(job)
            else:
                print(f"Skipping job '{job.get('title', 'Unknown Title')}' due to low score: {score}")
        except ValueError:
            print(f"Skipping job '{job.get('title', 'Unknown Title')}' due to invalid score format: {job.get('score')}")
            continue
            
    if not eligible_jobs:
        print("No jobs met the minimum score criteria for application preparation.")
        return
        
    prepared_applications = []
    for job_dict in eligible_jobs:
        title_for_logging = job_dict.get('title', 'Unknown Title')
        print(f"Preparing application for eligible job: {title_for_logging}")
        try:
            application_data = await generate_application_for_job(job_dict, profile_content)
            prepared_applications.append(application_data)
        except Exception as e:
            print(f"Error preparing application for job {title_for_logging}: {e}")
            # Optionally, append a placeholder or error message:
            # prepared_applications.append(JobApplication(
            #     job_description=job_dict.get('description', 'Error processing this job.'),
            #     cover_letter=f"Error: {e}",
            #     interview_preparation=f"Error: {e}"
            # ))

    if prepared_applications:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_applications_to_file(prepared_applications, output_md_filename, timestamp)
    else:
        print("No applications were prepared (possibly due to errors or no eligible jobs).")
