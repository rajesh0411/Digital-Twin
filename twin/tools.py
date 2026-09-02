import base64
import json
import os
import requests
from dotenv import load_dotenv

load_dotenv(override=True)

pushover_user = os.getenv("PUSHOVER_USER")
pushover_token = os.getenv("PUSHOVER_TOKEN")
github_username = os.getenv("GITHUB_USERNAME")

pushover_url = "https://api.pushover.net/1/messages.json"
github_headers = {"Accept": "application/vnd.github+json"}


def push(text):
    requests.post(
        pushover_url,
        data={
            "token": pushover_token,
            "user": pushover_user,
            "message": text,
        },
    )


def record_user_details(email, name="Name not provided", notes="not provided"):
    push(f"Recording interest from {name} with email {email} and notes {notes}")
    return "OK"


def record_unknown_question(question):
    push(f"Recording {question} asked that I couldn't answer")
    return "OK"

def list_github_repos():
    if not github_username:
        return "GITHUB_USERNAME is not set"
    response = requests.get(
        f"https://api.github.com/users/{github_username}/repos",
        headers=github_headers,
        params={"sort": "updated", "per_page": 100, "type": "owner"},
        timeout=20,
    )
    if response.status_code != 200:
        return f"GitHub error {response.status_code}: {response.text}"
    repos = []
    for repo in response.json():
        repos.append(
            {
                "name": repo.get("name"),
                "description": repo.get("description"),
                "language": repo.get("language"),
                "stars": repo.get("stargazers_count"),
                "topics": repo.get("topics") or [],
                "url": repo.get("html_url"),
                "updated_at": repo.get("updated_at"),
            }
        )
    return repos


def get_github_repo(repo):
    if not github_username:
        return "GITHUB_USERNAME is not set"
    repo_name = repo.strip().split("/")[-1]
    response = requests.get(
        f"https://api.github.com/repos/{github_username}/{repo_name}",
        headers=github_headers,
        timeout=20,
    )
    if response.status_code != 200:
        return f"GitHub error {response.status_code}: {response.text}"
    data = response.json()
    readme_response = requests.get(
        f"https://api.github.com/repos/{github_username}/{repo_name}/readme",
        headers=github_headers,
        timeout=20,
    )
    readme = ""
    if readme_response.status_code == 200:
        encoded = readme_response.json().get("content", "")
        readme = base64.b64decode(encoded).decode("utf-8", errors="replace")[:8000]
    return {
        "name": data.get("name"),
        "description": data.get("description"),
        "language": data.get("language"),
        "stars": data.get("stargazers_count"),
        "topics": data.get("topics") or [],
        "url": data.get("html_url"),
        "readme": readme or "No README found",
    }

record_user_details_json = {
    "name": "record_user_details",
    "description": "Use this tool to record that a user is interested in being in touch and provided an email address",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {"type": "string", "description": "The email address of this user"},
            "name": {"type": "string", "description": "The user's name, if they provided it"},
            "notes": {
                "type": "string",
                "description": "Any additional info about the conversation that's worth recording to give context",
            },
        },
        "required": ["email"],
        "additionalProperties": False,
    },
}

record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "Always use this tool to record any question that couldn't be answered as you didn't know the answer",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {"type": "string", "description": "The question that couldn't be answered"},
        },
        "required": ["question"],
        "additionalProperties": False,
    },
}

list_github_repos_json = {
    "name": "list_github_repos",
    "description": "List this person's public GitHub repositories. Use when a visitor asks about their projects, GitHub, or what they have built.",
    "parameters": {
        "type": "object",
        "properties": {},
        "additionalProperties": False,
    },
}

get_github_repo_json = {
    "name": "get_github_repo",
    "description": "Get details and README for one of this person's public GitHub repositories. Use when a visitor asks about a specific repo.",
    "parameters": {
        "type": "object",
        "properties": {
            "repo": {
                "type": "string",
                "description": "The repository name only, for example agents, not a full URL",
            },
        },
        "required": ["repo"],
        "additionalProperties": False,
    },
}

tools = [
    {"type": "function", "function": record_user_details_json},
    {"type": "function", "function": record_unknown_question_json},
    {"type": "function", "function": list_github_repos_json},
    {"type": "function", "function": get_github_repo_json},
]

tool_map = {
    "record_user_details": record_user_details,
    "record_unknown_question": record_unknown_question,
    "list_github_repos": list_github_repos,
    "get_github_repo": get_github_repo,
}


def handle_tool_calls(tool_calls):
    results = []
    for tool_call in tool_calls:
        tool_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        print(f"Tool called: {tool_name}", flush=True)
        tool = tool_map.get(tool_name)
        result = tool(**arguments) if tool else "Unknown tool: " + tool_name
        results.append(
            {"role": "tool", "content": json.dumps(result), "tool_call_id": tool_call.id}
        )
    return results
