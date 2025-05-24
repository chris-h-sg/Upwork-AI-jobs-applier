import argparse
import asyncio # Added import
import os # Added import
from src.commands.fetch import fetch_and_save_jobs
from src.commands.grade import grade_and_save_jobs
from src.commands.apply import create_applications_and_save

# Handler functions for each subcommand
def handle_fetch_jobs(args):
    print(f"Subcommand: fetch_jobs")
    # print(f"Output CSV: {args.output_csv}") # Original print, can be kept or removed
    # For now, use a default search query and num_jobs. These could be made CLI args later.
    default_search_query = "AI agent developer"
    default_num_jobs = 10 
    asyncio.run(fetch_and_save_jobs(
        search_query=default_search_query,
        num_jobs=default_num_jobs,
        output_csv_filename=args.output_csv
        # run_in_simulated_mode is True by default in fetch_and_save_jobs
    ))
    print(f"fetch_jobs command finished. Output should be in {args.output_csv}")

def handle_grade_jobs(args):
    print(f"Subcommand: grade_jobs")
    # print(f"Input CSV: {args.input_csv}") # Original print
    # print(f"Output CSV: {args.output_csv}") # Original print
    asyncio.run(grade_and_save_jobs(
        input_csv_filename=args.input_csv,
        output_csv_filename=args.output_csv
    ))
    print(f"grade_jobs command finished. Output should be in {args.output_csv}")

async def handle_fetch_and_grade_jobs_async(args):
    print("Subcommand: fetch_and_grade_jobs")
    print(f"Step 1: Fetching jobs, output to: {args.output_csv_fetch}")
    
    # Use default search query and num_jobs for now, similar to handle_fetch_jobs
    default_search_query = "AI agent developer"
    default_num_jobs = 10

    await fetch_and_save_jobs(
        search_query=default_search_query,
        num_jobs=default_num_jobs,
        output_csv_filename=args.output_csv_fetch
    )
    
    print(f"Step 2: Grading jobs from '{args.output_csv_fetch}', output to: {args.output_csv_grade}")
    await grade_and_save_jobs(
        input_csv_filename=args.output_csv_fetch,
        output_csv_filename=args.output_csv_grade
    )
    print("Fetch and grade process complete.")

# This wrapper is needed because the main args.func(args) call is synchronous
def handle_fetch_and_grade_jobs(args):
    asyncio.run(handle_fetch_and_grade_jobs_async(args))

def handle_prepare_applications(args):
    print(f"Subcommand: prepare_applications")
    # print(f"Input CSV: {args.input_csv}") # Original print
    # print(f"Output file: {args.output_file}") # Original print
    asyncio.run(create_applications_and_save(
        input_csv_filename=args.input_csv,
        output_md_filename=args.output_file
    ))
    print(f"prepare_applications command finished. Output should be in {args.output_file}")

async def handle_main_pipeline_async(args): # args might not be used if no specific args for main_pipeline
    print("Starting main pipeline...")

    # Define intermediate/output filenames
    fetched_jobs_csv = "fetched_jobs.csv" # Default from fetch_jobs
    graded_jobs_csv = "graded_jobs.csv"   # Default from grade_jobs
    applications_md = "applications.md" # Default from prepare_applications

    # --- Step 1: Fetch Jobs ---
    print(f"Stage 1: Fetching jobs -> {fetched_jobs_csv}")
    default_search_query = "AI agent developer" # Consistent with other commands
    default_num_jobs = 10
    try:
        await fetch_and_save_jobs(
            search_query=default_search_query,
            num_jobs=default_num_jobs,
            output_csv_filename=fetched_jobs_csv
        )
        if not os.path.exists(fetched_jobs_csv):
            print(f"Error: Fetched jobs CSV '{fetched_jobs_csv}' not created. Aborting pipeline.")
            return
        print("Job fetching complete.")
    except Exception as e:
        print(f"Error during job fetching stage: {e}")
        return

    # --- Step 2: Grade Jobs ---
    print(f"Stage 2: Grading jobs from '{fetched_jobs_csv}' -> {graded_jobs_csv}")
    try:
        await grade_and_save_jobs(
            input_csv_filename=fetched_jobs_csv,
            output_csv_filename=graded_jobs_csv
        )
        if not os.path.exists(graded_jobs_csv):
            print(f"Error: Graded jobs CSV '{graded_jobs_csv}' not created. Aborting pipeline.")
            # Optionally, clean up fetched_jobs_csv if desired
            return
        print("Job grading complete.")
    except Exception as e:
        print(f"Error during job grading stage: {e}")
        return
        
    # --- Step 3: Prepare Applications ---
    print(f"Stage 3: Preparing applications from '{graded_jobs_csv}' -> {applications_md}")
    try:
        await create_applications_and_save(
            input_csv_filename=graded_jobs_csv,
            output_md_filename=applications_md
        )
        print("Application preparation complete.")
    except Exception as e:
        print(f"Error during application preparation stage: {e}")
        return
        
    print("Main pipeline finished successfully.")

# This wrapper is needed because the main args.func(args) call is synchronous
def handle_main_pipeline(args):
    asyncio.run(handle_main_pipeline_async(args))


def main():
    parser = argparse.ArgumentParser(description="Upwork Automation CLI Tool")
    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")

    # fetch_jobs subcommand
    fetch_parser = subparsers.add_parser("fetch_jobs", help="Fetch jobs from Upwork and save to CSV.")
    fetch_parser.add_argument("--output-csv", default="fetched_jobs.csv", help="Output CSV file for fetched jobs.")
    fetch_parser.set_defaults(func=handle_fetch_jobs)

    # grade_jobs subcommand
    grade_parser = subparsers.add_parser("grade_jobs", help="Grade jobs from a CSV file.")
    grade_parser.add_argument("--input-csv", required=True, help="Input CSV file with jobs to grade.")
    grade_parser.add_argument("--output-csv", default="graded_jobs.csv", help="Output CSV file for graded jobs.")
    grade_parser.set_defaults(func=handle_grade_jobs)

    # fetch_and_grade_jobs subcommand
    fetch_grade_parser = subparsers.add_parser("fetch_and_grade_jobs", help="Fetch jobs and then grade them.")
    fetch_grade_parser.add_argument("--output-csv-fetch", default="fetched_jobs.csv", help="Output CSV for fetched jobs part.")
    fetch_grade_parser.add_argument("--output-csv-grade", default="graded_jobs.csv", help="Output CSV for graded jobs part.")
    fetch_grade_parser.set_defaults(func=handle_fetch_and_grade_jobs)

    # prepare_applications subcommand
    prepare_parser = subparsers.add_parser("prepare_applications", help="Prepare job applications from graded jobs CSV.")
    prepare_parser.add_argument("--input-csv", required=True, help="Input CSV file with graded jobs.")
    prepare_parser.add_argument("--output-file", default="applications.md", help="Output file for applications.")
    prepare_parser.set_defaults(func=handle_prepare_applications)

    # main_pipeline subcommand
    pipeline_parser = subparsers.add_parser("main_pipeline", help="Run the full end-to-end job processing pipeline.")
    # No arguments for main_pipeline initially
    pipeline_parser.set_defaults(func=handle_main_pipeline)

    args = parser.parse_args()
    
    # Call the function associated with the chosen subcommand
    if hasattr(args, 'func'):
        args.func(args)
    else:
        # This part should ideally not be reached if all subparsers have a func set
        # and `required=True` is set for subparsers.
        # However, it's a good fallback for development.
        print(f"Subcommand {args.command} is recognized but has no action defined yet or 'func' was not set.")

if __name__ == "__main__":
    main()
