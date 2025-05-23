# UpworkScribe AI: Automated Jobs Application on Upwork

**UpworkScribe AI is your partner in navigating the competitive world of freelancing. It automates aspects of Upwork job searching and application generation to help you secure more projects and grow your freelance career. 🚀**

This project has been updated to use the official Upwork API for fetching job postings, making it more robust and reliable than web scraping methods. This requires setting up Upwork API credentials.

## Important Note on Current Status

**Please be aware:** The job fetching mechanism (`UpworkJobScraper` in `src/scraper.py`) is currently configured to use **simulated API data** for demonstration and development purposes. This allows you to run the application and see its workflow without a live API connection.

To connect to the live Upwork API and fetch real job postings, you **must** complete the OAuth 2.0 setup as described in the "Setting up Upwork API Access" section below and then modify `src/scraper.py` to use your actual API client configuration and tokens.

## The Challenge of Modern Freelancing

The freelance marketplace has undergone a dramatic transformation in the digital age. While platforms like Upwork have opened up a world of opportunities, they have also intensified competition. Freelancers often find themselves spending countless hours searching for suitable projects, tailoring proposals, and crafting unique cover letters. This process can be not only time-consuming but also mentally exhausting, leading to missed opportunities and proposal fatigue.

## How UpworkScribe AI Helps

UpworkScribe AI simplifies the freelancing process by acting as your personal assistant. It offers:

* **Automatic Job Scanning and Qualification:** Saves freelancers time by identifying and qualifying the most relevant job opportunities.
* **Personalized Cover Letter:** automate the Creation of tailored cover letters for each project, increasing the chances of standing out to clients.
* **Interview Preparation Support:** Generates materials to help freelancers prepare for client meetings and secure jobs with confidence.
* **24/7 Availability:** can be setup to work around the clock, ensuring no opportunities are missed, even when you're offline.
* **Cost-Effective:** Offers powerful features at a low cost, making it accessible to freelancers at all levels.
* **Support For Multiple LLM Providers:** Can integrate with various large language models, offering flexibility and adaptability to meet different user needs.

## Features

### Job Fetching and Classification (via Upwork API)

- **Job Monitoring**: The system fetches new project listings from Upwork via the official API, based on the freelancer's provided job titles, ensuring up-to-date opportunities.
- **Intelligent Job Scoring**: Each job receives a score based on various criteria such as: match with freelancer experience & skills, budget, duration, client history, and past projects on the platform. Only jobs scoring 7/10 or higher proceed for further analysis.

### AI Cover Letter and Interview Script Generation

- **Dynamic Cover Letter Creation**: AI agents crafts custom cover letters based on each job description and.
- **Personalized Content**: Tailors cover letters to reflect the user’s unique writing style, skills, and relevant experiences.
- **Interview Script and Questions**: Prepares a list of potential interview questions and a script for the freelancer, covering job-specific topics to improve interview readiness.
- **Keyword Optimization**: Incorporates job-related keywords to enhance proposal relevance and client interest.

---

## How It Works

1. **User Input**: The process starts with the user entering a job title.
2. **Job Fetching**: The system fetches job listings from Upwork via the official API that match the user-provided search queries, gathering relevant opportunities.
3. **Job Scoring and Filtering**: Each job is scored by an AI agent, and only jobs with a score of 7/10 or higher are processed further, filtering out lower-quality matches.
5. **Cover Letter and Interview Preparation**: For strong job matches, the system generates:
   - A personalized cover letter emphasizing the user’s qualifications and alignment with the job.
   - A custom interview preparation script including potential questions to prepare the user for discussions with potential clients.
6. **Review and Submission**: The generated cover letter, interview script, and questions are saved for user review, allowing for final adjustments before submission to prospective clients.

### System Flowchart

This is the detailed flow of the system:

[![](https://mermaid.ink/img/pako:eNqdlMGO2jAQhl_FMlJPoNJyKETtSiEBxGqL2rJ7Sjg49oRYBDuyHegKePc6TlKye1olUiJP8n_zz4xiXzCVDLCH94oUGXoOY4Hs9Ri9aFBoLYrSaPQoE_TMTQ47NBo9ID_aUqsG9FKcpTpUn_Wu5nwnmFuBVIBqGesK6ue8kl1r0Xf07fOX8RWF623g_wmjkGtKFENP8jyqFFzsuwm66MOPhg0uQQb0gFKpXLE_iaEZ6FvXM3DgLyUpaNeStp7RCgQoYsBhflHknBLDpUCBFAaE2XXhjWwzX9FiE0b2ftNW6Lpf3JMG8mSn-ATGgNp1Ncu7Zm191InDuRoXLwz6hH6XoKsi3g5t4chVtCUnQC3uhvuu2GUtrIOVC4JY1KE2r7ltFqU8z70BTdOhNkoewBtMJpNmPTpzZjLva_F3SGUulTcYj8dd3G_wdHbHp9PpR_F5gydJL_egdU-SPnjYuqe98EXrns764Mv_o-uFrxp81s-92WNNEsZYrwlseiXAQ3wEdSSc2dPmUiWMscngCDH27JIRdYhxLG5WR0ojt6-CYs-oEoZYyXKfYS8lubZRWTD744ec2CPr2Ly9_QPS1oVz?type=png)](https://mermaid.live/edit#pako:eNqdlMGO2jAQhl_FMlJPoNJyKETtSiEBxGqL2rJ7Sjg49oRYBDuyHegKePc6TlKye1olUiJP8n_zz4xiXzCVDLCH94oUGXoOY4Hs9Ri9aFBoLYrSaPQoE_TMTQ47NBo9ID_aUqsG9FKcpTpUn_Wu5nwnmFuBVIBqGesK6ue8kl1r0Xf07fOX8RWF623g_wmjkGtKFENP8jyqFFzsuwm66MOPhg0uQQb0gFKpXLE_iaEZ6FvXM3DgLyUpaNeStp7RCgQoYsBhflHknBLDpUCBFAaE2XXhjWwzX9FiE0b2ftNW6Lpf3JMG8mSn-ATGgNp1Ncu7Zm191InDuRoXLwz6hH6XoKsi3g5t4chVtCUnQC3uhvuu2GUtrIOVC4JY1KE2r7ltFqU8z70BTdOhNkoewBtMJpNmPTpzZjLva_F3SGUulTcYj8dd3G_wdHbHp9PpR_F5gydJL_egdU-SPnjYuqe98EXrns764Mv_o-uFrxp81s-92WNNEsZYrwlseiXAQ3wEdSSc2dPmUiWMscngCDH27JIRdYhxLG5WR0ojt6-CYs-oEoZYyXKfYS8lubZRWTD744ec2CPr2Ly9_QPS1oVz)

---

## Tech Stack

-   **LangGraph & LangChain**: Frameworks used for building AI agents and interacting with LLMs (GPT-4o, Llama 3, Gemini).
-   **LangSmith**: For monitoring the different LLM calls and AI agents' interactions.
-   **`python-upwork-oauth2`**: For interacting with the official Upwork API.

---

## How to Run

### Setup

1. **Clone the repository:**

   ```sh
   git clone https://github.com/kaymen99/Upwork-AI-jobs-applier.git
   cd Upwork-AI-jobs-applier
   ```

2. **Set up environment variables:**

   Create a `.env` file in the root directory of the project and add your API keys, see `.env.example` to know all the parameters you will need.

### Setting up Upwork API Access

This project uses the official Upwork API via the `python-upwork-oauth2` library to fetch job postings. Setting this up requires several steps:

1.  **Obtain Initial API Credentials (`Client ID` and `Client Secret`):**
    To begin, you need a `Client ID` and a `Client Secret` from Upwork. You can obtain these by registering your application and creating an API key on the Upwork developer portal: **[Link to Upwork Developer Portal - User to fill this in]**.

2.  **Configure Environment Variables:**
    Once you have your `Client ID` and `Client Secret`, create a `.env` file in the root directory by copying `.env.example`. Add your credentials to this `.env` file:
    ```env
    UPWORK_CLIENT_ID="your_client_id_here"
    UPWORK_CLIENT_SECRET="your_client_secret_here"
    ```

3.  **OAuth 2.0 Authentication Flow (Crucial Step for Live Data):**
    The `python-upwork-oauth2` library requires completing Upwork's OAuth 2.0 authentication flow. This process typically involves:
    *   Redirecting a user (you) to an Upwork authorization URL.
    *   Authorizing the application.
    *   Upwork redirecting back to a specified `redirect_uri` with an authorization code.
    *   Exchanging this code for an **access token** and a **refresh token**.

    **Important:** The application's API client (`src/scraper.py`) currently contains a **placeholder** for the Upwork client initialization and token management. **You will need to consult the `python-upwork-oauth2` library documentation and examples to fully implement the OAuth setup, token acquisition, storage (e.g., in your `.env` file or a secure vault), and refresh logic to fetch live data.** This is a one-time setup to get your tokens, which then need to be made available to the application (e.g., via environment variables like `UPWORK_ACCESS_TOKEN`, `UPWORK_REFRESH_TOKEN`).

    Ensure all required variables are correctly set in your `.env` file before attempting to run with a live API connection.

### Run Locally

#### Prerequisites

- Python 3.9+
- Python 3.9+
- Necessary Python libraries (listed in `requirements.txt`).
- API keys for your chosen LLM provider(s) (e.g., OpenAI, Google, Groq) set in your `.env` file.
- Upwork API `Client ID` and `Client Secret` (and eventually access/refresh tokens) set in your `.env` file for live data access (see "Setting up Upwork API Access").

#### Running the Application

1. **Create and activate a virtual environment:**

   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

2. **Install the required packages:**

   ```sh
   pip install -r requirements.txt
   ```

3. **Start the main automation workflow:**

   ```sh
   python main.py
   ```
   This runs the full job processing and application generation workflow. It will use the job title configured inside `main.py` for fetching jobs (currently using simulated job data as per the "Important Note" above). Generated cover letters and other outputs are saved as configured.

4. **Test the Upwork jobs fetching script (standalone):**

   ```sh
   python scrape_upwork_jobs.py
   ```
   This script specifically fetches jobs based on the query defined within it (currently using simulated job data) and saves them to `upwork_jobs_data.csv`. It's useful for testing the job fetching and data saving parts independently.

---

### Run in Docker

#### Prerequisites

- Docker installed on your machine.
- API keys for LLM models you want to use (OpenAI, Claude, Gemini, Groq,...)

#### Running the Application

1. **Build and run the Docker container:**

   ```sh
   docker build -t upwork-auto-jobs-applier-using-ai .
   docker run -e OPENAI_API_KEY=YOUR_API_KEY_HERE -v ./data:/usr/src/app/data upwork-auto-jobs-applier-using-ai
   ```

   The application will start the main workflow (currently using simulated job data). Ensure your `.env` file is correctly populated with LLM API keys if you build the image with it or pass them as environment variables. Docker usage for live Upwork API data would require careful management of Upwork API tokens.

2. **Test the Upwork jobs fetching script** in Docker:

   ```sh
   docker run -e OPENAI_API_KEY=YOUR_API_KEY_HERE -v ./data:/usr/src/app/data upwork-auto-jobs-applier-using-ai python scrape_upwork_jobs.py
   ```
   This will run the standalone job fetching script (currently using simulated data) and save the output CSV to the bind-mounted `./data` directory.

---

### Customization

- To use this automation for your own profile, just add your profile into `files/profile.md` and remove the example profile.

- You can customize the behavior of each AI agent by modifying the corresponding agent prompt in the `prompts` script.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any changes.

## Contact

If you have any questions or suggestions, feel free to contact me at `aymenMir1001@gmail.com`.
