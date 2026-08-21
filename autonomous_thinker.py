import os
from crewai import Agent, Task, Crew, Process

class RianAutonomousCell:
    def __init__(self):
        print("Initializing R.I.A.N. Autonomous Thinking Cell...")

    def run_task(self, objective_description):
        planner = Agent(
            role='Lead AI Strategist & Executor',
            goal='Analyze objectives, break them down into modular execution steps, and plan solutions.',
            backstory='An advanced autonomous core designed to think logically and handle complex technical workloads.',
            verbose=True
        )

        task = Task(
            description=objective_description,
            expected_output="A structured execution plan, technical breakdown, or code solution.",
            agent=planner
        )

        crew = Crew(
            agents=[planner],
            tasks=[task],
            process=Process.sequential
        )

        result = crew.kickoff()
        return result

print("Autonomous Thinker module ready!")
