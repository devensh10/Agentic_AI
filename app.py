import os
import subprocess
import json
import requests
from pathlib import Path
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import Tool
from langchain.agents import create_react_agent, AgentExecutor
from langchain_google_genai import ChatGoogleGenerativeAI

GITHUB_USERNAME = "ADD_GITHUB_USERNAME"
GITHUB_TOKEN = "ADD_YOUR_GITHUB_TOKEN"
GEMINI_API_KEY = "ADD_GEMINI_API_KEY"

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GEMINI_API_KEY)

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def analyze_folder(folder_path: str) -> str:
    try:
        files = []
        for root, _, filenames in os.walk(folder_path):
            for filename in filenames:
                if not filename.startswith("."):
                    files.append(os.path.relpath(os.path.join(root, filename), folder_path))
        
        if not files:
            return f"The folder '{os.path.basename(folder_path)}' is empty."
        
        return f"The folder '{os.path.basename(folder_path)}' contains {len(files)} files: {files[:10]}{'...' if len(files) > 10 else ''}"
    except Exception as e:
        return f"Error analyzing folder: {str(e)}"

def create_repo(repo_name: str) -> str:
    try:
        data = {
            "name": repo_name,
            "description": f"Auto-generated repository for {repo_name}",
            "private": False,
            "auto_init": False
        }
        response = requests.post("https://api.github.com/user/repos", headers=HEADERS, json=data)
        if response.status_code == 201:
            return f"SUCCESS: Repo '{repo_name}' created successfully"
        elif response.status_code == 422:
            return f"INFO: Repo '{repo_name}' already exists"
        else:
            return f"ERROR: Failed to create repo '{repo_name}': {response.text}"
    except Exception as e:
        return f"ERROR: Exception creating repo: {str(e)}"


def push_to_github(local_path: str, repo_name: str) -> str:
    try:
        
        has_files = False
        for root, _, filenames in os.walk(local_path):
            for filename in filenames:
                if not filename.startswith("."):
                    has_files = True
                    break
            if has_files:
                break
        
        if not has_files:
            return f"WARNING: No files to push in '{repo_name}'"
        
        repo_url = f"https://{GITHUB_TOKEN}@github.com/{GITHUB_USERNAME}/{repo_name}.git"
        
        # Clean up any existing git repo
        git_dir = os.path.join(local_path, '.git')
        if os.path.exists(git_dir):
            import shutil
            shutil.rmtree(git_dir)
        
        # Initialize git repo
        subprocess.run(["git", "init"], cwd=local_path, check=True, capture_output=True)
        subprocess.run(["git", "add", "-A"], cwd=local_path, check=True, capture_output=True)
        
        # Check if there's anything to commit
        result = subprocess.run(["git", "status", "--porcelain"], cwd=local_path, capture_output=True, text=True)
        if not result.stdout.strip():
            return f"WARNING: No changes to commit in '{repo_name}'"
        
        subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=local_path, check=True, capture_output=True)
        subprocess.run(["git", "branch", "-M", "main"], cwd=local_path, check=True, capture_output=True)
        subprocess.run(["git", "remote", "add", "origin", repo_url], cwd=local_path, check=True, capture_output=True)
        subprocess.run(["git", "push", "-u", "origin", "main"], cwd=local_path, check=True, capture_output=True)
        
        return f"SUCCESS: Successfully pushed '{repo_name}' to GitHub"
    except subprocess.CalledProcessError as e:
        return f"ERROR: Git push failed for '{repo_name}': {str(e)}"
    except Exception as e:
        return f"ERROR: Exception pushing to GitHub: {str(e)}"

def process_multiple_folders(parent_path: str) -> str:
    try:
        if not os.path.isdir(parent_path):
            return f"ERROR: Invalid folder path '{parent_path}'"

        folders = [os.path.join(parent_path, f) for f in os.listdir(parent_path)
                   if os.path.isdir(os.path.join(parent_path, f)) and not f.startswith(".")]

        if not folders:
            return f"WARNING: No subfolders found in '{parent_path}'"

        results = []
        results.append(f"Found {len(folders)} subfolders in '{parent_path}'")
        
        for folder in folders:
            folder_name = os.path.basename(folder)
            
            
            analyze_result = analyze_folder(folder)
            results.append(f"ANALYZE {folder_name}: {analyze_result}")
            
            
            if "is empty" in analyze_result:
                results.append(f"SKIP {folder_name}: Empty folder")
                continue
            
            
            create_result = create_repo(folder_name)
            results.append(f"CREATE {folder_name}: {create_result}")
            
            
            push_result = push_to_github(folder, folder_name)
            results.append(f"PUSH {folder_name}: {push_result}")
        
        return "\n".join(results)
    except Exception as e:
        return f"ERROR: Exception processing folders: {str(e)}"

tools = [
    Tool(
        name="analyze_folder",
        func=analyze_folder,
        description="Analyzes a folder's contents and returns file information. Input: folder_path (string)"
    ),
    Tool(
        name="create_repo",
        func=create_repo,
        description="Creates a GitHub repository. Input: repo_name (string)"
    ),
    Tool(
        name="push_to_github",
        func=push_to_github,
        description="Pushes a local folder to GitHub repository. Input: local_path (string), repo_name (string)"
    ),
    Tool(
        name="process_multiple_folders",
        func=process_multiple_folders,
        description="Processes all subfolders in a parent directory. Input: parent_path (string)"
    )
]

prompt_template = PromptTemplate.from_template("""
You are an intelligent GitHub automation agent. You can understand natural language commands and execute them using the available tools.

Available commands you can handle:
- "process folder <path>" - Process a single folder (analyze, create repo, push)
- "process all folders in <path>" - Process all subfolders in a directory
- "analyze <path>" - Just analyze a folder's contents
- "create repo <name>" - Create a GitHub repository
- "push <folder_path> to <repo_name>" - Push a folder to a repository

Always be helpful and execute the user's request using the appropriate tools.

You have access to these tools:
{tools}

Use the following format:
Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Question: {input}
{agent_scratchpad}
""")

agent = create_react_agent(llm, tools, prompt_template)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True, max_iterations=10)

def main():
    print("\n🤖 GitHub Automation Agent")
    print("=" * 50)
    print("Available commands:")
    print("1. 'process folder <path>' - Process a single folder")
    print("2. 'process all folders in <path>' - Process all subfolders")
    print("3. 'analyze <path>' - Just analyze a folder")
    print("4. 'create repo <name>' - Create a GitHub repository")
    print("5. 'push <folder_path> to <repo_name>' - Push folder to existing repo")
    print("6. 'exit' - Exit the program")
    print("=" * 50)
    
    while True:
        try:
            user_input = input("\n💬 Enter your command: ").strip()
            
            if user_input.lower() == 'exit':
                print("👋 Goodbye!")
                break
            
            if not user_input:
                print("⚠️  Please enter a command")
                continue
            
            
            print(f"\n🔄 Processing: {user_input}")
            result = agent_executor.invoke({"input": user_input})
            print(f"\n✅ Result: {result['output']}")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            print("Please try again with a valid command.")

if __name__ == "__main__":
    main()
satvik@Satvik:~/langchain$ 

