import os
from fastapi import FastAPI, HTTPException
import requests
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

GITHUB_API_URL = "https://api.github.com"

GITHUB_ACCESS_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN")
headers = {"Authorization": f"token {GITHUB_ACCESS_TOKEN}"}

def get_user():
    response = requests.get(f"{GITHUB_API_URL}/user", headers=headers)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch user info")
    return response.json()

def get_repos():
    response = requests.get(f"{GITHUB_API_URL}/user/repos", headers=headers)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch repos")
    return response.json()

def get_repo(repo_name: str):
    # Get username from authenticated info
    user_resp = requests.get(f"{GITHUB_API_URL}/user", headers=headers)
    if user_resp.status_code != 200:
        raise HTTPException(status_code=user_resp.status_code, detail="Failed to fetch user info")
    username = user_resp.json()["login"]
    response = requests.get(f"{GITHUB_API_URL}/repos/{username}/{repo_name}", headers=headers)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch repository info")
    return response.json()

def get_repo_languages(repo_name: str):
    user_resp = requests.get(f"{GITHUB_API_URL}/user", headers=headers)
    if user_resp.status_code != 200:
        raise HTTPException(status_code=user_resp.status_code, detail="Failed to fetch user info")
    username = user_resp.json()["login"]
    response = requests.get(f"{GITHUB_API_URL}/repos/{username}/{repo_name}/languages", headers=headers)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch repository languages")
    return response.json()

def get_followers():
    response = requests.get(f"{GITHUB_API_URL}/user/followers", headers=headers)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch followers")
    return response.json()

def get_following():
    response = requests.get(f"{GITHUB_API_URL}/user/following", headers=headers)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch following")
    return response.json()

def get_starred():
    response = requests.get(f"{GITHUB_API_URL}/user/starred", headers=headers)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch starred repositories")
    return response.json()