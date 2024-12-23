import requests
import json
import threading

def load_credentials():
    credentials_path = "creds.json"

    with open(credentials_path, "r") as creds_file:
        credentials = json.load(creds_file)

    return credentials

def search_recipes(creds, offset, results, index):
    api_key = creds["api_key"]
    url = creds["url"]

    params = {
        "apiKey": api_key,
        "offset": offset
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        if data["results"]:
            results[index] = data["results"][0]  # Store the first recipe at the given index
        else:
            results[index] = "No recipes found!"
    else:
        results[index] = f"Error: {response.status_code}, {response.text}"

def main():
    print("Hello, World!")
    creds = load_credentials()

    recipes = [None] *100
    threads = []

    for i in range(59):
       thread = threading.Thread(target=search_recipes, args=(creds, i, recipes, i))
       threads.append(thread)
       thread.start()

    for thread in threads:
        thread.join()


    print(recipes[45])
if __name__ == "__main__":
    main()