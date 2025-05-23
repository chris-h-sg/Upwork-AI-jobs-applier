import os
import hashlib
import re # Keep for now for process_job_info_data, might be removed later
import asyncio # Added for asyncio.to_thread

# Removed: BeautifulSoup, tqdm_asyncio, playwright.async_api,
# get_playwright_browser_context, convert_html_to_markdown

# Potentially needed from python-upwork-oauth2, placeholder:
# import upwork
# from upwork.config import Config

from src.utils import ainvoke_llm # Keep if LLM is still used for description parsing
from src.database import job_exists
from src.structured_outputs import JobInformation, JobType, ClientInformation # Added JobType, ClientInformation
from src.prompts import SCRAPER_PROMPT # Keep if LLM is still used for description parsing


class UpworkJobScraper:
    """
    Fetches Upwork job data using the Upwork API.
    """

    def __init__(self): # batch_size is likely not relevant for API calls
        """
        Initializes the UpworkJobScraper and sets up API client configuration.
        """
        self.client_id = os.getenv("UPWORK_CLIENT_ID")
        self.client_secret = os.getenv("UPWORK_CLIENT_SECRET")

        # Placeholder for Upwork client initialization using python-upwork-oauth2
        # This will require specific setup according to the library's OAuth2 flow,
        # which typically involves user authorization to get an access token.
        # The actual implementation will need to handle token acquisition, storage, and refresh.
        # For now, self.client is None and operations will be simulated.
        self.client = None  # This should be replaced with actual client instantiation
        
        # Example of how client instantiation might look (conceptual):
        # if self.client_id and self.client_secret:
        #     try:
        #         # Assuming a configuration object might be needed
        #         # config = upwork.Config(
        #         #     client_id=self.client_id,
        #         #     client_secret=self.client_secret,
        #         #     redirect_uri=os.getenv("UPWORK_REDIRECT_URI"), # Important for OAuth
        #         #     access_token=os.getenv("UPWORK_ACCESS_TOKEN"), # If already obtained
        #         #     refresh_token=os.getenv("UPWORK_REFRESH_TOKEN") # If already obtained
        #         # )
        #         # self.client = upwork.Client(config)
        #         # Perform a test call or check client readiness if library supports it
        #         # print("Upwork API client initialized (conceptually).")
        #         pass # Actual initialization code here
        #     except Exception as e:
        #         print(f"Failed to initialize Upwork API client: {e}")
        #         self.client = None
        # else:
        #     print("Upwork client_id or client_secret not found in environment variables.")
        #     self.client = None
            
        print("UpworkJobScraper initialized. Actual API client setup for python-upwork-oauth2 is pending user OAuth flow and token management.")

    async def fetch_jobs_from_api(self, search_query="AI agent Developer", num_jobs=10):
        """
        Fetches jobs from the Upwork API based on search query and number of jobs.
        (Currently uses simulated data)
        """
        if not self.client:
            # This message is crucial for the user to understand that the API is not yet live.
            print("Upwork API client not initialized. Using SIMULATED data. Full OAuth setup and API integration required for live data.")
            # Proceed with simulated data for development/testing purposes
            # return [] # Or, for testing, use simulated data as below:
            # The actual "Simulating API call for..." print will be removed from here
            # and handled by the calling function if needed.

        jobs_data = []
        try:
            # Placeholder for actual GraphQL query and execution
            # The query will use search_query and num_jobs.
            # Example structure of a GraphQL query for job search:
            # graphql_query = f"""
            # query {{
            #   jobSearch(query: "{search_query}", first: {num_jobs}, sortBy: "recency") {{
            #     nodes {{
            #       id # This is the Upwork job ID, e.g., "~01xxxxxxxxxxxxxx"
            #       title
            #       description: descriptionV2 # Or just 'description'
            #       jobType # e.g., HOURLY, FIXED_PRICE
            #       amount {{ currencyCode value }} # For fixed price
            #       hourlyBudget {{ min max }} # Or hourlyRate
            #       skills {{ nodes {{ name }} }}
            #       categoryPage {{ title }} # Or similar for category
            #       duration # May need parsing or could be structured
            #       workload # e.g., "hours_per_week_v2", may need mapping
            #       url: upworkJobUrl # Or just 'url'
            #       client {{
            #         country {{ name }}
            #         publicFeedback # Or 'feedback'
            #         totalJobsPosted # Or 'jobsPosted'
            #         paymentVerificationStatus
            #       }}
            #     }}
            #   }}
            # }}
            # """
            # This is a conceptual GQL query. Actual field names from python-upwork-oauth2 might differ.
            # api_response = await self.client.execute(graphql_query) # Or similar async method

            # Simulate API response for now if self.client is None
            # The direct print about simulation call details is removed.
            simulated_api_jobs = [
                {
                    "id": "~01xxxxxxxxxxxxxx", "title": "AI Developer for Chatbot", "description": "Looking for an experienced AI developer to build a customer service chatbot using Python and Rasa.",
                    "jobType": "HOURLY", "hourlyBudget": {"min": 30, "max": 50}, "amount": None,
                    "skills": {"nodes": [{"name": "Python"}, {"name": "AI"}, {"name": "Rasa"}]}, 
                    "categoryPage": {"title": "AI & Machine Learning"}, "duration": "3-6 months", "workload": "30+ hours/week",
                    "upworkJobUrl": "https://www.upwork.com/jobs/ai-developer_~01xxxxxxxxxxxxxx",
                    "client": { "country": {"name": "USA"}, "publicFeedback": 4.75, "totalJobsPosted": 15, "paymentVerificationStatus": "VERIFIED"}
                },
                {
                    "id": "~01yyyyyyyyyyyyyy", "title": "Fixed Price: Landing Page Design", "description": "Need a modern landing page for a new SaaS product. Figma design preferred.",
                    "jobType": "FIXED_PRICE", "hourlyBudget": None, "amount": {"currencyCode": "USD", "value": 1200},
                    "skills": {"nodes": [{"name": "Web Design"}, {"name": "Figma"}, {"name": "Landing Pages"}]},
                    "categoryPage": {"title": "Web Design"}, "duration": "Less than 1 month", "workload": "N/A", # Workload might be different for fixed price
                    "upworkJobUrl": "https://www.upwork.com/jobs/landing-page_~01yyyyyyyyyyyyyy",
                    "client": { "country": {"name": "Canada"}, "publicFeedback": 4.9, "totalJobsPosted": 5, "paymentVerificationStatus": "VERIFIED"}
                },
                 {
                    "id": "~01zzzzzzzzzzzzzz", "title": "Data Analyst for Market Research", "description": "Analyze market trends for a new product launch. Experience with SQL and Tableau required.",
                    "jobType": "HOURLY", "hourlyBudget": {"min": 25, "max": 40}, "amount": None,
                    "skills": {"nodes": [{"name": "SQL"}, {"name": "Tableau"}, {"name": "Market Research"}]},
                    "categoryPage": {"title": "Data Analytics"}, "duration": "1-3 months", "workload": "10-20 hours/week",
                    "upworkJobUrl": "https://www.upwork.com/jobs/data-analyst_~01zzzzzzzzzzzzzz",
                    "client": { "country": {"name": "UK"}, "publicFeedback": 4.5, "totalJobsPosted": 20, "paymentVerificationStatus": "NOT_VERIFIED"} # Example of not verified
                }
            ]
            # In a real scenario:
            # api_jobs = api_response.get("data", {}).get("jobSearch", {}).get("nodes", [])
            api_jobs = simulated_api_jobs # Using simulated for now

            for api_job in api_jobs:
                api_job_id = api_job.get("id")
                if not api_job_id:
                    print("Skipping job with no ID.")
                    continue

                hashed_job_id = hashlib.sha256(api_job_id.encode()).hexdigest()
                
                # Assuming job_exists can be async or run in executor
                # If job_exists is not async, it would need to be run in a thread pool:
                # loop = asyncio.get_event_loop()
                # if await loop.run_in_executor(None, job_exists, hashed_job_id):
                # Now using asyncio.to_thread to call the synchronous job_exists
                if await asyncio.to_thread(job_exists, hashed_job_id):
                    print(f"Skipping already collected job: {api_job_id} (Hashed: {hashed_job_id[:10]}...)")
                    continue
                
                job_type_str = api_job.get("jobType", "").upper()
                job_type_enum = JobType.NOT_SPECIFIED
                if job_type_str == "HOURLY":
                    job_type_enum = JobType.HOURLY
                elif job_type_str == "FIXED_PRICE":
                    job_type_enum = JobType.FIXED # Corrected from FIXED_PRICE to match Enum definition

                payment_rate = None
                budget = None
                if job_type_enum == JobType.HOURLY and api_job.get("hourlyBudget"):
                    hr_rate = api_job["hourlyBudget"]
                    min_rate = hr_rate.get('min') # Keep as None if missing
                    max_rate = hr_rate.get('max') # Keep as None if missing
                    if min_rate is not None and max_rate is not None:
                         payment_rate = f"${min_rate}-${max_rate}"
                    elif max_rate is not None: 
                         payment_rate = f"Up to ${max_rate}"
                    elif min_rate is not None:
                         payment_rate = f"From ${min_rate}"
                    # If both are None, payment_rate remains None, which is fine.

                elif job_type_enum == JobType.FIXED and api_job.get("amount"): # Corrected from FIXED_PRICE to match Enum definition
                    amount_data = api_job["amount"]
                    val = amount_data.get('value') # Keep as None if missing
                    code = amount_data.get('currencyCode', '') # Default to empty string
                    if val is not None:
                        budget = f"${val} {code}".strip()


                client_info_raw = api_job.get("client", {})
                client_country_raw = client_info_raw.get("country", {})
                
                # The description from the API might be HTML or Markdown.
                # If it's HTML and needs cleaning, or if specific details need LLM extraction,
                # convert_html_to_markdown and ainvoke_llm would be used here.
                # For now, assume description is usable as is or LLM parsing is out of scope for this direct mapping.
                description_text = api_job.get("description", "")

                job_info = JobInformation(
                    job_id=hashed_job_id, # Store the hashed ID
                    title=api_job.get("title"),
                    description=description_text, 
                    job_type=job_type_enum,
                    budget=budget,
                    payment_rate=payment_rate,
                    skills=[skill.get("name") for skill in api_job.get("skills", {}).get("nodes", []) if skill.get("name")],
                    category=api_job.get("categoryPage", {}).get("title"), # Adjusted based on example
                    duration=api_job.get("duration"), # This might need parsing if not structured
                    workload=api_job.get("workload"), # This might need parsing/mapping
                    link=api_job.get("upworkJobUrl"), # Adjusted based on example
                    client_information=ClientInformation(
                        country=client_country_raw.get("name"), # Mapped to ClientInformation.country
                        feedback_score=client_info_raw.get("publicFeedback"), # Mapped to ClientInformation.feedback_score
                        jobs_posted=client_info_raw.get("totalJobsPosted"), # Mapped to ClientInformation.jobs_posted
                        payment_verification_status=(str(client_info_raw.get("paymentVerificationStatus", "")).upper() == "VERIFIED") # Mapped to ClientInformation.payment_verification_status
                        # Optional fields like joined_date, total_spent, company_profile will use their defaults (None)
                        # as they are not present in the current client_info_raw simulated data.
                    )
                )
                jobs_data.append(job_info.model_dump())
                # Removed: print(f"Processed job: {api_job.get('title')}")

        except Exception as e:
            # Log the full error for debugging, especially during initial API integration
            import traceback
            print(f"Error fetching or processing jobs from API: {e}\n{traceback.format_exc()}")

        return self.process_job_info_data(jobs_data)

    def process_job_info_data(self, jobs_data):
        """
        Performs any final common formatting on the job data.
        The regex for payment_rate previously here is now handled during the mapping
        from API response if structured rates (min/max) are available.
        This method is kept for any other potential common processing.
        """
        # Example: Ensure all descriptions are strings, even if None initially
        for job in jobs_data:
            if job.get("description") is None:
                job["description"] = ""
            # Any other common cleaning or formatting can go here.
        return jobs_data

# Old methods have been removed by replacing the entire block of old methods
# with the new fetch_jobs_from_api and the updated process_job_info_data.

# Note: job_exists from src.database is a synchronous function.
# It is now called from the async method fetch_jobs_from_api using `await asyncio.to_thread(job_exists, ...)`,
# which runs it in a separate thread to avoid blocking the event loop.
# `asyncio` has been imported at the top of the file.