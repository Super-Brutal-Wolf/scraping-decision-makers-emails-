# $30/ month
import json
from apify_client import ApifyClient
client = ApifyClient("apify_api_J75DE8jFVpEBjZQKCop7fonNrPn5ss1JwhUn")

def linkedin(title, location):
    job_list = []
    run_input = {
        "title": title,
        "location": location,
        "publishedAt": "r86400",
        "rows": 500,
        "proxy": {
            "useApifyProxy": True,
            "apifyProxyGroups": [
            "RESIDENTIAL"
            ],
            "apifyProxyCountry": "US"
        },
    }
    
    run = client.actor("BHzefUZlZRKWxkTck").call(run_input=run_input)
    print(f"find {len(list(client.dataset(run["defaultDatasetId"]).iterate_items()))} jobs from linkedin")
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        individual = {
            "title": item.get('title'),
            "location": item.get('location'),
            "companyName": item.get('companyName'),
            "description": item.get('description'),
            "publisher": "Linkedin"
        }
        job_list.append(individual)
        
    with open('jobs_list_from_Linkedin.json', 'w') as f:
        json.dump(job_list, f, indent=4)
    print(len(job_list))

if __name__ == '__main__':
    title = input("Enter the job title you are looking for: ")
    location = input("Enter the location you are looking for: ")
    linkedin(title, location)
    