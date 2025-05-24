# This file is deprecated.
# The main entry point for this application is now app.py.

# import asyncio # Old import
# from dotenv import load_dotenv # Old import
# from src.utils import read_text_file # Old import
# from src.graph import UpworkAutomation # Old import

# # Load environment variables from a .env file # Old logic
# load_dotenv() # Old logic

if __name__ == "__main__":
    print("This script (main.py) is deprecated.")
    print("Please use the new CLI application: python app.py <command>")
    print("For example, to run the full pipeline, use: python app.py main_pipeline")
    print("To fetch jobs: python app.py fetch_jobs")
    print("To grade jobs: python app.py grade_jobs --input-csv <filename>")
    print("To prepare applications: python app.py prepare_applications --input-csv <filename>")
    # # Old logic below
    # # Job title to look for
    # job_title = "AI agent Developer"

    # # load the freelancer profile
    # profile = read_text_file("./files/profile.md")

    # # run automation
    # automation = UpworkAutomation(profile)
    # asyncio.run(automation.run(job_title=job_title))
    
    # # Visualize automation graph as a PNG image
    # # output_path = "./automation_graph.png"  # Specify the desired output path
    # # with open(output_path, "wb") as file:
    # #     file.write(automation.graph.get_graph(xray=True).draw_mermaid_png())
    # # print(f"Graph saved as PNG at {output_path}")
