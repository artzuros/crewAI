import os
from crewai import Agent
from utils import *

from langchain_community.llms import Ollama

from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper

wrapper = DuckDuckGoSearchAPIWrapper(region="in-en", time="d", max_results=1)
search_tool = DuckDuckGoSearchRun(wrapper=wrapper)

ollama_mistral = Ollama(model="mistral")

taskAssigner = Agent(
    role="Task_Assigner",
    goal="""Interpret text input and decide which Calendar Agent is to be called to complete the task""",
    backstory="""Task Assigner is an expert agent who has expertise in natural language processing. He\'s been working with the team for over three years now. 
    He always knows which calendar agent has to be assigned the task based on the input. Decide which calendar agent
    (eventCreater (add events to calendar), eventModifier (modifies already existing events),
    eventDeleter (deletes event) or eventbusyTime(finds when during the day the calendar has an event))
    should the task be given to and assign the task to that agent.
    ONLY output the name of the agent to whom the task is to be assigned.""",
    verbose=True,
    allow_delegation=True,
    llm=ollama_mistral,
    tools=[]#search_tool]
)

##Calendar AGENTS
eventCreater = Agent(
    role="Event_Creater",
    goal="""Create a Calendar event based on the Args passed""",
    backstory="""Event Creater is an expert agent who has expertise in creating events in Google Calendar. He\'s been working with the team for over three years now. 
    He knows how to create events in Google Calendar using Google Calendar API. His current task is to create a Calendar event based on the Args passed.""",
    verbose=True,
    allow_delegation=True,
    llm=ollama_mistral,
    tools=[]#search_tool]
)

eventModifier = Agent(
    role="Event_Modifier",
    goal="""Modify/updates an event in the Google Calendar""",
    backstory="""Event Modifier is an expert agent who has expertise in modifying events in Google Calendar. He\'s been working with the team for over three years now. 
    He knows how to modify events in Google Calendar using Google Calendar API. His current task is to modify an event in the Google Calendar.""",
    verbose=True,
    allow_delegation=True,
    llm=ollama_mistral,
    tools=[]#search_tool]
)

eventDeleter = Agent(
    role="Event_Deleter",
    goal="""Delete an event in the Google Calendar""",
    backstory="""Event Deleter is an expert agent who has expertise in deleting events in Google Calendar. He\'s been working with the team for over three years now. 
    He knows how to delete events in Google Calendar using Google Calendar API. His current task is to delete an event in the Google Calendar.""",
    verbose=True,
    allow_delegation=True,
    llm=ollama_mistral,
    tools=[]#search_tool]
)

eventbusyTime = Agent(
    role="Event_Busy_Time",
    goal="""Find when during the day the calendar has an event""",
    backstory="""Event Busy Time is an expert agent who has expertise in finding when during the day the calendar has an event. He\'s been working with the team for over three years now. 
    He knows how to find when during the day the calendar has an event using Google Calendar API. His current task is to find when during the day the calendar has an event.""",
    verbose=True,
    allow_delegation=True,
    llm=ollama_mistral,
    tools=[]#search_tool]
)