# AI-Powered Facebook Page Automation with Python

Automatically generate and publish AI-powered educational content and infographic images to a Facebook Page using Python, Google Gemini AI, and the Facebook Graph API.

This project can be configured to publish Facebook Page posts automatically on a daily schedule using Windows Task Scheduler.

## Features

- Generate original content using Google Gemini AI.
- Create educational posts about herbs, plants, spices, and other topics.
- Generate branded infographic images using Python and Pillow.
- Create images in Facebook Feed and Story formats.
- Automatically publish images to a Facebook Page.
- Save publishing history to help prevent duplicate posts.
- Retry temporary AI API errors.
- Schedule multiple daily posts using Windows Task Scheduler.
- Run locally on your own Windows computer.

## 1. How the Automation Works

The project follows this workflow:

```text
Windows Task Scheduler
          |
          v
        post.py
          |
          v
     ai_content.py
          |
          v
      Gemini AI
          |
          v
   Generate Post Content
          |
          v
       render.py
          |
          v
    Create Infographic
          |
          v
    facebook_api.py
          |
          v
    Facebook Graph API
          |
          v
   Publish Facebook Post
          |
          v
   Publish Facebook Story
          |
          v
      Save Post History
```

## 2. Requirements

Before starting, install or prepare:

- Windows 10 or Windows 11.
- Python 3.10 or newer (use a version supported by the installed dependencies).
- Git.
- A Google Gemini API key.
- A Meta Developer account.
- A Facebook Page that you have permission to manage.
- A Facebook app configured for the required Page publishing permissions.
- An internet connection.

## 3. Download the Project

Clone the repository:

```bash
git clone YOUR_REPOSITORY_URL
```

Open the project directory:

```bash
cd YOUR_PROJECT_FOLDER
```

Alternatively, download the repository as a ZIP file and extract it.

## 4. Create a Python Virtual Environment

Create a virtual environment:

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

Upgrade pip:

```bash
python -m pip install --upgrade pip
```

## 5. Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

The project uses libraries such as:

- `google-genai` – Gemini AI integration.
- `Pillow` – Image creation and editing.
- `python-dotenv` – Environment variable configuration.
- `requests` – HTTP requests to the Facebook Graph API.

If the repository does not contain `requirements.txt`, install the packages manually:

```bash
pip install google-genai Pillow python-dotenv requests
```

## 6. Configure Google Gemini API

Gemini generates the educational content used in Facebook posts.

1. Visit [Google AI Studio](https://aistudio.google.com/).
2. Sign in with your Google account.
3. Create or obtain an API key.
4. Keep the API key private.

The key will be added to the project's `.env` file in the next step.

## 7. Configure Facebook Graph API

Facebook publishing is handled through the Meta Graph API.

1. Visit [Meta for Developers](https://developers.facebook.com/).
2. Sign in with your Meta account.
3. Create a Meta application or select an existing one.
4. Configure the products and permissions required for Facebook Page publishing.
5. Obtain an appropriate Page access token.
6. Obtain the Facebook Page ID.
7. Check that the token has the permissions required for the publishing operations used by the project.

Refer to the [Meta Graph API documentation](https://developers.facebook.com/docs/graph-api/) for current requirements.

The exact permissions and token setup depend on your application type and Meta's current policies.

## 8. Configure Environment Variables

Create a file named `.env` in the project's root directory.

Copy the following template:

```env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
GEMINI_MODEL=YOUR_SUPPORTED_GEMINI_MODEL

FACEBOOK_APP_ID=YOUR_FACEBOOK_APP_ID
FACEBOOK_APP_SECRET=YOUR_FACEBOOK_APP_SECRET

FACEBOOK_ACCESS_TOKEN=YOUR_FACEBOOK_PAGE_ACCESS_TOKEN
FACEBOOK_PAGE_ID=YOUR_FACEBOOK_PAGE_ID
```

Replace the placeholder values with your own credentials.

**Important:** Never upload `.env` to GitHub. It contains private API credentials and access tokens.

The repository should include `.env.example` with empty values so other users know which settings they need.

## 9. Understand the Project Files

| File | Purpose |
|---|---|
| `post.py` | Main automation script |
| `ai_content.py` | Generates content using Gemini AI |
| `render.py` | Creates infographic images |
| `facebook_api.py` | Handles Facebook publishing |
| `.env` | Stores private credentials |
| `.env.example` | Example configuration template |
| `requirements.txt` | Python dependencies |
| `state.json` | Stores publishing history |
| `post.log` | Stores execution logs |
| `out/` | Stores generated images |

## 10. Test Content Generation and Image Creation

Before publishing anything, test the project using dry-run mode.

Generate a morning post:

```bash
python post.py --slot morning --dry-run
```

Generate an evening post:

```bash
python post.py --slot evening --dry-run
```

Dry-run mode should generate the content and images without publishing them to Facebook.

Check the generated images in the output directory.

If the images and generated content look correct, continue to the next step.

## 11. Publish a Test Post Manually

Once the dry run works, test actual Facebook publishing.

Morning:

```bash
python post.py --slot morning
```

Evening:

```bash
python post.py --slot evening
```

These commands can publish real content to the configured Facebook Page.

Check the Facebook Page to confirm that the post was published successfully.

The Story publishing operation depends on the Facebook API configuration and permissions.

## 12. Configure Automatic Daily Posting

For Windows users, this project uses Windows Task Scheduler.

You can create scheduled tasks to run the Python script automatically at your preferred times.

For example:

| Schedule | Command |
|---|---|
| 10:00 AM | `python post.py --slot morning` |
| 8:00 PM | `python post.py --slot evening` |

### Create the Morning Task

1. Open Windows Task Scheduler.
2. Select **Create Task**.
3. Enter a task name, such as `Facebook_Morning_Post`.
4. Open the Triggers tab.
5. Create a new trigger.
6. Select Daily.
7. Set your preferred posting time.
8. Open the Actions tab.
9. Select **Start a program**.

Configure the action:

**Program/script:**

```text
PATH_TO_PYTHON/python.exe
```

**Add arguments:**

```text
"PATH_TO_PROJECT/post.py" --slot morning
```

**Start in:**

```text
PATH_TO_PROJECT
```

Replace the example paths with the actual paths on your computer.

### Create the Evening Task

Repeat the same process with another task.

Use:

```text
"PATH_TO_PROJECT/post.py" --slot evening
```

Choose your preferred evening time.

### Configure Task Settings

For both tasks:

- Enable the option to wake the computer to run the task.
- Enable the option to start the task as soon as possible after a missed start, if desired.
- Configure battery settings according to your needs.
- Ensure the Windows account can access the project directory and `.env` file.

**Important:** Windows Task Scheduler can wake supported computers from sleep or hibernation when wake timers are enabled. It cannot normally start a fully powered-off computer.

The computer also needs an internet connection when the script runs.

## 13. Monitor Automatic Publishing

The project log file is:

```text
post.log
```

View the latest log entries:

```powershell
Get-Content ".\post.log" -Tail 50
```

Monitor the log continuously:

```powershell
Get-Content ".\post.log" -Wait
```

Check publishing history:

```powershell
Get-Content ".\state.json"
```

You can also inspect Windows Task Scheduler's Last Run Time and Last Run Result to check whether a scheduled task executed successfully.

A successful task execution does not necessarily mean Facebook publishing succeeded. Always check the application logs and Facebook Page.

## 14. Troubleshooting

### Gemini API Error: 401 Unauthorized

Possible causes:

- Invalid API key.
- Incorrect environment variable.
- API key configuration problem.

Check the `GEMINI_API_KEY` value in `.env`.

### Gemini API Error: 503 Service Unavailable

The Gemini service may be temporarily experiencing high demand.

Possible solutions:

- Wait and retry.
- Check your internet connection.
- Verify the configured model is available.
- Allow the application's retry mechanism to complete.

### Facebook API Error: 401 or 403

Possible causes:

- Invalid or expired access token.
- Missing permissions.
- Incorrect Page ID.
- Incorrect app configuration.

Check your Meta app and Page access token.

### Scheduled Task Does Not Run

Check:

- Task Scheduler trigger settings.
- Python executable path.
- Project working directory.
- Windows permissions.
- Wake timer settings.
- Task Scheduler history.

### No Post Appears on Facebook

Check `post.log` to identify whether the problem occurred during:

1. AI content generation.
2. Image creation.
3. Facebook feed publishing.
4. Facebook Story publishing.

Also check your Facebook Page directly.

## 15. Protect Your Credentials

Before publishing this repository publicly, make sure `.gitignore` contains:

```gitignore
.env
.env.*
!.env.example

venv/
.venv/
__pycache__/
*.pyc

state.json
post.log

out/
```

Do not upload:

- Gemini API keys.
- Facebook App Secrets.
- Facebook Page access tokens.
- Private account information.
- Personal logs containing sensitive information.

If a secret is accidentally published, revoke or rotate it. Deleting the file from the latest GitHub commit does not remove it from Git history.

## 16. Running the Project Every Day

After completing the setup:

1. Keep your API credentials configured in `.env`.
2. Make sure the Python environment and dependencies are installed.
3. Test the morning and evening commands.
4. Configure Windows Task Scheduler.
5. Confirm that both scheduled tasks are enabled.
6. Keep the computer in a supported sleep or powered-on state.
7. Check the logs regularly.
8. Verify successful publishing on your Facebook Page.

Once configured correctly, the system can generate and publish new content automatically according to your chosen schedule.

---

## Project Summary

**Language:** Python

**AI Content Generation:** Google Gemini

**Image Processing:** Pillow

**Publishing Platform:** Facebook Pages

**Publishing API:** Facebook Graph API

**Automation:** Windows Task Scheduler

**Execution:** Local Windows computer

**Output:** Facebook Feed posts and Stories

## Disclaimer

This is an independent automation project intended for educational and development purposes. Users are responsible for configuring their own API credentials, complying with Meta and Google policies, and ensuring that generated content is accurate and appropriate before publishing.