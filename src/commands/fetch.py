import asyncio
import csv
from src.scraper import UpworkJobScraper # Assuming UpworkJobScraper is in src.scraper

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

async def fetch_and_save_jobs(search_query, num_jobs, output_csv_filename, run_in_simulated_mode=True):
    # run_in_simulated_mode is True because Upwork client is not fully configured yet
    # This parameter is noted but not directly used to control scraper's simulation mode in this version,
    # as the scraper itself decides simulation based on self.client.
    # It's kept for conceptual alignment with the prompt.
    print(f"Fetching jobs for query: '{search_query}', count: {num_jobs}. Output to: {output_csv_filename}")
    if run_in_simulated_mode:
        # This message is informative; actual simulation is handled by UpworkJobScraper's internal state.
        print("Attempting to run in SIMULATED Upwork API mode (actual mode depends on scraper client init).")

    scraper = UpworkJobScraper() 
    
    job_listings = await scraper.fetch_jobs_from_api(
        search_query=search_query,
        num_jobs=num_jobs
    )

    if job_listings:
        print(f"Fetched {len(job_listings)} job listings.")
        save_data_to_csv(job_listings, output_csv_filename)
    else:
        print("No job listings fetched.")
    
    return output_csv_filename # Or return success status/count
