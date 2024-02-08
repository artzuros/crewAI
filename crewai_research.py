import os
from crewai import Agent, Task, Crew, Process
from langchain.llms import Ollama
from langchain.tools import DuckDuckGoSearchRun

search_tool = DuckDuckGoSearchRun()

ollama_mistral = Ollama(model = 'mistral')

researcher = Agent(
    role="Senior Research Analyst",
    goal = "Uncover cutting edfe developments in AI and Data Science",
    backstory = ''' You are a Senior Research Analyst at a leading tech think tank.
    Your expertise lies in identifying emerging trends and technologies in the AI and Data Science space.
    You have a knack for dissecting complex data and presenting actoinable insights.
    ''',
    verbose= True,
    allow_delegation= False,
    tools= [search_tool],
    llm = ollama_mistral
)

writer = Agent(
    role = 'Tech Content Strategist',
    goal = 'Craft compelling content on tech advancments',
    backstory = ''' You are a renowned Tech Content Strategist,known for your insughtful and
    engaging articles on technology and innovation. With a deep understanding of the tech industry, you transform complex concets into compelling narratives.''',
    verbose = True,
    allow_delegation = True,
    llm = ollama_mistral
)

research_task = Task(
    description= ''' Conduct a comprehensive analysis of latest developments in AI and Data Science in 2024.
    Identify key trends, breakthrough technologies and their potential impact on the industry.
    Compile your findings in a detailed report. Your final answer MUST be a full analysis report.''',
    agent= researcher,
)

write_task = Task(
    description= ''' Using the insights form the researcher's report, develop an engaging blog post that highlights the most significant AI advancements.
    Your post should be informative yet accessible, catering to a tech-savy audience. Aim for a narrattive that captures the essence of these breakthroughs and their implications for the future.
    Your final answer MUST be a blog post atleast 3 paragraphs long.''', 
    agent= writer,
    )

crew = Crew(
    agents= [researcher, writer],
    tasks= [research_task, write_task],
    verbose= False,
    process= Process.sequential
)

result = crew.kickoff()

print("#############################")
print(result)
