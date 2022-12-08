import pyttsx3
import time
import random
import subprocess


def main():
    say_message('speaking is hard')

def say_message(message):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    nationality = 'uk'
    if nationality == 'French':
        engine.setProperty('voice', voices[38].id)
    else:
        engine.setProperty('voice', voices[23].id)

    engine.say(message)
    engine.runAndWait()

if __name__=='__main__':
    main()
