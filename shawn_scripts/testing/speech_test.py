import pyttsx3
import time
import random
import subprocess


def main():
    welcome()
    goodbye()

def say_message(message):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    nationality = 'uk'
    if nationality == 'French':
        engine.setProperty('voice', voices[38].id)
    else:
        engine.setProperty('voice', voices[7].id)

    engine.say(message)
    engine.runAndWait()

def welcome():
    mytime = time.localtime()
    if mytime.tm_hour < 5:
        tod = 'My stars, you\'re here early. Let\'s get you pumped up.'
        song = '2001.mp3'
    elif mytime.tm_hour < 11:
        operas = [['Puccini', 'puccini.mp3'],
                  ['Verdi', 'verdi.mp3'],
                  ['Mozart','mozart.mp3'],
                  ['Haydn', 'haydn.mp3'],
                  ['Beethoven', 'beethoven.mp3']]
        num = random.randint(0, len(operas)-1)
        opera = operas[num]
        print(opera)
        tod = 'Good morning Johannes, how about some {}?'.format(opera[0])
        song = opera[1]
    elif mytime.tm_hour < 16:
        tod = 'Let\'s do some pipetting!'
        song = 'get_it_started.mp3'
    else:
        tod = 'You\'re here late!'
        song = 'rockabye.mp3'

    general = 'Go take a break, I\'ve got this.'
    say_message(tod)
    say_message(general)
    # music('/data/songs/'+song, protocol)

def goodbye():
    mytime = time.localtime()
    if mytime.tm_hour < 5:
        tod = 'Make this a great day!'
    elif mytime.tm_hour < 11:
        tod = 'Have a great rest of your day!'
    elif mytime.tm_hour < 16:
        tod = 'Almost done for the day!'
    else:
        tod = 'Now go to bed!'

    general = 'That\'s all for me! '
    say_message(general)
    say_message(tod)

# def run_quiet_process(command):
#     subprocess.Popen('{} &'.format(command), shell=True)
#
# def music(song, protocol):
#     print('Speaker')
#     print('Next\t--> CTRL-C')
#     try:
#         if not protocol.is_simulating():
#             run_quiet_process('mpg123 {}'.format(song))
#         else:
#             print('Not playing mp3, simulating')
#     except KeyboardInterrupt:
#         pass
#         print()

if __name__=='__main__':
    main()
