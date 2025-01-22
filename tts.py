import pyttsx3

def text_to_speech(text):
    engine = pyttsx3.init()
    engine.setProperty('voice', 'zh+f3')
    engine.say(text)
    engine.runAndWait()
text = "你的智能助手已经准备就绪"
text_to_speech(text)