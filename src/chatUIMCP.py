import streamlit as st
import requests
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

from github_mcp_server import *

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

st.title("Enhanced GitHub Chatbot with Gemini LLM")

github_token = st.text_input("Enter your GitHub Token", type="password")

if github_token:
    os.environ["GITHUB_ACCESS_TOKEN"] = github_token

st.header("Direct MCP Server Queries")
if github_token:
    if st.button("Get GitHub User Info"):
        try:
            user_info = get_user()
            st.write(user_info)
        except Exception as e:
            st.error(f"Error: {e}")

    repo_name_input = st.text_input("Enter Repository Name to get languages")
    if repo_name_input and st.button("Get Repo Languages"):
        try:
            languages = get_repo_languages(repo_name_input)
            st.write(languages)
        except Exception as e:
            st.error(f"Error: {e}")

def get_most_starred_repo():
    try:
        repos = get_repos()
        if isinstance(repos, list) and repos:
            most_starred = max(repos, key=lambda repo: repo.get("stargazers_count", 0))
            return most_starred
        return {"info": "No repositories found."}
    except Exception as e:
        return {"error": str(e)}

st.header("Chat with Gemini LLM Using MCP Server Functions")
query = st.text_input("Enter your GitHub query")

if query and github_token and st.button("Ask Gemini LLM"):
    # Interpret the query to decide which function to call
    def interpret_query(query):
        prompt = f"""
You are an assistant that converts user queries into function calls to query GitHub using available functions.
The available functions are:
- get_user: returns user info.
- get_repos: returns list of repositories.
- get_repo: returns repository details. Parameter: "repo_name"
- get_repo_languages: returns languages of a repository. Parameter: "repo_name"
- get_followers: returns list of followers.
- get_following: returns list of users the account is following.
- get_starred: returns list of starred repositories.
- get_most_starred: returns the repository owned by the user with the highest star count.

Given the user query below, output a JSON object with keys "function" and "params" that represent the function to call and its parameters.
User query: "{query}"
Output example: {{"function": "get_user", "params": {{}}}}
If no function matches, output: {{"function": null, "params": {{}}}}
"""
        model = genai.GenerativeModel("gemini-1.5-flash")
        result = model.generate_content(prompt)
        try:
            function_call = json.loads(result.text.strip())
        except Exception as e:
            function_call = {"function": None, "params": {}}
        return function_call

    function_call = interpret_query(query)
    st.write("Interpreted Function Call:", function_call)
    
    # Map the interpreted function call to an actual function
    func = function_call.get("function")
    params = function_call.get("params", {})
    mcp_response = None

    if func == "get_user":
        mcp_response = get_user()
    elif func == "get_repos":
        mcp_response = get_repos()
    elif func == "get_repo":
        repo_name_param = params.get("repo_name")
        if repo_name_param:
            mcp_response = get_repo(repo_name_param)
        else:
            mcp_response = {"error": "repo_name parameter missing"}
    elif func == "get_repo_languages":
        repo_name_param = params.get("repo_name")
        if repo_name_param:
            mcp_response = get_repo_languages(repo_name_param)
        else:
            mcp_response = {"error": "repo_name parameter missing"}
    elif func == "get_followers":
        mcp_response = get_followers()
    elif func == "get_following":
        mcp_response = get_following()
    elif func == "get_starred":
        mcp_response = get_starred()
    elif func == "get_most_starred":
        mcp_response = get_most_starred_repo()
    else:
        mcp_response = {"info": "No valid function determined from query."}
    
    st.write("MCP Function Response:", mcp_response)
    
    # Generate a final answer using Gemini LLM by combining the original query and the MCP response
    final_prompt = f"""
You are an assistant that uses GitHub API results to answer user queries about their account.
User query: "{query}"
Interpreted function call: {json.dumps(function_call)}
Function result: {json.dumps(mcp_response)}
Provide a clear, concise, and friendly answer to the user based on the above information.
"""
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        final_result = model.generate_content(final_prompt)
        final_answer = final_result.text
    except Exception as e:
        final_answer = f"Error generating final answer: {e}"
    
    st.write("Final Answer:", final_answer)