from apify_client import ApifyClient
import requests
import time
import json
import csv
import pandas as pd

ROCKET_API_KEY = "1807155k03f33ab8b09dcfc830bf577e0ba020bb"
ROCKET_SEARCH_DECISION_MAKER_URL = "https://api.rocketreach.co/api/v2/search"
ROCKET_SEARCH_DECISION_MAKER_EMAILS_URL = "http://api.rocketreach.co/api/v2/person/lookup"
APIFY_API_KEY = "apify_api_J75DE8jFVpEBjZQKCop7fonNrPn5ss1JwhUn"

client = ApifyClient(APIFY_API_KEY)

def find_decision_maker(job):
    headers = {
        "Api-Key": ROCKET_API_KEY,
        "Content-Type": "application/json"
    }
    body = {
        "start": 1,
        "page_size": 10,
        "query": {
            "company_name": [
                f"{job["companyName"]}"
            ]
        },
            "order_by": "popularity"
    }
    time.sleep(1)
    response = requests.post(url=ROCKET_SEARCH_DECISION_MAKER_URL, headers=headers, json=body)
    if "Retry-After" in response.headers:
        print(f"please wait for {response.headers["Retry-After"]} second")
        time.sleep(2)
        time.sleep(int(response.headers["Retry-After"]))
        response = requests.post(url=ROCKET_SEARCH_DECISION_MAKER_URL, headers=headers, json=body)
        
    response_json = response.json()
    
    if "profiles" not in response_json or response_json["profiles"] == []:
        print(f"decision maker re-found for company: {job['companyName']}")
        job["decision_maker"] = "Not found"
        job["decision_maker_linkedin_url"] = "Not found"
        job["decision_maker_location"] = "Not found"
        job["decision_maker_current_title"] = "Not found"
    else:
        decision_makers_list = response_json['profiles']
        decision_maker = decision_makers_list[0]
        job["decision_maker"] = decision_maker.get("name")
        job["decision_maker_linkedin_url"] = decision_maker.get("linkedin_url")
        job["decision_maker_location"] = decision_maker.get("location")
        job["decision_maker_current_title"] = decision_maker.get("current_title")
        print(f"Decision maker found for company: {job['companyName']}")
        
    if job.get("decision_maker") in [None, "Unknown", "Not found"]:
        job["work_email"] = "Not found"
        job["personal_email"] = "Not found"
        return 
    else:
        params = {
            "name": job["decision_maker"],
            "current_employer": job["companyName"],
            "linkedin_url": job["decision_maker_linkedin_url"],
        }
        
        time.sleep(1)
        response = requests.get(url=ROCKET_SEARCH_DECISION_MAKER_EMAILS_URL, headers=headers, params=params)
        if "Retry-After" in response.headers:
            print(f"please wait for {response.headers["Retry-After"]} second")
            time.sleep(2)
            time.sleep(int(response.headers["Retry-After"]))
            response = requests.get(url=ROCKET_SEARCH_DECISION_MAKER_EMAILS_URL, headers=headers, params=params)
        else:
            response_json = response.json()
            emails = response_json.get("emails", [])
            job["work_email"] = emails[0].get("email") if len(emails) > 0 else "Not found"
            job["personal_email"] = emails[1].get("email") if len(emails) > 1 else "Not found"
            print(f"find email for {job["companyName"]}") 
        return job    
    

def main(title, location, country):
    try:
        with open('job_list.csv', 'r') as file:
            pass
    except FileNotFoundError:
        with open('job_list.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Title', 'Location', 'Company', 'Description', 'Publisher', 'decision_maker', 'decision_maker_linkedin_url', 'decision_maker_location', 'decision_maker_current_title', 'work_email', 'personal_email'])
 
    job_list = []
    searching_title = title.strip().replace(" ", "+")
    searching_location = location.strip().replace(" ", "+")
    
    print("Searching for Linkedin")
    run_input = {
        "title": title,
        "location": location,
        "publishedAt": "r86400",
        "rows": 250,
        "proxy": {
            "useApifyProxy": True,
            "apifyProxyGroups": [
            "RESIDENTIAL"
            ],
            "apifyProxyCountry": "US"
        },
    }
    
    run = client.actor("BHzefUZlZRKWxkTck").call(run_input=run_input)
    print(f"find {len(list(client.dataset(run["defaultDatasetId"]).iterate_items()))} jobs from Linkedin")
    
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        individual = {
            "title": item.get('title'),
            "location": item.get('location'),
            "companyName": item.get('companyName'),
            "description": item.get('description'),
            "publisher": "Linkedin"
        }
        new_individual = find_decision_maker(individual)
        if new_individual != None:
            job_list.append(new_individual)
            new_expend_individual = [
                new_individual["title"],
                new_individual["location"],
                new_individual["companyName"],
                new_individual["description"],
                new_individual["publisher"],
                new_individual["decision_maker"],
                new_individual["decision_maker_linkedin_url"],
                new_individual["decision_maker_location"],
                new_individual["decision_maker_current_title"],
                new_individual["work_email"],
                new_individual["personal_email"]
            ]
    with open('version1.json', 'w') as f:
        json.dump(job_list, f, indent=4)
    
    print("Searching for Indeed")    
    searching_url = f"https://www.indeed.com/jobs?q={searching_title}&l={searching_location}&fromage=1"
    run_input = {
            "count": 250,
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
    print(f"find {len(list(client.dataset(run["defaultDatasetId"]).iterate_items()))} jobs from Indeed")
    
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        individual = {
            "title": item.get('title'),
            "location": location,
            "companyName": item.get('company'),
            "description": item.get('jobDescription'),
            "publisher": "Indeed"
        }
        new_individual = find_decision_maker(individual)
        if new_individual != None:
            job_list.append(new_individual)
            new_expend_individual = [
                new_individual["title"],
                new_individual["location"],
                new_individual["companyName"],
                new_individual["description"],
                new_individual["publisher"],
                new_individual["decision_maker"],
                new_individual["decision_maker_linkedin_url"],
                new_individual["decision_maker_location"],
                new_individual["decision_maker_current_title"],
                new_individual["work_email"],
                new_individual["personal_email"]
            ]
    with open('version2.json', 'w') as f:
        json.dump(job_list, f, indent=4)    

    print("Searching for Glassdoor")
    run_input = {
        "country": country,
        "city": location,
        "engines": "2",
        "last": "1d",
        "max": 250,
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
            "location": item.get('location'),
            "companyName": item.get('company'),
            "description": item.get('description'),
            "publisher": "Glassdoor"
        }
        new_individual = find_decision_maker(individual)
        if new_individual != None:
            job_list.append(new_individual)
            new_expend_individual = [
                new_individual["title"],
                new_individual["location"],
                new_individual["companyName"],
                new_individual["description"],
                new_individual["publisher"],
                new_individual["decision_maker"],
                new_individual["decision_maker_linkedin_url"],
                new_individual["decision_maker_location"],
                new_individual["decision_maker_current_title"],
                new_individual["work_email"],
                new_individual["personal_email"]
            ]
    with open('version3.json', 'w') as f:
        json.dump(job_list, f, indent=4)
    
    print
    searching_url = f"https://www.ziprecruiter.com/jobs-search?search={searching_title}&location={searching_location}&radius=5000&days=1"
    
    run_input = {
        "maxItems": 250,
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
    print(f"find {len(list(client.dataset(run["defaultDatasetId"]).iterate_items()))} jobs from Ziprecruiter")
    
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        individual = {
            "title": item.get('Title'),
            "location": item.get('City'),
            "companyName": item.get('OrgName'),
            "description": item.get('description'),
            "publisher": "ZipRecruiter"
        }
        new_individual = find_decision_maker(individual)
        if new_individual != None:
            job_list.append(new_individual)
            new_expend_individual = [
                new_individual["title"],
                new_individual["location"],
                new_individual["companyName"],
                new_individual["description"],
                new_individual["publisher"],
                new_individual["decision_maker"],
                new_individual["decision_maker_linkedin_url"],
                new_individual["decision_maker_location"],
                new_individual["decision_maker_current_title"],
                new_individual["work_email"],
                new_individual["personal_email"]
            ]
    with open('version4.json', 'w') as f:
        json.dump(job_list, f, indent=4)
    df = pd.DataFrame(job_list)
    df.to_excel('total_jobs_list.xlsx', index=False, sheet_name='finalresult')
    

if __name__ == '__main__':
    title = input("Enter the job title you are looking for: ")
    location = input("Enter the location you are looking for: ")
    country = input("Enter the country you are looking for: ")
    
    main(title, location, country)