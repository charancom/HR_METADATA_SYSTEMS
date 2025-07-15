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



# import os
# os.environ["OPENAI_API_KEY"] = "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"
# os.environ["LLAMA_CLOUD_API_KEY"] = "llx-KZbzjQypInrMrAqm67nyHiHkYZu4atkiNlW4B3nJ67m7rdcV"
#
# import os
# SERVICE_ACCOUNT_FILE = 'C:\\Users\sreec\PycharmProjects\ENTERPRISE_RAG\gen-lang-client-0166514082-32b8ddccac3a.json'
#
# SERVICE_ACCOUNT_FILE = 'C:\\Users\\sreec\\PycharmProjects\\ENTERPRISE_RAG\\gen-lang-client-0166514082-32b8ddccac3a.json'
#
# os.environ["LLAMA_CLOUD_API_KEY"] = "llx-KZbzjQypInrMrAqm67nyHiHkYZu4atkiNlW4B3nJ67m7rdcV"
# # url = "https://b34af4f8-6b2e-4367-bf45-8abc2a9e94f5.us-east4-0.gcp.cloud.qdrant.io:6333"
# # api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.CgGX6wAufVIYcpwwAalFysYIirDBDlxQCst4lVLlo14"
#
# os.environ["OPENAI_API_KEY"] = "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"
# os.environ["token_github"] = "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"
#
# os.environ["OPENAI_API_KEY"] = "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"
# os.environ["token_github"] = "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"
# os.environ["LLAMA_CLOUD_API_KEY"] = "llx-KZbzjQypInrMrAqm67nyHiHkYZu4atkiNlW4B3nJ67m7rdcV"
# os.environ["GROQ_API_KEY"] = "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"
# os.environ["PINECONE_API_KEY"] = "pcsk_VTNGF_A5c535ZGvy2bTgUrZTpJubSoWbH7GfWK2dgEsHske3EPhAYEzbRM2AYjwkQtLN9"
# os.environ["PINECONE_API_KEY_1"]="pcsk_4xVEdF_GemYyHYLKyAWy85BoQ2EUDWyPYEuT8cVhhLp7EeDJh4x21J9qeuoq4LF77uxXzg"
# path_file = "C:\\Users\sreec\Downloads\Data_Scientist_Job_Description.pdf"
