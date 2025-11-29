from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from main import ContentPipelineFlow, BlogPost, TweetPost, LinkedinPost, Score

class GenerateRequest(BaseModel):
    topic: str
    content_length: Optional[int] = None # -> state.max_character
    instruction: Optional[str] = None # -> state.instruction

class BlogResponse(BaseModel):
    topic: str
    blog_post: BlogPost | dict | None 
    score: Score | None 

class TweetResponse(BaseModel):
    topic: str 
    tweet_post: TweetPost | dict | None 
    score: Score | None

class LinkedinResponse(BaseModel):
    topic: str 
    tweet_post: LinkedinPost | dict | None 
    score: Score | None

def run_flow(content_type: str, req: GenerateRequest):
    flow = ContentPipelineFlow()

    inputs: dict = {
        "content_type": content_type,
        "topic": req.topic,
        "instruction": req.instruction,
        "max_characters": req.content_length
    }

    if req.content_length is not None: 
        inputs["max_characters"] = req.content_length
    if req.instruction is not None:
        inputs["instruction"] = req.instruction
    
    flow.kickoff(inputs=inputs)
    return flow.state 


app = FastAPI(title="Social Content Pipeline API")

@app.post("/content/blog", response_model = BlogResponse)
def generate_blog(req: GenerateRequest):
    state = run_flow("blog", req)
    return BlogResponse(
        topic=state.topic,
        blog_post=state.blog_post,
        score=state.score,
    )

@app.post("/content/tweet", response_model = TweetResponse)
def generate_tweet(req: GenerateRequest):
    state = run_flow("tweet", req)
    return TweetResponse(
        topic=state.topic,
        tweet_post=state.tweet_post,
        score=state.score,
    )

@app.post("/content/linkedin", response_model = LinkedinResponse)
def generate_linkedin(req: GenerateRequest):
    state = run_flow("linkedin", req)
    return LinkedinResponse(
        topic=state.topic,
        blog_post=state.linkedin_post,
        score=state.score,
    )
