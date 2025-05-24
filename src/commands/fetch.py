import asyncio
import csv
from src.scraper import UpworkJobScraper, UpworkConfigurationError, UpworkApiError

# Copied from scrape_upwork_jobs.py
def save_data_to_csv(jobs_data_list, filename):
    """
    Saves a list of job data (dictionaries) to a CSV file.
    Client information is flattened with a 'client_' prefix.
    """
    if not jobs_data_list:
        print("No job data to save.")
        return

    processed_jobs_for_csv = []
    for job_dict in jobs_data_list:
        flat_job = job_dict.copy() # Start with a copy of the original job dictionary
        client_info = flat_job.pop('client_information', {}) # Safely pop client_information
        
        # Flatten client_information into the main dictionary
        if client_info: # Ensure client_info is not None and is a dictionary
            for k, v in client_info.items():
                flat_job[f'client_{k}'] = v # Prepend 'client_' to client keys
        
        processed_jobs_for_csv.append(flat_job)
    
    if not processed_jobs_for_csv:
        print("No processable job data to save after attempting to flatten.")
        return

    try:
        fieldnames = processed_jobs_for_csv[0].keys()
    except IndexError:
        print("No job data to derive CSV headers from (list was empty after processing).")
        return

    try:
        with open(filename, 'w', newline='', encoding='utf-8') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=fieldnames)
            dict_writer.writeheader()
            dict_writer.writerows(processed_jobs_for_csv)
        print(f"Successfully saved {len(processed_jobs_for_csv)} jobs to {filename}")
    except IOError as e:
        print(f"I/O error writing to CSV {filename}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while saving data to CSV: {e}")

async def fetch_and_save_jobs(search_query, num_jobs, output_csv_filename):
    print(f"Attempting to fetch jobs for query: '{search_query}', count: {num_jobs}. Output will be saved to: {output_csv_filename}")
    
    job_listings = [] # Initialize to ensure it's defined in case of early exit
    try:
        scraper = UpworkJobScraper() 
        
        job_listings = await scraper.fetch_jobs_from_api(
            search_query=search_query,
            num_jobs=num_jobs
        )

        if job_listings:
            print(f"Successfully fetched {len(job_listings)} job listings.")
            save_data_to_csv(job_listings, output_csv_filename)
            return output_csv_filename # Indicate success by returning filename
        else:
            # This case means API call was successful but no jobs matched the query.
            print("No job listings found matching your query. Nothing to save.")
            return None # Indicate no data, but not an error

    except UpworkConfigurationError as e:
        print(f"Configuration Error: Could not initialize Upwork client. Please check your .env file for UPWORK_CLIENT_ID, UPWORK_CLIENT_SECRET, UPWORK_REDIRECT_URI and ensure you have completed the OAuth flow if prompted. Details: {e}")
        return None # Indicate failure
    except UpworkApiError as e:
        print(f"API Error: Failed to fetch jobs from Upwork. Details: {e}")
        return None # Indicate failure
    except Exception as e:
        import traceback
        print(f"An unexpected error occurred during job fetching: {e}\n{traceback.format_exc()}")
        return None # Indicate failure
