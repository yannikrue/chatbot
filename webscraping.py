import requests
from datetime import datetime

from bs4 import BeautifulSoup

days = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]


def get_weather():
    weather_report = "https://www.meteoschweiz.admin.ch/home.html?tab=report"

    # to get data from website
    file = requests.get(weather_report)

    # import Beautifulsoup for scraping the data
    soup = BeautifulSoup(file.content, "html.parser")
    text = soup.get_text()
    day = datetime.today().weekday()
    hour = datetime.now().hour

    start = text.find("Heute, {}".format(days[day]))
    text = text[start:]

    if hour < 20:
        end = text.find("{}\n".format(days[day + 1]))
    else:
        start = text.find("{}\n".format(days[day + 1]))
        text = text[start:]
        end = text.find("{}\n".format(days[day + 2]))


    report = text[:end]
    return report

def get_news():
    url = "https://www.srf.ch/"
    file = requests.get(url)

    soup = BeautifulSoup(file.content, "html.parser")

    mydivs = soup.find("div", {"class": "collection__teaser-list-branding-wrapper"})
    text= mydivs.findAll(text = True)
    text[:] = (value for value in text if value != '\n')
    news = ""
    for t in text:
        t = t + '\n'
        news += t
    return news