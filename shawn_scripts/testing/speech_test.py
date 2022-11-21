import pyttsx3
engine = pyttsx3.init()
voices = engine.getProperty('voices')
#good ones are 7 and 38
print(voices[7].id)
engine.setProperty('voice', voices[7].id)
engine.say('Good morning, it is a lovely day to pipette.')
engine.say('Let\'s get this party started.')
engine.runAndWait()
