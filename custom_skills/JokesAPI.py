import requests
import random
def get_joke(language):
  if language == 'english':
    url = 'https://api.jokes.one/joke/random?category=general'
  elif language == 'hindi':
    url = 'https://api.jokes.one/joke/random?category=general&locale=hi_IN'
  response = requests.get(url)
  joke = response.json()['result']['joke']
  return joke
print(get_joke('english'))
print(get_joke('hindi'))