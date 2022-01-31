import requests

url = "https://youtube-v31.p.rapidapi.com/videos"

querystring = {"part":"contentDetails,snippet,statistics","id":"7ghhRHRP6t4"}

headers = {
    'x-rapidapi-host': "youtube-v31.p.rapidapi.com",
    'x-rapidapi-key': "f1bd510b4dmsha9e4705c644b59fp1f4043jsn121019a642ec"
    }

response = requests.request("GET", url, headers=headers, params=querystring)

print(response.json())