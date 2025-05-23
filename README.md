# UpworkScribe AI

UpworkScribe AI is a project designed to automate aspects of Upwork job searching and application generation using AI.

---
**## Important Note on Current Status**
> **Please be aware:** The job fetching mechanism (`UpworkJobScraper` in `src/scraper.py`) is currently configured to use **simulated API data** for demonstration and development purposes. This allows you to run the application and see its workflow without a live API connection.
>
> To connect to the live Upwork API and fetch real job postings, you **must** complete the OAuth 2.0 setup as described in the "Setting up Upwork API Access" section below and then modify `src/scraper.py` to use your actual API client configuration and tokens.

## How to Run

### Setup

1. **Clone the repository:**

   ```sh
   git clone https://github.com/kaymen99/Upwork-AI-jobs-applier.git
   cd Upwork-AI-jobs-applier
   ```

2. **Prepare environment variables:**

   Copy the `.env.example` file to a new file named `.env` in the project root. You will need to populate this file with your API keys for LLM providers and your Upwork API credentials as detailed below.

### Setting up Upwork API Access

This project uses the official Upwork API via the `python-upwork-oauth2` library to fetch job postings. This requires setting up Upwork API credentials in your `.env` file:

1.  **Obtain Initial API Credentials (`Client ID` and `Client Secret`):**
    To begin, you need a `Client ID` and a `Client Secret` from Upwork. You can obtain these by registering your application and creating an API key on the Upwork developer portal: **https://developers.upwork.com/**.
    Once obtained, add them to your `.env` file:
    ```env
    UPWORK_CLIENT_ID="your_client_id_here"
    UPWORK_CLIENT_SECRET="your_client_secret_here"
    ```

2.  **OAuth 2.0 Authentication Flow (Crucial Step for Live Data):**
    The `python-upwork-oauth2` library requires completing Upwork's OAuth 2.0 authentication flow. This process typically involves:
    *   Redirecting a user (you) to an Upwork authorization URL.
    *   Authorizing the application.
    *   Upwork redirecting back to a specified `redirect_uri` with an authorization code.
    *   Exchanging this code for an **access token** and a **refresh token**.

    **Important: Completing the OAuth 2.0 flow is crucial for fetching live job data.** The application's API client (`src/scraper.py`) currently uses **simulated data** and contains a **placeholder** for the Upwork client initialization.

    To switch to live Upwork API data:
    1.  **Implement OAuth Flow:** You **must** consult the `python-upwork-oauth2` library documentation ([https://github.com/upwork/python-upwork-oauth2](https://github.com/upwork/python-upwork-oauth2)) and its examples to fully implement the OAuth 2.0 setup. This is a one-time process to acquire your `Access Token` and `Refresh Token`.
    2.  **Store Your Tokens Securely:** After successfully completing the OAuth flow and obtaining your tokens, you need to store them securely. Add them to your `.env` file, similar to your `Client ID` and `Client Secret`:
        ```env
        UPWORK_ACCESS_TOKEN="your_access_token_here"
        UPWORK_REFRESH_TOKEN="your_refresh_token_here"
        ```
        **Do not commit your `.env` file if it contains sensitive credentials.** Ensure it's listed in your `.gitignore` file.
    3.  **Modify `src/scraper.py`:** Update the `UpworkJobScraper` class in `src/scraper.py` to use your `Client ID`, `Client Secret`, `Access Token`, and `Refresh Token` for live API calls, replacing the simulated data logic. You will need to initialize and use the `upwork.Client` with these credentials as shown in the `python-upwork-oauth2` library examples.

    Ensure all Upwork API related variables (`UPWORK_CLIENT_ID`, `UPWORK_CLIENT_SECRET`, `UPWORK_ACCESS_TOKEN`, `UPWORK_REFRESH_TOKEN`) are correctly set in your `.env` file and utilized by `src/scraper.py` before attempting to run with a live API connection.

### Run Locally

#### Prerequisites

- Python 3.9 or newer
- Necessary Python libraries (listed in `requirements.txt`).
- API keys for your chosen LLM provider(s) (e.g., OpenAI, Google, Groq) set in your `.env` file.
- Upwork API `Client ID`, `Client Secret`, `Access Token`, and `Refresh Token` set in your `.env` file for live data access (as detailed in "Setting up Upwork API Access").

#### Running the Application

1. **Create and activate a virtual environment:**

   ```sh
   python -m venv venv
   ```
   *   On Unix-like systems (Linux, macOS):
       ```sh
       source venv/bin/activate
       ```
   *   On Windows:
       ```sh
       venv\Scripts\activate
       ```

2. **Install the required packages:**

   ```sh
   pip install -r requirements.txt
   ```

3. **Start the main automation workflow:**

   ```sh
   python main.py
   ```
   This runs the full job processing and application generation workflow. It will use the job title configured inside `main.py` for fetching jobs (currently using simulated job data as per the "Important Note" above unless live API setup is completed). Generated cover letters and other outputs are saved as configured.

4. **Test the Upwork jobs fetching script (standalone):**

   ```sh
   python scrape_upwork_jobs.py
   ```
   This script specifically fetches jobs based on the query defined within it (currently using simulated job data unless live API setup is completed) and saves them to `upwork_jobs_data.csv`. It's useful for testing the job fetching and data saving parts independently.

---

### Customization

- To use this automation for your own profile, just add your profile into `files/profile.md` and remove the example profile.

- You can customize the behavior of each AI agent by modifying the corresponding agent prompt in the `prompts` script.
