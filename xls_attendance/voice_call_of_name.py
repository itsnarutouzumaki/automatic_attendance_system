import pyttsx3
def call_name(registration_numbers):
    engine = pyttsx3.init()
    registration_numbers = sorted(registration_numbers, key=lambda x: x.lower())
    engine.say("Ladies and GentleMen, Attendance has Been marked for")
    engine.runAndWait()

    for number in registration_numbers:
        engine.say(number)
        engine.runAndWait()

    engine.say("thank you so much")
    engine.runAndWait()

