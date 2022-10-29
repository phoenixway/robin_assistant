from nltk import word_tokenize
from nltk.corpus import stopwords
import re, os, sys, datetime

class AICore:
    def parse(self, text):
        answer = f"Default answer on '{text}'"
        stop=set(stopwords.words('english'))
        data=word_tokenize(text)
        data=[w for w in data if w not in stop]
        try:
            for token in data:
                if token in ['wake','wakemeup','alarm','alert','alarmme']:
                    m = re.search(r'in|after\s+(?P<minutes>\d+)\s*(minutes|min|m)', text) 
                    if m:
                        minutes = int(m.group('minutes'))
                        answer = f"You will be alarmed by {minutes} minutes."
                        # dt = datetime.datetime.now() + datetime.timedelta(minutes=minutes)
                        # target_dt = dt.strftime(f"%H:%M")
                        os.system(f"gnome-terminal -- /home/roman/scripts/tmr.sh {minutes}m")
                    else:
                        answer = "Soon will be implemented!"
                elif token in ['exit', 'bye', 'quit', 'goodbye']:
                    quit()
                    sys.exit(0)
        except:
            answer = "Error happened!"
        return answer