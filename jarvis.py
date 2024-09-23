import speech_recognition as sr
import webbrowser
import os
import requests
import subprocess
from bs4 import BeautifulSoup
import pyttsx3  # Importing the pyttsx3 library
import threading
import time
import psutil
import subprocess

API_KEY = '926d2a8e447684fc33a3e648d9a9c930'  # Replace with your actual API key
CITY = 'Gandhinagar'

# Initialize the text-to-speech engine
engine = pyttsx3.init()
voices = engine.getProperty("voices")
engine.setProperty("voice", voices[0].id)  # Use the first voice in the list
engine.setProperty("rate", 170)
print(psutil.__file__) 
def pgrep(name):
    pids = []
    for proc in psutil.process_iter(attrs=['pid', 'name']):
        if proc.info['name'] == name:
            pids.append(proc.info['pid'])  # Append the PID, not the name
    return pids
# pgrep()
# Create a lock for speaking
speak_lock = threading.Lock()

def speak(text):
    """Speak the text using the local machine's voice."""
    with speak_lock:
        engine.say(text)
        engine.runAndWait()
        print(f"Said: {text}")

def greet():
    """Greet the user."""
    greetings = [
        "Hello! I am Jarvis made by you. How can I assist you today?",
        "Hi there, jarvis here made by you! What can I do for you?",
        "Greetings, my name is jarvis. you made me tonight! How can I help you today?"
    ]
    import random
    speak(random.choice(greetings))

def get_weather(stop_event):
    """Fetch the weather from OpenWeatherMap."""
    print("Fetching weather information...")
    stop_event.clear()  # Clear the stop event
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200:
            weather = f"{data['main']['temp']}°C, {data['weather'][0]['description']}"
            print(f"Weather fetched: {weather}")
            speak(f"The current weather in {CITY} is {weather}.")
        else:
            print("Failed to fetch weather details.")
            speak("Sorry, I couldn't fetch the weather details.")
    except Exception as e:
        if stop_event.is_set():
            print("Weather fetching stopped.")
        else:
            print(f"An error occurred: {e}")

def get_news(stop_event):
    """Fetch news headlines from BBC."""
    print("Fetching news headlines...")
    stop_event.clear()  # Clear the stop event
    try:
        url = 'https://www.bbc.com/news'
        response = requests.get(url)

        if response.status_code != 200:
            print(f"Failed to retrieve news: {response.status_code}")
            speak("Sorry, I couldn't fetch the news.")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        articles = []

        for item in soup.select('[data-testid="card-headline"]'):
            title = item.get_text(strip=True)
            link = item.find_parent('a')['href']
            if link.startswith('/'):
                link = 'https://www.bbc.com' + link
            articles.append((title, link))

        if articles:
            print("News fetched successfully.")
            for title, link in articles[:7]:  # Top 7 headlines
                if stop_event.is_set():
                    print("News fetching stopped.")
                    return
                print(f"Speaking: {title} - Link: {link}")
                speak(title)  # Speak each headline
                time.sleep(2)  # Delay for clarity
            print("Finished speaking news headlines.")  # Indicate end
        else:
            print("No news articles found.")
            speak("Sorry, I couldn't fetch the news.")
    except Exception as e:
        if stop_event.is_set():
            print("News fetching stopped.")
        else:
            print(f"An error occurred: {e}")
            speak("Sorry, I couldn't fetch the news.")

# def get_news(stop_event):
#     """Fetch news headlines from BBC."""
#     print("Fetching news headlines...")
#     stop_event.clear()  # Clear the stop event
#     try:
#         url = 'https://www.bbc.com/news'
#         response = requests.get(url)
#         soup = BeautifulSoup(response.text, 'html.parser')
#         articles = []

#         for item in soup.select('[data-testid="card-headline"]'):
#             title = item.get_text()
#             articles.append(title)  # Store titles

#         if articles:
#             print("News fetched successfully.")
#             for article in articles[:7]:  # Get top 7 headlines
#                 if stop_event.is_set():
#                     print("News fetching stopped.")
#                     return  # Stop if interrupted
#                 speak(article)  # Speak each headline individually
#                 print(f"Speaking: {article}")  # Debug info
#                 time.sleep(1)  # Add a slight delay between headlines
#         else:
#             print("No news articles found.")
#             speak("Sorry, I couldn't fetch the news.")
#     except Exception as e:
#         if stop_event.is_set():
#             print("News fetching stopped.")
#         else:
#             print(f"An error occurred: {e}")

def take_command(stop_event):
    """Listen for voice commands and return the recognized text."""
    recognizer = sr.Recognizer()
    while True:
        with sr.Microphone() as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
            try:
                command = recognizer.recognize_google(audio)
                print(f"You said: {command}")
                if "stop" in command:
                    stop_event.set()  # Set the stop event
                    speak("Stopping the current task.")
                elif command.lower().startswith("jarvis"):  # Check if it starts with "jarvis"
                    command = command.replace("jarvis", "", 1).strip()  # Remove "jarvis" from the start
                    print(f"Command received: {command}")
                    execute_command(command)
                else:
                    print("Command not recognized as a valid request.")
            except sr.UnknownValueError:
                print("Sorry, I didn't catch that.")
            except sr.RequestError:
                print("Could not request results; check your network connection.")




def open_chrome():
    """Check if Chrome is running, and open it if not."""
    chrome_pids = pgrep("chrome.exe")
    
    if chrome_pids:
        speak("Chrome is already running.")
    else:
        speak("Opening Chrome for you.")
        chrome_path = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'
        if os.path.exists(chrome_path):
            subprocess.Popen(chrome_path)
        else:
            speak("I couldn't find Chrome at the specified path.")
            print("Chrome path not found.")

def execute_command(command):
    """Execute the recognized command."""
    print(f"Executing command: {command}")
    if "weather" in command:
        threading.Thread(target=get_weather, args=(stop_event,)).start()
    elif "news" in command:
        threading.Thread(target=get_news, args=(stop_event,)).start()  # Start news in a new thread
    elif "open" in command:
        open_chrome()
    elif "folder" in command:
        folder_name = command.split("open ", 1)[1]
        path = os.path.join(os.path.expanduser('~'), 'Desktop', folder_name)
        if os.path.exists(path):
            speak(f"Opening the folder named {folder_name}.")
            subprocess.Popen(f'explorer "{path}"')
        else:
            speak(f"I couldn't find the folder named {folder_name}.")
    elif "youtube" in command:
        search_query = command.split("search for ", 1)[1] if "search for " in command else ""
        speak(f"Searching YouTube for {search_query}.")
        webbrowser.open(f"https://www.youtube.com/results?search_query={search_query}")
    else:
        print("Command not recognized for execution.")

# def execute_command(command):
#     """Execute the recognized command."""
#     print(f"Executing command: {command}")
#     if  "weather" in command:
#         threading.Thread(target=get_weather, args=(stop_event,)).start()
#     elif "news" in command:  # Generalize the news command
#         threading.Thread(target=get_news, args=(stop_event,)).start()
#     elif "open" in command:
#         open_chrome()

        
#     elif "folder" in command:
#         folder_name = command.split("open ", 1)[1]
#         path = os.path.join(os.path.expanduser('~'), 'Desktop', folder_name)
#         if os.path.exists(path):
#             speak(f"Opening the folder named {folder_name}.")
#             subprocess.Popen(f'explorer "{path}"')
#         else:
#             speak(f"I couldn't find the folder named {folder_name}.")
#     elif "youtube" in command:
#         search_query = command.split("search for ", 1)[1] if "search for " in command else ""
#         speak(f"Searching YouTube for {search_query}.")
#         webbrowser.open(f"https://www.youtube.com/results?search_query={search_query}")
#     else:
#         print("Command not recognized for execution.")

if __name__ == "__main__":
    stop_event = threading.Event()  # Create a stop event
    print("Jarvis is starting...")
    greet()  # Initial greeting
    take_command(stop_event)
