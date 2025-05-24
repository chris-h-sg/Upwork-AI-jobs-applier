import os
import time

import upwork
from upwork.routers import graphql

from src.structured_outputs import JobInformation

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
        self._initialize_credentials()
        self._setup_client()

    def _initialize_credentials(self):
        """Initialize credentials from environment variables."""
        self.client_id = os.getenv("UPWORK_CLIENT_ID")
        self.client_secret = os.getenv("UPWORK_CLIENT_SECRET")
        self.redirect_uri = os.getenv("UPWORK_REDIRECT_URI")
        self.access_token = os.getenv("UPWORK_ACCESS_TOKEN")
        self.refresh_token = os.getenv("UPWORK_REFRESH_TOKEN")
        self.expires_at_str = os.getenv("UPWORK_EXPIRES_AT")
        self.client = None
        self.config = None

    def _setup_client(self):
        """Set up the Upwork client with existing tokens or initiate OAuth flow."""
        config_data = self._get_base_config()
        
        if self._has_valid_tokens():
            if not self._initialize_with_existing_tokens(config_data):
                self._try_oauth_flow()
        else:
            self._try_oauth_flow()

        if self.client is None:
            raise UpworkConfigurationError(self._get_configuration_error_message())

    def _get_base_config(self):
        """Get base configuration for Upwork client."""
        return {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri,
        }

    def _has_valid_tokens(self):
        """Check if we have all required tokens."""
        return all([self.access_token, self.refresh_token, self.expires_at_str])

    def _initialize_with_existing_tokens(self, config_data):
        """Initialize client with existing tokens."""
        try:
            expires_at_timestamp = float(self.expires_at_str)
            
            if time.time() >= expires_at_timestamp - 300:  # 5 minutes buffer
                print("INFO: Existing token is expired or nearing expiry. The library will attempt to refresh it if needed.")
            
            config_data['token'] = {
                'access_token': self.access_token,
                'refresh_token': self.refresh_token,
                'token_type': 'Bearer',
                'expires_at': expires_at_timestamp,
            }
            self.config = upwork.Config(config_data)
            self.client = upwork.Client(self.config)
            
            return self._validate_client_connection()
            
        except (ValueError, Exception) as e:
            print(f"Error initializing with existing tokens: {e}")
            self._reset_client_state()
            return False

    def _validate_client_connection(self):
        """Validate the client connection by making a test API call."""
        try:
            response = graphql.Api(self.client).execute({'query': "query { user { nid } }"})
            if 'message' in response:
                raise UpworkApiError(f"API returned error message: {response['message']}")
            print(f"Successfully initialized Upwork client with existing tokens for user: {response.get('data', {}).get('user', {}).get('nid')}")
            return True
        except Exception as e:
            print(f"WARNING: Failed to validate existing tokens: {e}")
            self._reset_client_state()
            return False

    def _reset_client_state(self):
        """Reset client and config state."""
        self.client = None
        self.config = None

    def _try_oauth_flow(self):
        """Attempt OAuth flow if credentials are available."""
        if all([self.client_id, self.client_secret, self.redirect_uri]):
            if not self._has_valid_tokens():
                print("INFO: Existing tokens not found or invalid. Attempting OAuth flow.")
            if not self._perform_oauth_flow():
                self._reset_client_state()

    def _get_configuration_error_message(self):
        """Get detailed error message for configuration issues."""
        return (
            "Upwork client could not be initialized. This can be due to several reasons:\n"
            "1. Missing or incorrect UPWORK_CLIENT_ID, UPWORK_CLIENT_SECRET, or UPWORK_REDIRECT_URI in your .env file.\n"
            "2. The OAuth 2.0 flow was not completed successfully (e.g., did not paste callback URL, or Upwork returned an error).\n"
            "3. Existing tokens (UPWORK_ACCESS_TOKEN, UPWORK_REFRESH_TOKEN, UPWORK_EXPIRES_AT) in .env are invalid or expired, and the refresh/re-authentication attempt failed.\n"
            "Please check your .env file, ensure you have a valid internet connection, "
            "and be prepared to complete the OAuth flow when prompted (by copying URLs between your browser and the console)."
        )

    def _perform_oauth_flow(self):
        """Perform OAuth 2.0 authorization flow."""
        try:
            self.config = upwork.Config(self._get_base_config())
            temp_client = upwork.Client(self.config)
            
            authorization_url = temp_client.get_authorization_url()
            self._print_oauth_instructions(authorization_url)
            
            callback_url = self._get_callback_url()
            if not callback_url:
                return False

            print("INFO: Authorization code obtained. Requesting access token...")
            temp_client.get_access_token(callback_url)
            
            self._update_client_with_tokens(temp_client)
            return True

        except Exception as e:
            import traceback
            print(f"An error occurred during the OAuth flow: {e}\n{traceback.format_exc()}")
            return False

    def _print_oauth_instructions(self, authorization_url):
        """Print OAuth flow instructions."""
        print("\n--- Upwork API OAuth Authorization Needed ---")
        print("1. Open the following URL in your browser:")
        print(f"   {authorization_url}")
        print("2. Authorize the application.")
        print("3. You will be redirected to a URL (your redirect_uri). Copy the FULL redirected URL from your browser's address bar.")

    def _get_callback_url(self):
        """Get callback URL from user input."""
        callback_url = input("4. Paste the full callback URL here and press Enter: \n")
        if not callback_url:
            print("ERROR: No callback URL provided. OAuth flow aborted.")
            return None
        return callback_url

    def _update_client_with_tokens(self, temp_client):
        """Update client with new tokens and print instructions."""
        self.config = temp_client.config
        self.client = temp_client
        self.access_token = self.config.token['access_token']
        self.refresh_token = self.config.token['refresh_token']

        print("\n--- OAuth Successful! ---")
        print("Successfully obtained Upwork API tokens.")
        print("IMPORTANT: Please save these tokens in your .env file for future sessions to avoid repeating this process:")
        print(f"UPWORK_ACCESS_TOKEN=\"{self.access_token}\"")
        print(f"UPWORK_REFRESH_TOKEN=\"{self.refresh_token}\"")
        print(f"UPWORK_EXPIRES_AT=\"{self.config.token['expires_at']}\"")
        print("-----------------------------\n")

    async def fetch_jobs_from_api(self, search_query="AI agent Developer", num_jobs=10):
        """Fetch jobs from Upwork API."""
        print(f"INFO: Attempting to fetch jobs using live Upwork API for query: '{search_query}', count: {num_jobs}")
        
        try:
            api_response = await self._execute_job_search_query(search_query, num_jobs)
            self._handle_token_refresh()
            self._check_api_errors(api_response)
            
            jobs = self._extract_jobs_from_response(api_response)
            if not jobs:
                return []

            return self._process_jobs(jobs)

        except Exception as e:
            self._handle_api_error(e)

    async def _execute_job_search_query(self, search_query, num_jobs):
        """Execute the GraphQL query to search for jobs."""
        query = self._build_job_search_query(search_query, num_jobs)
        return graphql.Api(self.client).execute(query)

    def _build_job_search_query(self, search_query, num_jobs):
        """Build the GraphQL query for job search."""
        return {
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
                        publishedDateTime
                        description
                        durationLabel
                        engagement
                        job {
                            contractTerms {
                                contractType
                            }
                            activityStat {
                                jobActivity {
                                    lastClientActivity
                                    invitesSent 
                                    totalInvitedToInterview 
                                    totalUnansweredInvites 
                                }
                            }
                        }
                        hourlyBudgetMin {
                            currency
                            displayValue
                        }
                        hourlyBudgetMax {
                            currency
                            displayValue
                        }
                        weeklyBudget {
                            currency
                            displayValue
                        }
                        experienceLevel
                        category 
                        subcategory
                        totalApplicants
                        preferredFreelancerLocation 
                        preferredFreelancerLocationMandatory 
                        skills {
                            prettyName
                        }
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

    def _handle_token_refresh(self):
        """Handle token refresh if needed."""
        if self.config and self.config.token:
            current_token = self.config.token
            if self.access_token != current_token.get('access_token'):
                self._print_token_update_instructions(current_token)
                self._update_tokens(current_token)

    def _print_token_update_instructions(self, current_token):
        """Print instructions for updating tokens."""
        print("\n--- Upwork API Token Updated ---")
        print("Your API access token was refreshed during the operation.")
        print("Please update your .env file with the new token details for future sessions:")
        print(f"UPWORK_ACCESS_TOKEN=\"{current_token['access_token']}\"")
        if 'refresh_token' in current_token and self.refresh_token != current_token.get('refresh_token'):
            print(f"UPWORK_REFRESH_TOKEN=\"{current_token['refresh_token']}\"")
        print(f"UPWORK_EXPIRES_AT=\"{current_token['expires_at']}\"")
        print("--------------------------------\n")

    def _update_tokens(self, current_token):
        """Update tokens with new values."""
        self.access_token = current_token.get('access_token')
        if 'refresh_token' in current_token:
            self.refresh_token = current_token.get('refresh_token')

    def _check_api_errors(self, api_response):
        """Check for API errors in the response."""
        if 'errors' in api_response:
            error_messages = [error.get('message', 'Unknown error') for error in api_response['errors']]
            raise UpworkApiError(f"Upwork API returned errors: {', '.join(error_messages)}")

    def _extract_jobs_from_response(self, api_response):
        """Extract jobs from API response."""
        jobs = api_response.get("data", {}).get("marketplaceJobPostingsSearch", {}).get("edges", [])
        if not jobs:
            print("INFO: Live API call successful, but no jobs found for the query.")
            return []
        print(f"INFO: Successfully fetched {len(jobs)} jobs from live API.")
        return jobs

    def _process_jobs(self, jobs):
        """Process the list of jobs into JobInformation objects."""
        jobs_data_models = []
        try:
            for api_job in jobs:
                node = api_job.get("node", {})
                print(node)
                if not node.get("id"):
                    print("Skipping job with no ID.")
                    continue

                job_info = self._create_job_information(node)
                jobs_data_models.append(job_info.model_dump())

        except Exception as e:
            import traceback
            print(f"ERROR: Error processing jobs data: {e}\n{traceback.format_exc()}")

        return jobs_data_models

    def _create_job_information(self, node):
        """Create a JobInformation object from a job node."""
        return JobInformation(
            id=node.get("id"),
            title=node.get("title"),
            publishedDateTime=node.get("publishedDateTime"),
            description=node.get("description", ""),
            durationLabel=node.get("durationLabel"),
            engagement=node.get("engagement"),
            contractType=node.get("job", {}).get("contractTerms", {}).get("contractType"),
            hourlyBudgetMin=node.get("hourlyBudgetMin", {}).get("displayValue") if node.get("hourlyBudgetMin") else None,
            hourlyBudgetMax=node.get("hourlyBudgetMax", {}).get("displayValue") if node.get("hourlyBudgetMax") else None,
            weeklyBudget=node.get("weeklyBudget", {}).get("displayValue") if node.get("weeklyBudget") else None,
            experienceLevel=node.get("experienceLevel"),
            category=node.get("category"),
            subcategory=node.get("subcategory"),
            totalApplicants=node.get("totalApplicants"),
            preferredFreelancerLocation=node.get("preferredFreelancerLocation"),
            preferredFreelancerLocationMandatory=node.get("preferredFreelancerLocationMandatory", False),
            skills=[skill.get("prettyName") for skill in node.get("skills", []) if skill and skill.get("prettyName")],
            clientCompanyName=node.get("client", {}).get("companyName"),
            clientTotalPostedJobs=node.get("client", {}).get("totalPostedJobs"),
            clientTotalReviews=node.get("client", {}).get("totalReviews"),
            clientTotalFeedback=node.get("client", {}).get("totalFeedback"),
            clientTotalSpent=node.get("client", {}).get("totalSpent", {}).get("displayValue") if node.get("client", {}).get("totalSpent") else None
        )

    def _handle_api_error(self, error):
        """Handle API errors."""
        import traceback
        error_message = f"Upwork API Error: Failed to fetch jobs from Upwork API: {error}\n{traceback.format_exc()}"
        print(error_message)
        raise UpworkApiError(error_message)