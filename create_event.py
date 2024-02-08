import os
from langchain_community.llms import Ollama
from langchain.chat_models import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun
from crewai import Agent, Task, Crew, Process

from langchain.agents import Tool
from langchain_experimental.utilities import PythonREPL
python_repl = PythonREPL()
python_tool = Tool(
    name="python_repl",
    description="A Python shell. Use this to execute python commands. Input should be a valid python command. If you want to see the output of a value, you should print it out with `print(...)`.",
    func=python_repl.run,
)

from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langchain_community.utilities import SerpAPIWrapper
wrapper = DuckDuckGoSearchAPIWrapper(region="in-en", time="d", max_results=1)
search_tool = DuckDuckGoSearchRun(wrapper=wrapper)
serp_tool = SerpAPIWrapper(serpapi_api_key= "0f298aeed044ba2259d72fe7805b71af4bb3fc8ac34e2e9e29ddcca47e0c77c7")

os.environ["OPENAI_API_KEY"] = "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"
os.environ["SERPAPI_API_KEY"] = "0f298aeed044ba2259d72fe7805b71af4bb3fc8ac34e2e9e29ddcca47e0c77c7"
llm_gpt = ChatOpenAI(temperature=0.7,model_name="gpt-3.5-turbo",)
ollama_openhermes = Ollama(model="openhermes")

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import datetime

# If modifying these SCOPES, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']

# try:
creds = None
# The file token.pickle stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'crewAI\credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)

service = build('calendar', 'v3', credentials=creds)

# # Call the Calendar API
# now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
# print('Getting the upcoming 10 events')
# events_result = service.events().list(calendarId='primary', timeMin=now,
#                                         maxResults=10, singleEvents=True,
#                                         orderBy='startTime').execute()
# events = events_result.get('items', [])

# if not events:
#     print('No upcoming events found.')
# for event in events:
#     start = event['start'].get('dateTime', event['start'].get('date'))
#     print(start, event['summary'])

Emily = Agent(
    role="Emily",
    goal="""Use https://www.timeanddate.com to determine current date and time.
    """,
    backstory="Emily is an agent who has expertise in data analysis . She\'s been working with the team for over three years now. Her current task is to retrieve current date and time and pass it to John using www.dateandtime.com",
    verbose=True,
    allow_delegation=True,
    llm=llm_gpt,
    tools=[search_tool]
)

task_Emily = Task(
    description="Retrieve current date and time using and pass it to John",
    agent=Emily,
    verbose=True,
)

John = Agent(
    role="John",
    goal="""Interpret text input and create calendar details based on that, details are summary ,start time and end time in ISO 8601 format for Asia/Kolkata.
    If summary is not clear take summary as 'N/A', make sure that that the summary is always in quotes.
    Always give the final answer in this format only: {
            'summary': event_puprose,
            'start': {
                'dateTime': start_time,
                'timeZone': 'Asia/Kolkata',
            },
            'end': {
                'dateTime': end_time,
                'timeZone': 'Asia/Kolkata',
            },
        }""",
    backstory="John is a seasoned agent who has expertise in natural language processing. He\'s been working with the team for over three years now. He knows what the current date time is in Asia/Kolkata using python datetime library. His current task is to interpret text input and create calendar details based on that, details are summary ,start time and end time in ISO 8601 format for Asia/Kolkata.",
    verbose=True,
    allow_delegation=True,
    llm=llm_gpt,
    tools=[search_tool]
)

task_John = Task(
    description="""Take Emily's output and using that, inpterpret the current time first and then summary, start time and end time in ISO 8601 format for Asia/Kolkata. in this format{
            'summary': event_puprose,
            'start': {
                'dateTime': start_time,
                'timeZone': 'Asia/Kolkata',
            },
            'end': {
                'dateTime': end_time,
                'timeZone': 'Asia/Kolkata',
            },
        }"""+ 
                """Tommorow evening from 6 to 9 pm for music session """,
    agent=John,
    verbose=True,
)

crew = Crew(
    agents=[John],
    tasks=[task_John],
    verbose=True,
    process=Process.sequential,
)

# Kickoff the crew tasks
result = crew.kickoff()
# Handle the "result" as needed

# convert result to dict
result_dict = eval(result)
print(result_dict)

event = result_dict
event = service.events().insert(calendarId='primary', body=event).execute()
print(f"Event created: {event.get('htmlLink')}")

# except Exception as e:
#     print(f"An error occurred: {str(e)}")