from apify_client import ApifyClient
import json
client = ApifyClient("apify_api_sWo8upg6Me4zM2FY6ui1H4KMr21f0V4nzs3U")

def ziprecruiter(title, location):
    job_list = []
    searching_title = title.strip().replace(' ', '+')
    searching_location = location.strip().replace(' ', '+')
    searching_url = f"https://www.ziprecruiter.com/jobs-search?search={searching_title}&location={searching_location}&radius=5000&days=1"
    
    run_input = {
        "maxItems": 500,
        "proxy": {
            "useApifyProxy": True,
            "apifyProxyGroups": [
            "RESIDENTIAL"
            ],
            "apifyProxyCountry": "US"
        },
        "startUrls": [
            {
            "url": searching_url,
            "method": "GET"
            }
        ],
        "maxConcurrency": 10,
        "minConcurrency": 1,
        "maxRequestRetries": 30
    }
  
    run = client.actor("vQO5g45mnm8jwognj").call(run_input=run_input)
    
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        individual = {
            "title": item.get('Title'),
            "location": item.get('City'),
            "companyName": item.get('OrgName'),
            "description": item.get('description'),
            "publisher": "ZipRecruiter"
        }
        job_list.append(individual)
        
    with open('jobs_list_from_Ziprecruiter.json', 'w') as f:
        json.dump(job_list, f, indent=4)
    print(len(job_list))   

if __name__ == '__main__':
    title = input("Enter the job title you are looking for: ")
    location = input("Enter the location you are looking for: ")
    ziprecruiter(title, location)
    