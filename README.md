# Agentic GitHub Repo Creator 🚀

![Agentic AI](https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExYm9vY2E2eWZhYzJ6YmxubzRzYTZ4MGY0ZHFtODg4Z2NzM2ZmOGI1MyZjdD1n/l3q2K5jinAlChoCLS/giphy.gif)

> ⚙️ Build GitHub repositories automatically from folders using LangChain Agents + Gemini + GitHub API.

---

## 🔮 Features

- 📂 Automatically analyze folder structure
- 🤖 Use Google Gemini 1.5 Flash for reasoning
- 🧠 Generate metadata (description, language, topics)
- 📝 Auto-create `README.md`
- 🐙 Create GitHub repo and push code
- 🗣️ Prompt-based CLI tool

---

## 📦 Requirements

- Python 3.9+
- Git installed
- Access to:
  - [Google Gemini API Key](https://aistudio.google.com/app/apikey)
  - [GitHub Personal Access Token](https://github.com/settings/tokens)

Install dependencies:
```bash
pip install -r requirements.txt
```

---

## 🚀 Usage

1. 🔑 Replace your API keys in `app.py`:
```python
GITHUB_USERNAME = "your_github_username"
GITHUB_TOKEN = "your_github_token"
GEMINI_API_KEY = "your_gemini_api_key"
```

2. 🔁 Run the script:
```bash
python app.py
```

3. 💬 Enter the folder path when prompted:
```
📂 Enter parent folder path: /home/user/myprojects
```

4. 🔄 The tool will:
   - Analyze each subfolder
   - Generate repo metadata
   - Create GitHub repo
   - Push code

---

## 📁 Output

- New GitHub repository for each folder
- Auto-generated `README.md`
- Intelligent tag and language detection

---

## 🧠 Credits

Built using:
- [LangChain](https://www.langchain.com/)
- [Google Generative AI (Gemini)](https://ai.google.dev/)
- [GitHub REST API](https://docs.github.com/en/rest)

Special thanks to **Mr. Vimal Daga** for mentorship and open-source inspiration 🙏

---

## 📜 License

MIT License. Use freely. Contribute back. 🌍

---

## 📸 Screenshot

![Terminal Animation](https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExYjE1cWRzbmprMHdwb2k5bnoyZDFva2I2M3dxZ25pc3dmeG9jYnVvZiZjdD1n/3o6ZsZKn2vJPKUPGoA/giphy.gif)

---


