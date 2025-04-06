import asyncio
import os
import requests
import base64
from dataclasses import dataclass
from typing import Any
from pydantic_ai import Agent, ModelRetry, RunContext

import os
@dataclass
class Deps:
    github_token: str | None
    owner: str | None
    repo: str | None
    branch: str | None


github_agent = Agent(
    'openai:gpt-3.5-turbo',
    system_prompt=(
        'Summarise the code',
        'Get me the Tech stack used in the projects'
    ),
    deps_type=Deps,
    retries=2
)


@github_agent.tool
async def get_repo_content(ctx: RunContext[Deps]) -> str:
    if ctx.deps.github_token is None:
        return "Please define the github_token of your GitHub account."
    if ctx.deps.owner is None:
        return "Please define the name of the owner of the repo."
    if ctx.deps.repo is None:
        return "Please define the repo name."
    if ctx.deps.branch is None:
        return "Please define the branch of the repo."

    headers = {'Authorization': f'Bearer {ctx.deps.github_token}'} if ctx.deps.github_token else {}
    git_tree_url = f'https://api.github.com/repos/{ctx.deps.owner}/{ctx.deps.repo}/git/trees/{ctx.deps.branch}?recursive=1'
    response = requests.get(git_tree_url, headers=headers)
    print(response.json())

    try:
        tree_data = response.json()
        for item in tree_data.get('tree', []):
            if item.get('type') == 'blob' and item.get('path', '').endswith('.py'):
                file_url = item['url']
                file_response = requests.get(file_url, headers=headers)
                file_data = file_response.json()
                file_content = base64.b64decode(file_data.get('content', '')).decode('utf-8')
                if file_content:
                    print(f'Analyzing {item["path"]}....')
                    return file_content
                else:
                    raise ModelRetry("Couldn't find the location")
    except KeyError as e:
        print(f"KeyError: {e} - Check the API response structure")


async def main():
    deps = Deps(
        owner='sahasourav17',
        repo='ResuMate',
        branch='main',
        github_token=os.getenv("token_github")
    )
    result = await github_agent.run(
        'Summarise me the repository code..',
        deps=deps,
    )
    print(result.data)


if __name__ == "__main__":
    asyncio.run(main())

