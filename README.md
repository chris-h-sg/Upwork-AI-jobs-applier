# UpworkScribe AI

UpworkScribe AI is a project designed to automate aspects of Upwork job searching and application generation using AI.

---
**## Important Note on Current Status**
> **Please be aware:** A successful connection to the Upwork API is **mandatory** for this application to function. The job fetching mechanism (`UpworkJobScraper` in `src/scraper.py`) relies entirely on live API data.
>
> You **must** correctly configure your Upwork API credentials in the `.env` file and successfully complete the OAuth 2.0 authentication flow as described in the "Setting up Upwork API Access" section.
>
> If the API setup is not complete, if credentials are incorrect, or if the OAuth flow is not successfully navigated, the application will **exit with an error message**. There is no fallback to simulated or demonstration data.

## How to Run

### Setup

1. **Clone the repository:**

   ```sh
   git clone https://github.com/kaymen99/Upwork-AI-jobs-applier.git
   cd Upwork-AI-jobs-applier
   ```

2. **Prepare environment variables:**

   Copy the `.env.example` file to a new file named `.env` in the project root. You will need to populate this file with your API keys for LLM providers and your Upwork API credentials as detailed below. The Upwork related variables are:
   *   `UPWORK_CLIENT_ID` (Mandatory): Your Upwork API client ID.
   *   `UPWORK_CLIENT_SECRET` (Mandatory): Your Upwork API client secret.
   *   `UPWORK_REDIRECT_URI` (Mandatory): The redirect URI configured in your Upwork API application settings. This is where Upwork will redirect you during the OAuth flow. For CLI applications where a web server isn't running, you can often use a placeholder like `https://localhost` or `http://localhost:8080/callback`, as long as it's registered with your Upwork app. You'll manually copy the URL from your browser after redirection.
   *   `UPWORK_ACCESS_TOKEN` (Optional): Your Upwork API access token.
   *   `UPWORK_REFRESH_TOKEN` (Optional): Your Upwork API refresh token.
   *   `UPWORK_EXPIRES_AT` (Optional): The Unix timestamp for when your access token expires.

   The access token, refresh token, and expiry time will be obtained and displayed by the application after the first successful OAuth 2.0 flow. You should add them to your `.env` file to bypass interactive authorization on subsequent runs.

### Setting up Upwork API Access

This project uses the official Upwork API via the `python-upwork-oauth2` library to fetch job postings. This requires setting up Upwork API credentials in your `.env` file as described above.

**Interactive OAuth 2.0 Flow (Crucial Step for Live Data):**

If `UPWORK_ACCESS_TOKEN`, `UPWORK_REFRESH_TOKEN`, and `UPWORK_EXPIRES_AT` are not found or are invalid in your `.env` file, the application will automatically initiate an interactive OAuth 2.0 flow when it first tries to connect to the Upwork API:

1.  **Provide Credentials:** Ensure `UPWORK_CLIENT_ID`, `UPWORK_CLIENT_SECRET`, and `UPWORK_REDIRECT_URI` are correctly set in your `.env` file.
2.  **Authorization Prompt:** The application will display an authorization URL in the console.
3.  **Browser Authorization:** Copy this URL and open it in your web browser. Log in to Upwork if prompted and authorize the application.
4.  **Redirect and Code Retrieval:** After authorization, Upwork will redirect your browser to your specified `UPWORK_REDIRECT_URI`. The URL in your browser's address bar will now contain an authorization `code` (e.g., `https://your-redirect-uri/?code=YOUR_AUTH_CODE&state=...`).
5.  **Paste Callback URL:** Copy the **entire** redirected URL from your browser's address bar and paste it back into the application when prompted.
6.  **Token Retrieval and Storage:** The application will use the authorization code to fetch your access token, refresh token, and expiry time. It will then print these values to the console.
    **IMPORTANT:** You **must** copy these new token values (`UPWORK_ACCESS_TOKEN`, `UPWORK_REFRESH_TOKEN`, `UPWORK_EXPIRES_AT`) and save them into your `.env` file. This will allow the application to use these tokens directly on subsequent runs, bypassing the interactive browser authorization step.

    Example of token variables to add/update in `.env` after successful OAuth:
    ```env
    UPWORK_ACCESS_TOKEN="the_long_access_token_string_from_console"
    UPWORK_REFRESH_TOKEN="the_refresh_token_string_from_console"
    UPWORK_EXPIRES_AT="the_timestamp_from_console" 
    ```

**Note on `src/scraper.py`:** The `UpworkJobScraper` class in `src/scraper.py` is now designed to handle this OAuth flow automatically. You no longer need to modify it manually for token setup, provided your initial `Client ID`, `Client Secret`, and `Redirect URI` are correct in `.env`.

Ensure all required Upwork API related variables are correctly set in your `.env` file and that you complete the OAuth flow as prompted. If the API connection cannot be established (e.g., due to incorrect credentials, incomplete OAuth flow, or network issues), the application will not be able to fetch jobs and will raise an error.

### Run Locally

#### Prerequisites

- Python 3.9 or newer
- Necessary Python libraries (listed in `requirements.txt`).
- API keys for your chosen LLM provider(s) (e.g., OpenAI, Google, Groq) set in your `.env` file.
- Upwork API `UPWORK_CLIENT_ID`, `UPWORK_CLIENT_SECRET`, and `UPWORK_REDIRECT_URI` set in your `.env` file. Access and refresh tokens will be obtained via the OAuth flow if not present.

#### Running the Application

1. **Create and activate a virtual environment:**

   ```sh
   python -m venv .venv
   ```
   *   On Unix-like systems (Linux, macOS):
       ```sh
       source .venv/bin/activate
       ```
   *   On Windows:
       ```sh
       .venv\Scripts\activate
       ```

2. **Install the required packages:**

   ```sh
   pip install -r requirements.txt
   ```

3. **Start the main automation workflow:**

   ```sh
   python main.py
   ```
   This runs the full job processing and application generation workflow. It will use the job title configured inside `main.py` for fetching jobs. A successful Upwork API connection is required. Generated cover letters and other outputs are saved as configured.

4. **Test the Upwork jobs fetching script (standalone):**

   ```sh
   python scrape_upwork_jobs.py
   ```
   This script specifically fetches jobs based on the query defined within it and saves them to `upwork_jobs_data.csv`. A successful Upwork API connection is required. It's useful for testing the job fetching and data saving parts independently.

---

### Customization

- To use this automation for your own profile, just add your profile into `files/profile.md` and remove the example profile.

- You can customize the behavior of each AI agent by modifying the corresponding agent prompt in the `prompts` script.
