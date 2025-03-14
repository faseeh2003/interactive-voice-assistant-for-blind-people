import pygame
import time
import speech_recognition as sr
import pyttsx3
import datetime
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import pytz
from transformers import pipeline

# Initialize pygame mixer
pygame.mixer.init()

# Initialize the recognizer and text-to-speech engine
recognizer = sr.Recognizer()
engine = pyttsx3.init()

# Load a pre-trained question-answering model from Hugging Face
qa_pipeline = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")

# Function to read jokes from a text file
def load_jokes(file_path):
    with open(file_path, "r") as file:
        jokes = file.read().splitlines()
    return jokes

# Function to read context from a text file
def load_context(file_path):
    with open(file_path, "r") as file:
        context = file.read()
    return context

# Load jokes and context from text files
jokes = load_jokes("jokes.txt")
context = load_context("context.txt")

# Global variable to keep track of the current joke index
current_joke_index = 0

# Function to convert text to speech
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Function to listen to the user's voice and convert it to text
def listen():
    with sr.Microphone() as source:
        print("Listening...")
        try:
            audio = recognizer.listen(source, timeout=5)  # Listen for 5 seconds
            print("Recognizing...")
            query = recognizer.recognize_google(audio, language="en-US")
            print(f"User said: {query}")
            return query
        except sr.WaitTimeoutError:
            speak("Sorry, I did not hear anything. Please try again.")
            return None
        except sr.UnknownValueError:
            speak("Sorry, I did not understand that.")
            return None
        except sr.RequestError:
            speak("Sorry, my speech service is down.")
            return None
        except Exception as e:
            print(f"Error: {e}")
            speak("Sorry, something went wrong.")
            return None

# Function to get the current time
def get_time():
    now = datetime.datetime.now()
    return now.strftime("%I:%M %p")

# Function to get the current date
def get_date():
    now = datetime.datetime.now()
    return now.strftime("%A, %B %d, %Y")

# Function to get the user's location (offline, requires manual input)
def get_location():
    return "mulavoor, ernakulam, kerala"

# Function to get the current weather (offline, requires manual input)
def get_weather():
    return "The weather is sunny with a temperature of 25°C."

# Function to get the current timezone
def get_timezone():
    try:
        location = get_location()
        geolocator = Nominatim(user_agent="voice_assistant")
        location_data = geolocator.geocode(location)
        tf = TimezoneFinder()
        timezone = tf.timezone_at(lat=location_data.latitude, lng=location_data.longitude)
        return timezone
    except Exception as e:
        print(f"Error fetching timezone: {e}")
        return "unknown timezone"

# Function to get an answer from the model
def get_answer(question):
    try:
        result = qa_pipeline(question=question, context=context)
        answer = result['answer']
        return answer
    except Exception as e:
        print(f"Error: {e}")
        return "Sorry, I couldn't process your request."

# Function to tell a joke
def tell_joke():
    global current_joke_index
    if current_joke_index < len(jokes):
        joke = jokes[current_joke_index]
        current_joke_index += 1  # Move to the next joke
        return joke
    else:
        return "I'm out of jokes for now. Ask me again later!"

# Function to play music
def play_music():
    try:
        music_file = "sos.wav"  # Replace with the actual file name
        print(f"Loading music file: {music_file}")
        pygame.mixer.music.load(music_file)
        print("Playing music...")
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            stop_query = listen()
            if stop_query and ("stop music" in stop_query.lower() or "stop song" in stop_query.lower()):
                pygame.mixer.music.stop()
                print("Music stopped by user.")
                return "Music stopped."
            time.sleep(1)

        print("Music finished playing.")
        return "Playing music..."
    except Exception as e:
        print(f"Error playing music: {e}")
        return "Sorry, I couldn't play the music."

# Function to stop music
def stop_music():
    try:
        pygame.mixer.music.stop()
        return "Music stopped."
    except Exception as e:
        print(f"Error stopping music: {e}")
        return "Sorry, I couldn't stop the music."

# Function to handle commands
def handle_command(query):
    query = query.lower()
    if "time" in query:
        speak(f"The current time is {get_time()}.")
    elif "date" in query:
        speak(f"Today's date is {get_date()}.")
    elif "location" in query:
        speak(f"You are currently in {get_location()}.")
    elif "weather" in query:
        speak(get_weather())
    elif "timezone" in query:
        speak(f"Your current timezone is {get_timezone()}.")
    elif "joke" in query or "tell me a joke" in query:
        speak(tell_joke())
    elif "play music" in query or "play song" in query:
        speak(play_music())
    elif "stop music" in query or "stop song" in query:
        speak(stop_music())
    elif "exit" in query or "quit" in query:
        speak("Goodbye!")
        return False
    else:
        speak("Let me think about that...")
        answer = get_answer(query)
        speak(answer)
    return True

# Main function to handle the assistant
def main():
    speak("Hello! I am your voice assistant. How can I help you today?")
    while True:
        query = listen()
        if query:
            if not handle_command(query):
                break

if __name__ == "__main__":
    main()