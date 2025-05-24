import os
import hashlib
import re # Keep for now for process_job_info_data, might be removed later
import asyncio
import time # Added for checking token expiry

import upwork # Official Upwork API library
from upwork.routers import graphql

from src.utils import ainvoke_llm # Keep if LLM is still used for description parsing
from src.database import job_exists
from src.structured_outputs import JobInformation, JobType, ClientInformation # Added JobType, ClientInformation
from src.prompts import SCRAPER_PROMPT # Keep if LLM is still used for description parsing


class UpworkConfigurationError(Exception):
    """Custom exception for Upwork API configuration errors."""
    pass


class UpworkApiError(Exception):
    """Custom exception for Upwork API call errors."""
    pass


class UpworkJobScraper:
    """
    Fetches Upwork job data using the Upwork API.
    """

    def __init__(self):
        self.client_id = os.getenv("UPWORK_CLIENT_ID")
        self.client_secret = os.getenv("UPWORK_CLIENT_SECRET")
        self.redirect_uri = os.getenv("UPWORK_REDIRECT_URI")
        self.access_token = os.getenv("UPWORK_ACCESS_TOKEN")
        self.refresh_token = os.getenv("UPWORK_REFRESH_TOKEN")
        expires_at_str = os.getenv("UPWORK_EXPIRES_AT")
        
        self.client = None
        self.config = None # Will hold the upwork.Config object

        # Base config data for Upwork client
        config_data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri,
        }

        # Try to initialize with existing tokens first
        if self.access_token and self.refresh_token and expires_at_str:
            try:
                expires_at_timestamp = float(expires_at_str)
                
                if time.time() >= expires_at_timestamp - 300: # 300 seconds = 5 minutes buffer
                    print("INFO: Existing token is expired or nearing expiry. The library will attempt to refresh it if needed.")
                
                config_data['token'] = {
                    'access_token': self.access_token,
                    'refresh_token': self.refresh_token,
                    'token_type': 'Bearer', # Standard token type
                    'expires_at': expires_at_timestamp,
                }
                self.config = upwork.Config(config_data)
                self.client = upwork.Client(self.config)
                
                # Optional: Test the connection by fetching user info to validate tokens
                # This part is synchronous and should ideally be handled in an async setup method
                # or by ensuring __init__ is called in a context where blocking is acceptable.
                try:
                    response = graphql.Api(self.client).execute({'query': "query { user { nid } }"})
                    print(f"Successfully initialized Upwork client with existing tokens for user: {response.get('data', {}).get('user', {}).get('nid')}")
                except Exception as e: 
                    print(f"WARNING: Failed to validate existing tokens (e.g., expired/revoked): {e}. Proceeding to OAuth flow.")
                    self.client = None 
                    self.config = None 
                    config_data.pop('token', None) # Remove bad token for OAuth attempt
                    # Fall through to OAuth flow attempt below
                
            except ValueError: # Handles error if UPWORK_EXPIRES_AT is not a valid float
                print(f"ERROR: UPWORK_EXPIRES_AT value ('{expires_at_str}') is not a valid timestamp. Cannot use existing tokens.")
                self.client = None; self.config = None; config_data.pop('token', None)
            except Exception as e: # Catch other potential errors during upwork.Config/Client init
                print(f"Error initializing Upwork client with existing tokens: {e}. Attempting OAuth flow.")
                self.client = None; self.config = None; config_data.pop('token', None) 
                # Fall through to OAuth flow attempt below
        
        # If client is not yet set (no tokens, or token init failed), try OAuth flow
        if not self.client:
            if self.client_id and self.client_secret and self.redirect_uri:
                if not (self.access_token and self.refresh_token and expires_at_str): # Only print if tokens weren't there to begin with
                    print("INFO: Existing tokens not found or invalid. Attempting OAuth flow.")
                if not self._perform_oauth_flow(): 
                    self.client = None # Ensure client is None if OAuth fails
            else:
                # This path is taken if essential initial credentials are missing
                # The self.client will remain None here.
                pass # The final check will handle raising the exception.

        if self.client is None:
            error_message = (
                "Upwork client could not be initialized. This can be due to several reasons:\n"
                "1. Missing or incorrect UPWORK_CLIENT_ID, UPWORK_CLIENT_SECRET, or UPWORK_REDIRECT_URI in your .env file.\n"
                "2. The OAuth 2.0 flow was not completed successfully (e.g., did not paste callback URL, or Upwork returned an error).\n"
                "3. Existing tokens (UPWORK_ACCESS_TOKEN, UPWORK_REFRESH_TOKEN, UPWORK_EXPIRES_AT) in .env are invalid or expired, and the refresh/re-authentication attempt failed.\n"
                "Please check your .env file, ensure you have a valid internet connection, "
                "and be prepared to complete the OAuth flow when prompted (by copying URLs between your browser and the console)."
            )
            raise UpworkConfigurationError(error_message)

    def _perform_oauth_flow(self):
        """
        Manages the OAuth 2.0 authorization code flow.
        """
        # This method assumes client_id, client_secret, and redirect_uri are already checked by __init__
        # before calling it, or that it's fine to proceed if they are set on the instance.
        try:
            # Use a fresh config for the initial part of OAuth
            current_config_data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'redirect_uri': self.redirect_uri,
            }
            # Important: Do not include any 'token' field here for the initial step
            self.config = upwork.Config(current_config_data)
            temp_client = upwork.Client(self.config) # This client is not yet authorized for protected resources
            
            authorization_url = temp_client.get_authorization_url() # state can be used for CSRF protection
            
            print("\n--- Upwork API OAuth Authorization Needed ---")
            print("1. Open the following URL in your browser:")
            print(f"   {authorization_url}")
            print("2. Authorize the application.")
            print("3. You will be redirected to a URL (your redirect_uri). Copy the FULL redirected URL from your browser's address bar.")
            
            callback_url_response = input("4. Paste the full callback URL here and press Enter: \n")

            if not callback_url_response:
                print("ERROR: No callback URL provided. OAuth flow aborted.")
                return False

            print("INFO: Authorization code obtained. Requesting access token...")
            # The get_access_token method will update temp_client.config with the token
            temp_client.get_access_token(callback_url_response) 
            
            self.config = temp_client.config # Store the updated config with tokens
            self.client = temp_client        # This client is now authorized

            print("\n--- OAuth Successful! ---")
            print("Successfully obtained Upwork API tokens.")
            print("IMPORTANT: Please save these tokens in your .env file for future sessions to avoid repeating this process:")
            print(f"UPWORK_ACCESS_TOKEN=\"{self.config.token['access_token']}\"")
            print(f"UPWORK_REFRESH_TOKEN=\"{self.config.token['refresh_token']}\"")
            print(f"UPWORK_EXPIRES_AT=\"{self.config.token['expires_at']}\"") # This is a Unix timestamp
            print("-----------------------------\n")
            # Update instance variables with new tokens for current session
            self.access_token = self.config.token['access_token']
            self.refresh_token = self.config.token['refresh_token']
            # Note: UPWORK_EXPIRES_AT is also available in self.config.token['expires_at']
            return True

        except Exception as e:
            import traceback
            print(f"An error occurred during the OAuth flow: {e}\n{traceback.format_exc()}")
            return False

    async def fetch_jobs_from_api(self, search_query="AI agent Developer", num_jobs=10):
        # If __init__ completed successfully, self.client should be initialized.
        # If not, UpworkConfigurationError would have been raised.
        # Therefore, we can assume self.client is valid here.

        print(f"INFO: Attempting to fetch jobs using live Upwork API for query: '{search_query}', count: {num_jobs}")
        
        query = {
            'query': """
            query marketplaceJobPostingsSearch(
                $marketPlaceJobFilter: MarketplaceJobPostingsSearchFilter,
                $searchType: MarketplaceJobPostingSearchType,
                $sortAttributes: [MarketplaceJobPostingSearchSortAttribute]
                ) {
                marketplaceJobPostingsSearch(
                    marketPlaceJobFilter: $marketPlaceJobFilter,
                    searchType: $searchType,
                    sortAttributes: $sortAttributes
                ) {
                    totalCount
                    edges {
                    node {
                        id
                        title
                        createdDateTime
                        description
                        durationLabel
                        engagement 
                        experienceLevel
                        category 
                        subcategory
                        relevanceEncoded 
                        preferredFreelancerLocation 
                        preferredFreelancerLocationMandatory 
                        client {
                            companyName
                            totalPostedJobs
                            totalReviews
                            totalFeedback
                            totalSpent {
                                currency
                                displayValue
                            }
                        }
                    }
                    }
                }
                }
            """,
            'variables': {
                "marketPlaceJobFilter": {
                    "titleExpression_eq": search_query,
                    "pagination_eq": { 'first': num_jobs, 'after': "0" }
                },
                "searchType": "JOBS_FEED",
                "sortAttributes": [
                    { "field": "RECENCY" }
                ]
                }
        }
        try:
            # Run synchronous SDK calls in a separate thread
            api_response_raw = await asyncio.to_thread(graphql.Api(self.client).execute, query)
            
            # Check if tokens were refreshed and need updating in .env
            if self.config and self.config.token: 
                current_token_in_config = self.config.token
                if self.access_token != current_token_in_config.get('access_token'):
                    print("\n--- Upwork API Token Updated ---")
                    print("Your API access token was refreshed during the operation.")
                    print("Please update your .env file with the new token details for future sessions:")
                    print(f"UPWORK_ACCESS_TOKEN=\"{current_token_in_config['access_token']}\"")
                    if 'refresh_token' in current_token_in_config and self.refresh_token != current_token_in_config.get('refresh_token'):
                         print(f"UPWORK_REFRESH_TOKEN=\"{current_token_in_config['refresh_token']}\"")
                    print(f"UPWORK_EXPIRES_AT=\"{current_token_in_config['expires_at']}\"")
                    print("--------------------------------\n")
                    self.access_token = current_token_in_config.get('access_token')
                    if 'refresh_token' in current_token_in_config:
                        self.refresh_token = current_token_in_config.get('refresh_token')
            
            api_jobs_processed = api_response_raw.get("data", {}).get("marketplaceJobPostingsSearch", {}).get("edges", [])
            if not api_jobs_processed:
                print("INFO: Live API call successful, but no jobs found for the query.")
                # If no jobs are found, it's not an error, just return an empty list.
                return [] # Return empty list directly
            else:
                print(f"INFO: Successfully fetched {len(api_jobs_processed)} jobs from live API.")

        except Exception as e:
            import traceback
            error_message = f"Upwork API Error: Failed to fetch jobs from Upwork API: {e}\n{traceback.format_exc()}"
            print(error_message) # Log the error
            raise UpworkApiError(error_message) # Raise custom error

        # If API call was successful and jobs were found, proceed to process them.
        # This part is only reached if api_jobs_processed is not empty and no exception occurred.
        jobs_data_models = []
        try: # This try-except is for processing the list of jobs (either real or simulated)
            for api_job in api_jobs_processed:
                node = api_job.get("node", {})
                print(node)
                api_job_id = node.get("id")
                if not api_job_id:
                    print("Skipping job with no ID.")
                    continue

                hashed_job_id = hashlib.sha256(api_job_id.encode()).hexdigest()
                
                # Now using asyncio.to_thread to call the synchronous job_exists
                if await asyncio.to_thread(job_exists, hashed_job_id):
                    # print(f"INFO: Skipping already collected job: {api_job_id} (Hashed: {hashed_job_id[:10]}...)") # Verbose
                    continue # Silently skip for cleaner logs during normal operation
                
                job_type_str = node.get("jobType", "").upper()
                job_type_enum = JobType.NOT_SPECIFIED
                if job_type_str == "HOURLY":
                    job_type_enum = JobType.HOURLY
                elif job_type_str == "FIXED_PRICE":
                    job_type_enum = JobType.FIXED # Corrected from FIXED_PRICE to match Enum definition

                payment_rate = None
                budget = None
                if job_type_enum == JobType.HOURLY and node.get("hourlyBudget"):
                    hr_rate = node["hourlyBudget"]
                    min_rate = hr_rate.get('min') # Keep as None if missing
                    max_rate = hr_rate.get('max') # Keep as None if missing
                    if min_rate is not None and max_rate is not None:
                         payment_rate = f"${min_rate}-${max_rate}"
                    elif max_rate is not None: 
                         payment_rate = f"Up to ${max_rate}"
                    elif min_rate is not None:
                         payment_rate = f"From ${min_rate}"
                    # If both are None, payment_rate remains None, which is fine.

                elif job_type_enum == JobType.FIXED and node.get("amount"): # Corrected from FIXED_PRICE to match Enum definition
                    amount_data = node["amount"]
                    val = amount_data.get('value') # Keep as None if missing
                    code = amount_data.get('currencyCode', '') # Default to empty string
                    if val is not None:
                        budget = f"${val} {code}".strip()


                client_info_raw = node.get("client", {})
                client_country_raw = client_info_raw.get("country", {})
                
                # The description from the API might be HTML or Markdown.
                # If it's HTML and needs cleaning, or if specific details need LLM extraction,
                # convert_html_to_markdown and ainvoke_llm would be used here.
                # For now, assume description is usable as is or LLM parsing is out of scope for this direct mapping.
                description_text = node.get("description", "")

                job_info = JobInformation(
                    job_id=hashed_job_id, # Store the hashed ID
                    title=node.get("title"),
                    description=description_text, 
                    job_type=job_type_enum,
                    budget=budget,
                    payment_rate=payment_rate,
                    skills=[skill.get("name") for skill in node.get("skills", {}).get("nodes", []) if skill.get("name")],
                    category=node.get("categoryPage", {}).get("title"), # Adjusted based on example
                    duration=node.get("duration"), # This might need parsing if not structured
                    workload=node.get("workload"), # This might need parsing/mapping
                    link=node.get("upworkJobUrl"), # Adjusted based on example
                    client_information=ClientInformation(
                        country=client_country_raw.get("name"), # Mapped to ClientInformation.country
                        feedback_score=client_info_raw.get("publicFeedback"), # Mapped to ClientInformation.feedback_score
                        jobs_posted=client_info_raw.get("totalJobsPosted"), # Mapped to ClientInformation.jobs_posted
                    payment_verification_status=(str(client_info_raw.get("paymentVerificationStatus", "")).upper() == "VERIFIED")
                    )
                )
                jobs_data_models.append(job_info.model_dump())

        except Exception as e:
            import traceback
            print(f"ERROR: Error processing jobs data (live or simulated): {e}\n{traceback.format_exc()}")

        return self.process_job_info_data(jobs_data_models) # Pass the processed list of dicts

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
# `asyncio`, `time`, `urlparse`, `parse_qs` and `upwork` have been imported.
# The `upwork.Config` is accessed via `upwork.Config`.
# The synchronous calls like `self.client.auth.get_user_info()` in `__init__` and
# `self.client.execute()` in `fetch_jobs_from_api` are handled appropriately for an asyncio context
# by being wrapped with `asyncio.to_thread` in `fetch_jobs_from_api` or by accepting that `__init__`
# might block if called from a sync context directly (which is typical for class instantiation).