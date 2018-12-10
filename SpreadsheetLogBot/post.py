import requests
import json

class Message:

    def __init__(self, type):
        self.data = None
        self.type = type

    def post(self):

        if len(self.data) == 0:
            print("No Data")
            return

        params = {
            'type': self.type,
            'data':json.dumps(self.data)
        }
        print("next is post")
        # headers = {
        #     'Authorization': "Bearer 321299187451-t7t1rjpn2kqve12nfm6i0uhkogcb485p.apps.googleusercontent.com",
        # }
        r = requests.post("https://script.google.com/macros/s/AKfycbxqRCbI0jlZUwm1-P5KHFACJxFL5yn-Oy-oJtT_Scupk89v9FjG/exec", data=params)
        print(r.status_code, r.reason)


class Logs(Message):
    def __init__(self):
        Message.__init__(self, 'logs')
        self.data = []

    def addData(self, boss, date, time, link):
        self.data.append({
            'boss':boss,
            'date':date,
            'time':time,
            'link':link
        })

class Raidar(Message):
    def __init__(self):
        Message.__init__(self, 'raidar')
        self.data = {}

    def addData(self, boss, era, percentile, time):
        bn = boss["boss"]
        if bn not in self.data:
            self.data[bn] = {}
            self.data[bn]["name"] = bn

        en = era["name"]
        if en not in self.data[bn]:
            self.data[bn][en] = {}
            self.data[bn][en]["start-date"] = era['start-date']
        if percentile not in self.data[bn][en]:
            self.data[bn][en][percentile] = time

        print("%s - %s - %s - %s" %(boss, era, percentile, time))


if __name__ == "__main__":
    None