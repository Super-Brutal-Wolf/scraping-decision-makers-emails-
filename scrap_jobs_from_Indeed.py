

# $20/ month
from apify_client import ApifyClient
import json
client = ApifyClient("apify_api_PtWo3fNasSgeTOM07RJ1gR1HVlhVWk18lMnS")

def indeed(title, location):
    searching_title = title.strip().replace(" ", "+")
    searching_location = location.strip().replace(" ", "+")
    job_list = []
    searching_url = f"https://www.indeed.com/jobs?q={searching_title}&l={searching_location}&fromage=1"
    
    run_input = {
            "count": 500,
            "findContacts": False,
            "outputSchema": "raw",
            "proxy": {
                "useApifyProxy": True,
                "apifyProxyGroups": [
                    "RESIDENTIAL"
                ],
                "apifyProxyCountry": "US"
            },
            "scrapeJobs.scrapeCompany": False,
            "scrapeJobs.searchUrl": searching_url,
            "useBrowser": True
        }
    
    run = client.actor("qA8rz8tR61HdkfTBL").call(run_input=run_input)
    
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        individual = {
            "title": item.get('title'),
            "location": location,
            "companyName": item.get('company'),
            "description": item.get('jobDescription'),
            "publisher": "Indeed"
        }
        job_list.append(individual)
    with open('jobs_list_from_Linkedin.json', 'w') as f:
        json.dump(job_list, f, indent=4)
    print(len(job_list))

if __name__ == '__main__':
    title = input("Enter the job title you are looking for: ")
    location = input("Enter the location you are looking for: ")
    indeed(title, location)