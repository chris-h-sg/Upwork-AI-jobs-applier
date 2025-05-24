from pydantic import BaseModel, Field
from typing import List, Optional

class JobInformation(BaseModel):
    id: str = Field(description="The unique identifier of the job")
    title: str = Field(description="The title of the job")
    publishedDateTime: str = Field(description="The date and time when the job was published")
    description: str = Field(description="The original full job description")
    durationLabel: Optional[str] = Field(default=None, description="The duration label of the job")
    engagement: Optional[str] = Field(default=None, description="The engagement type (e.g., hours per week)")
    contractType: Optional[str] = Field(default=None, description="The type of contract (HOURLY/FIXED)")
    hourlyBudgetMin: Optional[float] = Field(default=None, description="Minimum hourly budget")
    hourlyBudgetMax: Optional[float] = Field(default=None, description="Maximum hourly budget")
    weeklyBudget: Optional[float] = Field(default=None, description="Weekly budget amount")
    experienceLevel: Optional[str] = Field(default=None, description="Required experience level")
    category: Optional[str] = Field(default=None, description="Job category")
    subcategory: Optional[str] = Field(default=None, description="Job subcategory")
    totalApplicants: Optional[int] = Field(default=None, description="Total number of applicants")
    preferredFreelancerLocation: Optional[List[str]] = Field(default=None, description="List of preferred freelancer locations, or None if no preference")
    preferredFreelancerLocationMandatory: Optional[bool] = Field(default=False, description="Whether location is mandatory")
    skills: List[str] = Field(default_factory=list, description="List of required skills")
    clientCompanyName: Optional[str] = Field(default=None, description="Client's company name")
    clientTotalPostedJobs: Optional[int] = Field(default=None, description="Total jobs posted by client")
    clientTotalReviews: Optional[int] = Field(default=None, description="Total reviews received by client")
    clientTotalFeedback: Optional[float] = Field(default=None, description="Client's feedback score")
    clientTotalSpent: Optional[float] = Field(default=None, description="Total amount spent by client")

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