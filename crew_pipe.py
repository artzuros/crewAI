from utils import *
from crewai import Crew, Process
import re

from utils_mongo import MongoUtils as mu

from crewai import Agent, Task, Crew, Process

### Local LLM running <mistral> via <Ollama> 
from langchain_community.llms import Ollama
ollama_mistral = Ollama(model="mistral")

taskAssigner = Agent(
    role="Task_Assigner",
    goal="""Interpret text input and decide which Calendar Agent is to be called to complete the task""",
    backstory="""Task Assigner is an expert agent who has expertise in natural language processing. He\'s been working with the team for over three years now. 
    He always knows which calendar agent has to be assigned the task based on the input. Decide which calendar agent
    (eventCreater (add events to calendar), eventModifier (modifies already existing events),
    eventDeleter (deletes event), eventbusyTime(finds when during the day the calendar has an event) or eventSearcher (searches for an event))
    should the task be given to and assign the task to that agent.
    ONLY and ONLY output the name of the agent to whom the task is to be assigned and NOTHING ELSE.""",
    verbose=True,
    allow_delegation=True,
    llm=ollama_mistral,
    tools=[]#search_tool]
)

##Calendar AGENTS
eventCreater = Agent(
    role="Event_Creater",
    goal="""Create the arguments for Calendar event based on the input text """,
    verbose=True,
    backstory="""Event Creater is an expert agent who has expertise in creating events in Google Calendar. He\'s been working with the team for over three years now. 
    He knows how to create events in Google Calendar using Google Calendar API. His current task is to create a Calendar event based on the Args passed.""",
    allow_delegation=True,
    llm=ollama_mistral,
    tools=[]#CalendarTool.create_event]
)

eventModifier = Agent(
    role="Event_Modifier",
    goal="""Creates the arguments for Calendar event based on the input text""",
    verbose=True,
    backstory="""Event Modifier is an expert agent who has expertise in modifying events in Google Calendar. He\'s been working with the team for over three years now. 
    He knows how to modify events in Google Calendar using Google Calendar API. His current task is to modify an event in the Google Calendar.""",
    allow_delegation=True,
    llm=ollama_mistral,
    tools=[]#CalendarTool.modify_event]
)

eventDeleter = Agent(
    role="Event_Deleter",
    goal="""Delete an event in the Google Calendar""",
    verbose=True,
    backstory="""Event Deleter is an expert agent who has expertise in deleting events in Google Calendar. He\'s been working with the team for over three years now. 
    He knows how to delete events in Google Calendar using Google Calendar API. His current task is to delete an event in the Google Calendar.""",
    allow_delegation=True,
    llm=ollama_mistral,
    tools=[]#CalendarTool.delete_event]
)

eventbusyTime = Agent(
    role="Event_Busy_Time",
    goal="""Find which day is being talked about.""",
    verbose=True,
    backstory="""Event Busy Time is an expert agent who has expertise in finding which day is being talked about. """,
    allow_delegation=True,
    llm=ollama_mistral,
    tools=[]#CalendarTool.get_busy_time]
)

eventSearcher = Agent(
    role="Event_Searcher",
    goal="""Search for an event in the Google Calendar""",
    verbose=True,
    backstory="""Event Searcher is an expert agent who has expertise in finding and listing events from Google Calendar. He\'s been working with the team for over three years now. 
    He knows how to search events in Google Calendar using Google Calendar API. His current task is to search for an event in the Google Calendar.""",
    allow_delegation=True,
    llm=ollama_mistral,
    tools=[]#CalendarTool.list_events]
)

### Tasks

def tasks(input = None):

    input_text = input + 'Today date is 02/03/2024 in MM/DD/YYYY format'

    task_taskAssigner = Task(
        description="""Interpret the meaning and decide whether the task is for eventCreater, eventModifier, eventDeleter, eventbusyTime or eventSearcher agent and ONLY output the name of the agent to whom the task should be assigned, for the following text"""+ 
                    input_text,
        agent=taskAssigner,
        verbose=True,
    )

    task_eventCreater = Task(
        description="""Create the arguments  in this format ( If summmary is not specified then take summary as 'N/A', if location is not specified then take location as 'N/A', if email_reminder_minutes is not specified then take email_reminder_minutes as 24*60, if popup_reminder_minutes is not specified then take popup_reminder_minutes as 30)
        {
                'event_summary': summary,
                'event_location': location,
                'start_time': start_time, ISO8601 Format +5:30 
                'end_time': end_time, ISO8601 Format +5:30 
                'email_reminder_minutes': email_reminder_minutes,
                'popup_reminder_minutes': popup_reminder_minutes,
            }
        for a Calendar event for the following text. ONLY PRINT THE DICTIONARY AND NOTHING ELSE"""+ 
                    input_text,
        agent=eventCreater,
        verbose=True,
    )

    task_eventModifier = Task(
                # 'event_id': event_id,
        description= """Create the arguments for a Google Calendar event in this format ( If summmary is not specified then take summary as 'N/A', if location is not specified then take location as 'N/A', if start_time is not specified then take start_time as 'N/A', if end_time is not specified then take end_time as 'N/A')
            {    
                'event_summary': event_summary,
                'event_location': event_location,
                'start_time': start_time, ISO8601 Format +5:30 
                'end_time': end_time, ISO8601 Format +5:30
                'state' : state_number
                }
            Choose state number according to this : 1 -> Modify event summary, 2 -> Modify event location, 3 -> Modify event start time, 4 -> Modify event end time
                    12 -> Modify event summary and location, 13 -> Modify event summary and start time, 14 -> Modify event summary and end time
                    23 -> Modify event location and start time, 24 -> Modify event location and end time, 34 -> Modify event start time and end time
                    123 -> Modify event summary, location and start time, 124 -> Modify event summary, location and end time, 134 -> Modify event summary, start time and end time
                    234 -> Modify event location, start time and end time, 1234 -> Modify event summary, location, start time and end time
        for the following text. ONLY PRINT THE DICTIONARY AND NOTHING ELSE"""+ 
                    input_text,
        agent=eventModifier,
        verbose=True,
    )


########## TDLR
    task_eventDeleter = Task(
        description="""Use the delete_event tool and"""+ 
                    """Delete an event in the Google Calendar, for the following event_id"""+ 
                    input_text,
        agent=eventDeleter,
        verbose=True,
    )

    task_eventbusyTime = Task(
        description="""Interpret which day is being talked about,
                    for the following text""" + input_text + 
                    """ ONLY print the dictionary and nothing else in the format:
                    {'date': date} #YYYY/DD/MM format""",
        agent=eventbusyTime,
        verbose=True,
    )

    task_eventSearcher = Task(
        description="""Create the arguments for searching a Google Calendar event in this format ( If summmary is not specified then take summary as 'None', if location is not specified then take location as 'None', if start_time is not specified then take start_time as 'None', if end_time is not specified then take end_time as 'None')
            {    
                'summary': event_summary, # Summary should be ther only if in the input text a keyword is specified
                'location': event_location,
                'start_date': start_date, Print the date in YYYY-MM-DD format
                'end_date': end_date, Print the date in YYY-MM-DD format
                }
        For the following text. ONLY PRINT THE DICTIONARY AND NOTHING ELSE, I ONLY WANT THE DICTIONARY """+ 
                    input_text,
        agent=eventSearcher,
        verbose=True,
    )

    return task_taskAssigner, task_eventCreater, task_eventModifier, task_eventDeleter, task_eventbusyTime, task_eventSearcher

### 
# task_taskAssigner, task_eventCreater, task_eventModifier, task_eventDeleter, task_eventbusyTime, task_eventSearcher = tasks(input = "User Input here")
# from crewai import Crew, Process
# crew_1 = Crew(
#     agents=[taskAssigner],
#     tasks=[task_taskAssigner],
#     verbose=True,
#     process=Process.sequential,
# )

### Argument Creators

def args_tasks(task_eventCreater, task_eventModifier, task_eventDeleter, task_eventbusyTime, task_eventSearcher, result):
    if result == 'eventCreater' or result == 'eventCreator':
        crew_2 = Crew(
            agents=[eventCreater],
            tasks=[task_eventCreater],
            verbose=True,
            process=Process.sequential,
        )
        result2 = crew_2.kickoff()
        print(result2)
            

    elif result == 'eventModifier':
        crew_2 = Crew(
            agents=[eventModifier],
            tasks=[task_eventModifier],
            verbose=True,
            process=Process.sequential,
        )
        result2 = crew_2.kickoff()
        print(result2)
        
#########TDLR
    elif result == 'eventDeleter':
        crew_2 = Crew(
            agents=[eventDeleter],
            tasks=[task_eventDeleter],
            verbose=True,
            process=Process.sequential,
        )
        result2 = crew_2.kickoff()
        print(result2)

    elif result == 'eventbusyTime':
        crew_2 = Crew(
            agents=[eventbusyTime],
            tasks=[task_eventbusyTime],
            verbose=True,
            process=Process.sequential,
        )
        result2 = crew_2.kickoff()
        print(result2)

    elif result == 'eventSearcher':
        crew_2 = Crew(
            agents=[eventSearcher],
            tasks=[task_eventSearcher],
            verbose=True,
            process=Process.sequential,
        )
        result2 = crew_2.kickoff()
        print(result2)

    else:
        print("Something went wrong, please try again")
    
    return result2
    
## CREATOR
###result2 = args_tasks(task_eventCreater, task_eventModifier, task_eventDeleter, task_eventbusyTime, task_eventSearcher, result)

# if result == 'eventCreator':
#     result_dict = eval(result2)
#     print(result_dict)

#     created_event = CalendarTools.create_event(service, result_dict.get('event_summary'), result_dict.get('event_location'), result_dict.get('start_time'), result_dict.get('end_time'), int(result_dict.get('email_reminder_minutes')), int(result_dict.get('popup_reminder_minutes')))
#     eventId = re.sub(r'@.*', '', created_event)
#     print(eventId)
#     event = CalendarTools.list_events(service, event_id=eventId)
#     print(event[0])
#     mu.save_new_db(event = event[0], collection=collection)


## MODIFIER
# if result == 'eventModifier':
#     task_taskAssigner, task_eventCreater, task_eventModifier, task_eventDeleter, task_eventbusyTime, task_eventSearcher = tasks(input = "Modify the 8pm to start at 10pm")
#     result2 = args_tasks(task_eventCreater, task_eventModifier, task_eventDeleter, task_eventbusyTime, task_eventSearcher, result)
#     # Define function to prompt user for confirmation of events
#     def confirm_event(events):
#         print("Found the following events:")
#         for i, event in enumerate(events):
#             print(f"{i + 1}. {event['summary']} - {event['start']['dateTime']} to {event['end']['dateTime']}")

#         while True:
#             choice = input("Enter the number of the correct event (or '0' to cancel): ")
#             if choice == '0':
#                 return None
#             try:
#                 choice = int(choice)
#                 if 1 <= choice <= len(events):
#                     return events[choice - 1]
#                 else:
#                     print("Invalid choice. Please enter a valid number.")
#             except ValueError:
#                 print("Invalid input. Please enter a number.")
    
#     ### TDLR : Extract Current scenario 
#     # Example usage
#     summary = ""
#     start_date = "2024-03-02" #YYYY-MM-DD format
#     end_date = "" # YYYY-MM-DD format
#     location = ""

#     events = mu.list_events_db(collection, summary, start_date, end_date, location)

#     if events:
#         selected_event = confirm_event(events)
#         if selected_event:
#             print("Confirmed event:")
#             print(selected_event)
#     else:
#         print("No events found matching the criteria.")
    
#     ####### ask the user in a natural language way
#     event_id = selected_event.get('id')
#     result_dict = eval(result2)
#     print(result_dict)
#     updated_event = CalendarTools.modify_event(service, event_id ,result_dict.get('event_summary'), result_dict.get('event_location'), result_dict.get('start_time'), result_dict.get('end_time'), int(result_dict.get('state')))
#     mu.update_event_db(collection, updated_event[0]['id'], updated_event[0])
