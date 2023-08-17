import requests

class Requests():

    def __init__(self, key):
        self.key = key
        self.headers = {
            "Authorization" : self.key
        }
    
    def get_account(self, uuid):

        url = "https://api.henrikdev.xyz/valorant/v1/by-puuid/account/" + uuid
        response = requests.get(url, headers=self.headers) 
        return response.json()

    def getLifeTimeMatches(self, uuid):

        url = "https://api.henrikdev.xyz/valorant/v1/by-puuid/lifetime/matches/" + "eu" + "/" + uuid + "?size=1"
        response = requests.get(url, headers=self.headers) 
        return response.json()

    def getMatches(self, uuid):

        url = "https://api.henrikdev.xyz/valorant/v3/by-puuid/matches/" + "eu" + "/" + uuid
        response = requests.get(url, headers=self.headers) 
        return response.json()

    def getMMR(self, uuid):

        url = "https://api.henrikdev.xyz/valorant/v1/by-puuid/mmr/" + "eu" + "/" + uuid
        response = requests.get(url, headers=self.headers) 
        return response.json()