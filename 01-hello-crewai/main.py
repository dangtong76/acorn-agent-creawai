from dotenv import load_dotenv
from crewai import Agent, Task, Crew
from crewai.project import CrewBase, agent, task, crew 
from tools import count_words

load_dotenv()

@CrewBase
class TranslatorCrew:

    @agent # Role, Goal, BackStory
    def translator_agent(self):
        return Agent(
            config=self.agents_config["translator_agent"]
        )
    
    @agent
    def counter_agent(self):
        return Agent(
            config=self.agents_config["counter_agent"],
            tools=[count_words],
            allow_delegation=False
        )
    
    @task
    def translate_task(self):
        # Must : Description, Expected Output
        return Task(
            config=self.tasks_config["translate_task"]
        )
    
    @task
    def counter_task(self):
        return Task(
            config=self.tasks_config["counter_task"]
        )
    
    @crew
    def assemble_crew(self):
        return Crew(
            agents = self.agents,
            tasks = self.tasks,
            verbose=True
        )
    
TranslatorCrew().assemble_crew().kickoff(
    inputs = {
        "sentence": "I’m Dangtong, a software engineer.I turned 50 this year, and honestly, it’s been pretty hard."  
    }
)
    
    