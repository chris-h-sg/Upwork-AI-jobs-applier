import asyncio
# Removed csv import, UpworkJobScraper import
from src.commands.fetch import fetch_and_save_jobs # Updated import
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Removed local save_data_to_csv function

if __name__ == "__main__":
    search_query = "AI agent developer" # Or get from config/args
    number_of_jobs = 10
    output_filename = "upwork_jobs_data.csv" # Default output filename

    print(f"Executing standalone job fetch: Query='{search_query}', NumJobs={number_of_jobs}, Output='{output_filename}'")
    asyncio.run(fetch_and_save_jobs(
        search_query=search_query,
        num_jobs=number_of_jobs,
        output_csv_filename=output_filename
    ))
    print("Standalone job fetch complete.")
