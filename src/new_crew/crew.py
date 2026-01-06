from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
import os

MODEL_NAME = os.getenv("CREW_MODEL", "groq/llama-3.1-8b-instant")

@CrewBase
class OrganizationFeedbackCrew:
    """Crew to analyze organization feedback WITHOUT external tools"""

    @agent
    def feedback_collector(self) -> Agent:
        return Agent(
            config=self.agents_config["feedback_collector"],
            llm=LLM(model=MODEL_NAME, temperature=0.6),
            tools=[],          # 🔥 NO SERPER
            max_iter=1,        # 🔥 PREVENT RETRIES
            allow_delegation=False
        )

    @agent
    def industry_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["industry_analyst"],
            llm=LLM(model=MODEL_NAME, temperature=0.6),
            tools=[],
            max_iter=1,
            allow_delegation=False
        )

    @agent
    def insight_synthesizer(self) -> Agent:
        return Agent(
            config=self.agents_config["insight_synthesizer"],
            llm=LLM(model=MODEL_NAME, temperature=0.5),
            tools=[],
            max_iter=1,
            allow_delegation=False
        )

    @task
    def collect_user_feedback(self) -> Task:
        return Task(config=self.tasks_config["collect_user_feedback"])

    @task
    def analyze_industry_feedback(self) -> Task:
        return Task(config=self.tasks_config["analyze_industry_feedback"])

    @task
    def synthesize_final_insights(self) -> Task:
        return Task(config=self.tasks_config["synthesize_final_insights"])

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )
