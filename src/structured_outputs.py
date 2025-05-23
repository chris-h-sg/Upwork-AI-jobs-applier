from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional

class JobType(str, Enum):
    FIXED = "Fixed"
    HOURLY = "Hourly"
    NOT_SPECIFIED = "Not Specified" # Added to handle cases where job type isn't clear

class ClientInformation(BaseModel):
    # Fields from simulated API data
    country: Optional[str] = Field(default=None, description="The client's country")
    feedback_score: Optional[float] = Field(default=None, description="The client's feedback score")
    jobs_posted: Optional[int] = Field(default=None, description="The total number of jobs posted by the client")
    payment_verification_status: Optional[bool] = Field(default=None, description="Client's payment verification status")

    # Fields that were originally required but not in current simulated data - making them optional
    joined_date: Optional[str] = Field(default=None, description="The date the client joined the platform")
    total_spent: Optional[str] = Field(default=None, description="The total amount spent by the client ($)") 
    company_profile: Optional[str] = Field(default=None, description="The client's company profile or description")
    # 'location' was renamed to 'country' to match API. 'total_hires' renamed to 'jobs_posted'.

class JobInformation(BaseModel):
    title: str = Field(description="The title of the job")
    description: str = Field(description="The original full job description, must be extracted without any summarization or omission.")
    job_type: JobType = Field(description="The type of the job (Fixed or Hourly)")
    experience_level: Optional[str] = Field(default=None, description="The experience level required for the job") # Made Optional
    duration: Optional[str] = Field(default=None, description="The duration of the job") # Also making duration optional for robustness
    payment_rate: Optional[str] = Field(
        description="""
        The payment rate for the job. Can be in several formats:
        - Hourly rate range: '$15.00-$25.00' or '$15-$25'
        - Fixed rate: '$500' or '$1,000'
        - Budget range: '$500-$1,000'
        All values should include the '$' symbol.
        """
    )
    client_information: Optional[ClientInformation] = Field(
        description="The description of the client including location, number of hires, total spent, etc."
    )
    proposal_requirements: Optional[str] = Field(default=None, # Added default=None
        description="Notes left by the client regarding the proposal requiremenets. For example, instructions or special requests such as 'Begin your proposal with "" to confirm you’ve read the full posting.'"
    )
    
class JobScore(BaseModel):
    job_id: str = Field(description="The id of the job")
    score: int = Field(description="The score of the job")

class JobScores(BaseModel):
    scores: List[JobScore] = Field(description="The list of job scores")
    
class CoverLetter(BaseModel):
    letter: str = Field(description="The generated cover letter")
    
class CallScript(BaseModel):
    script: str = Field(description="The generated call script")
     
class JobApplication(BaseModel):
    job_description: str = Field(description="The full description of the job")
    cover_letter: str = Field(description="The generated cover letter")
    interview_preparation: str = Field(description="The generated interview preparation")