import Speechrecognition
import pyttsx3

recognizer = SpeechRecognition.Recognizer()

while True:

    try:

        with SpeechRecognition.Microphone() as mic:

            recognizer.adjust_for_ambient_noise(mic, duration=0.2)
            audio = recognizer.listen(mic)

            text = recognizer.recognize_google(audio)
            text - text.lower()

            print(f"Recognized{text}")

    except SpeechRecognition.UnknownValueError():
        recognizer = SpeechRecognition.Recognizer()
        continue