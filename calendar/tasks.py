from crewai import Task
from utils import *
from agents import *

from langchain.tools import BaseTool, StructuredTool, tool

input_text = 'book my calendar for today evening at 6pm for a meeting with my team'

task_taskAssigner = Task(
    description="""Interpret the meaning and decide whether the task is for eventCreater, eventModifier, eventDeleter or eventbusyTime agent and ONLY output the name of the agent to whom the task should be assigned, for the following text"""+ 
                input_text,
    agent=taskAssigner,
    verbose=True,
)

task_eventCreater = Task(
    description="""You will NOT get in action unless taskAssigner has called out your name. IF your name has been called out only then you will get into action otherwise your output will be the same output as of taskAssigner."""+ 
                """Create a Calendar event based on the Args passed, for the following text"""+ 
                input_text,
    agent=eventCreater,
    verbose=True,
)

task_eventModifier = Task(
    description="""You will NOT get in action unless taskAssigner has called out your name. IF your name has been called out only then you will get into action otherwise your output will be the same output as of taskAssigner."""+ 
                """Modify/updates an event in the Google Calendar, for the following text"""+ 
                input_text,
    agent=eventModifier,
    verbose=True,
)

task_eventDeleter = Task(
    description="""You will NOT get in action unless taskAssigner has called out your name. IF your name has been called out only then you will get into action otherwise your output will be the same output as of taskAssigner."""+ 
                """Delete an event in the Google Calendar, for the following text"""+ 
                input_text,
    agent=eventDeleter,
    verbose=True,
)

task_eventbusyTime = Task(
    description="""You will NOT get in action unless taskAssigner has called out your name. IF your name has been called out only then you will get into action otherwise your output will be the same output as of taskAssigner."""+ 
                """Find when during the day the calendar has an event, for the following text"""+ 
                input_text,
    agent=eventbusyTime,
    verbose=True,
)