import pyttsx3
import time
import random
import subprocess


def main():
    welcome()
    goodbye()

def say_message(message, file):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    nationality = 'uk'
    if nationality == 'French':
        engine.setProperty('voice', voices[38].id)
    else:
        engine.setProperty('voice', voices[7].id)

    engine.say(message)
    engine.save_to_file(message, file)
    engine.runAndWait()

def welcome():
    tod = 'My stars, you\'re here early. Let\'s get you pumped up.'
    say_message(tod, 'welcome_morning.mp3')
    operas = [['Puccini', 'puccini.mp3'],
              ['Verdi', 'verdi.mp3'],
              ['Mozart','mozart.mp3'],
              ['Haydn', 'haydn.mp3'],
              ['Beethoven', 'beethoven.mp3']]
    for opera in operas:
        tod = 'Good morning Johannes, how about some {}?'.format(opera[0])
        say_message(tod, 'welcome_{}.mp3'.format(opera[0]))
    tod = 'Let\'s do some pipetting!'
    say_message(tod, 'welcome_midday.mp3')
    tod = 'You\'re here late!'
    say_message(tod, 'welcome_late.mp3')
    general = 'Go take a break, I\'ve got this.'
    say_message(general, 'welcome_general.mp3')

def goodbye():

    tod = 'Make this a great day!'
    say_message(tod, 'goodbye_morning.mp3')
    tod = 'Have a great rest of your day!'
    say_message(tod, 'goodbye_midmorning.mp3')
    tod = 'Almost done for the day!'
    say_message(tod, 'goodbye_midday.mp3')
    tod = 'Now go to bed!'
    say_message(tod, 'goodbye_late.mp3')
    general = 'That\'s all for me! '
    say_message(general, 'goodbye_general.mp3')

if __name__=='__main__':
    main()
