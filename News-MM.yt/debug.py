import requests

url = "https://www.youtube.com/feeds/videos.xml?channel_id=UCKud809KUMIyNhqwuy5JeFw"
response = requests.get(url)
print(f"Status: {response.status_code}")
print(f"First 500 characters of response:")
print(response.text[:500])