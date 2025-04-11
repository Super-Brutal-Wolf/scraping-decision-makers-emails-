from apify_client import ApifyClient
import json
client = ApifyClient("apify_api_sWo8upg6Me4zM2FY6ui1H4KMr21f0V4nzs3U")

def glassdoor(title, location, country):
    job_list = []
    
    print("Searching for Glassdoor")
    run_input = {
        "country": country,
        "city": location,
        "engines": "1",
        "last": "1d",
        "distance": "50",
        "delay": 2,
        "max": 20,
        "proxy": {
            "useApifyProxy": True,
            "apifyProxyGroups": [
                "RESIDENTIAL"
            ],
            "apifyProxyCountry": "US"
        },
        "title": title
    }
    
    run = client.actor("PskQAJMqsgeJHXSDz").call(run_input=run_input)
    print(f"find {len(list(client.dataset(run["defaultDatasetId"]).iterate_items()))} jobs from Glassdoor")
    
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        individual = {
            "title": item.get('title'),
            "description": item.get('description'),
            "companyName": item.get('company'),
            "companyUrl": item.get('company_url'),
            "jobUrl": item.get('job_url'),
            "location": item.get('location'),
            "publisher": "Glassdoor",
        }
        job_list.append(individual)
        
    with open('jobs_list_from_Glassdoor.json', 'w') as f:
        json.dump(job_list, f, indent=4)
    print(len(job_list))

if __name__ == '__main__':
    title = input("Enter the job title you are looking for: ")
    location = input("Enter the location you are looking for: ")
    country = input("Enter the country you are looking for: ")
    glassdoor(title, location, country)