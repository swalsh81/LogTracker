import discord

from bs4 import BeautifulSoup
from requests_html import HTMLSession
import re

import post

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException


import data

class bot:

    def __init__(self):
        # self.client = discord.Client()
        self.BOT_FLAG = "!grph"

        self.REACT_TO = ""
        self.REACT_WITH = ""
        self.STOP = False
        # await self.getMessages(self.client)
        self.getRaidar(data.eras)

        @self.client.event
        async def on_ready():
            print("The bot is ready!")

        @self.client.event
        async def on_message(message):

            print(message.author.id)
            if message.author == self.client.user:
                return

            content = message.content

            if content.startswith(self.BOT_FLAG):
                content = content[len(self.BOT_FLAG):].strip()

            content = content.split(" ")

            if content[0] == "Hello":
                await self.client.send_message(message.channel, "World")

            if content[0] == "add":
                # self.client.delete_message(message)
                self.getData(await self.client.get_message(message.channel, content[1]))

            if content[0] == "^":
                counter = 0
                async for m in self.client.logs_from(message.channel, limit=2):
                    if counter is 1:
                        self.getData(m)
                    counter += 1

        self.client.run('NTE0MDg5NzI1MDc0NjA0MDU0.DtRgYQ.eLDSpwKVORDTrgnTnxjxbPzBaEM')

    async def getMessages(self, client):
        # startAt = "448325770570629120"
        stopAt = 0 #"449073353790193667"
        clear = False
        async for message in client.logs_from(client.get_channel('311591327663915009'), limit=500):
            if message.id == message.id:
                clear = True

            if message.id == stopAt:
                return

            if clear is False:
                continue

            self.getData(message)

    def getData(self, message):
        jsonMessage = post.Logs()

        if message.author.id == '448676909518290945':
            embeds = message.embeds
            if len(embeds) == 0:
                return
            embed = embeds[0]

            date = embed['title'].split("|")[1].strip()
            boss = ""
            link = ""
            time = ""
            for field in embed['fields'][:-1]:
                boss = field['name'].split("**")[1]
                link = field['value'].split(" ")[0].split("](")[1]
                if(link.count('dps.report') > 0):
                    time = self.parseReport(link)
                else:
                    time = 0
                print("%s %s %s %s" % (date, boss, time, link))
                jsonMessage.addData(boss=boss, time=time, link=link, date=date)

        if message.author.id in['119167866103791621', '172901565810737152']:
            content = message.content
            if content.count("\n---\n") is not 2:
                return
            date = content.split("|")[1].strip()
            logs = content.split('\n---\n')[1].split('\n\n')
            boss = ""
            link = ""
            time = ""
            for l in logs:
                parts = l.split('\n')
                tmp = parts[0].split("**")
                boss = parts[0].split("**")[1]
                for p in parts:
                    link = p.replace("<", "").replace(">","")
                    if link.count('dps.report') > 0:
                        break
                if (link.count('dps.report') > 0):
                    time = self.parseReport(link)
                else:
                    time = 0

                print("%s %s %s %s" % (date, boss, time, link))
                jsonMessage.addData(boss=boss, time=time, link=link, date=date)
        jsonMessage.post()

    def parseReport(self, link):
        session = HTMLSession()
        page = session.get(link)
        pageHTML = page.html.raw_html
        soup = BeautifulSoup(pageHTML, 'html.parser')

        time = ''
        millis = 0
        if soup.find(text=re.compile("Elite Insights")) is not None:
            progressBox = soup.select(".progress")
            lines = progressBox[0].find_next_siblings('p')
            for p in lines:
                txt = p.get_text().strip()
                if txt.startswith("Duration"):
                    time = txt.replace("Duration:", "").replace("Duration", "").strip()
                    time = time.replace("ms", "").replace("s ",":").replace("m ", ":").replace("s", "")

        elif soup.find(text=re.compile("raid_heroes")) is not None:
            lines = soup.select("center .text")
            for l in lines:
                if l.get_text().count("seconds") > 0:
                    time = l.get_text().replace("Success in", "").replace("in ","").replace("In ","").strip()
                    time = time.replace(" minutes ", ":").replace(" seconds", "")
                    break
        else:
            print("Invalid: " + link)

        if time.count(":") == 1:
            time += ":000"
        if time.count(":") == 0:
            return 0
        nums = time.split(":")
        if nums[1].count(".") == 1:
            split = nums[1].split(".")
            nums[1] = split[0]
            nums[2] = int(nums[2]) + int(split[1])
        time = (((int(nums[0]) * 60) + int(nums[1])) * 1000 + (int(nums[2])))/1000

        return time

    def getRaidar(self, eras):

        browser = webdriver.Chrome()

        checked = False

        for era in eras:
            for boss in data.bosses:
                jsonMessage = post.Raidar()
                browser = self.getPage(browser, "https://www.gw2raidar.com/global_stats/%i/area-%i" % (era["id"], boss["id"]))
                # browser.get("https://www.gw2raidar.com/global_stats/%i/area-%i" % (era["id"], boss["id"]))
                #
                # try:
                #     WebDriverWait(browser, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, "label[for='30check']")))
                #     print("Page is ready!")
                # except TimeoutException:
                #     print("Loading took too much time!")

                perc = [30, 50, 60, 70, 80, 90, 99]

                if not checked:
                    browser.find_element_by_css_selector("label[for='30check']").click()
                    browser.find_element_by_css_selector("label[for='60check']").click()
                    browser.find_element_by_css_selector("label[for='70check']").click()
                    browser.find_element_by_css_selector("label[for='80check']").click()
                    checked = True

                for p in perc:
                    try:
                        val = browser.find_element_by_css_selector('div.r-duration-item.r-bg-' + str(p))
                        jsonMessage.addData(boss, era, p, val.text)
                        # a=1
                    except Exception as e:
                        print(e)
                        print("None for %s at %i during %s" % (boss, p, "recent"))

                jsonMessage.post()
                a=1

    def getPage(self, browser, link):
        browser.get(link)

        try:
            WebDriverWait(browser, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, "label[for='30check']")))
            print("Page is ready!")
            return browser
        except TimeoutException:
            print("Loading took too much time!")
            return self.getPage(browser, link)


if __name__== "__main__":
    b = bot()
    print("main")
    # print(pytz.all_timezones)
    # weeklies.parseEvents('EDT')
    # now = datetime.datetime(year=2018, month=8, day=31, tzinfo=pytz.utc)
    # print(now)
    # print(now.astimezone(pytz.timezone('EST')))
    # print(now.astimezone(pytz.timezone('EST5EDT')))

