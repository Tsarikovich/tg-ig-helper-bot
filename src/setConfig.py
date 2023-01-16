import os

accounts_json = open("../credentials.json", "r", encoding="utf-8").read()
os.environ['accounts_list'] = accounts_json
os.environ['TOKEN'] = "5329709814:AAE9KbJJ2YdethL-zm5YotVhtV7RQH7_Ygo"
