from pydantic import BaseModel
from crewai import Agent, Task, Crew
from crewai.project import CrewBase, agent, task, crew

class Score(BaseModel):
    score: int
    reason: str 

@CrewBase
class ContentEvalCrew:

    @agent
    def seo_expert_agent(self):
        return Agent(
            config=self.agents_config["seo_expert_agent"]
        )
    
    @task
    def seo_expert_task(self):
        return Task(
            config=self.tasks_config["seo_expert_task"],
            output_pydantic=Score
        )
    
    @agent
    def virality_expert_agent(self):
        return Agent(
            config=self.agents_config["virality_expert_agent"]
        )
    
    @task
    def virality_expert_task(self):
        return Task(
            config=self.tasks_config["virality_expert_task"],
            output_pydantic=Score
        )
    
    @crew 
    def seo_crew(self):
        return Crew(
            agents=[self.seo_expert_agent()],
            tasks=[self.seo_expert_task()],
            verbose=True,
        )

    @crew
    def virality_crew(self):
        return Crew(
            agents=[self.virality_expert_agent()],
            tasks=[self.virality_expert_task()],
            verbose=True,
        )
