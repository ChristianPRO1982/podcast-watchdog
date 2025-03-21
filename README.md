# watch-podcast-download

[![Latest Release](https://img.shields.io/github/release/ChristianPRO1982/podcast-watchdog.svg)](https://github.com/ChristianPRO1982/podcast-watchdog/releases/latest)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/github/license/ChristianPRO1982/podcast-watchdog.svg)](https://github.com/ChristianPRO1982/podcast-watchdog/blob/main/LICENSE)

General watch on AI topics through the podcast medium. This project is used to download audios and store them automatically. In a second step, another project will consume the audios to make transcriptions and finally make a weekly summary of this watch sent by email. It's necessary for me to separate the projects because the computer used for downloading doesn't necessarily have the capacity to make transcriptions. Summaries will be made via the OpenAI API.

Some translations by Deepl.com

[Flowchart](https://github.com/ChristianPRO1982/ai-subject-monitoring-project?tab=readme-ov-file#PW-flowchart)

# System Architecture

## External APIs

* **OpenAI API:** Used for text transcription and summarization.

## Linux Machine Components

* **Crontab:** Automates the execution of the script at scheduled intervals.
* **Podcast Watchdog (PW):** Core Python scripts that handle the entire workflow.
    * *main.py:* The main execution script orchestrating all subprocesses.
    * *utils_parse_rss.py:* Parses RSS feeds and extracts podcast metadata.
    * *utils_podcast.py:* Handles downloading, transcribing, and summarizing podcasts.
* **Transcription API:** A FastAPI-based service that processes transcriptions.
* **Databases:**
    * *SQLite (podcast.db):* Local storage for podcast metadata.
    * *MySQL (ai-subject-monitoring):* Centralized database for storing AI-related podcast insights.

## Workflow

1. **Parse RSS Feeds (utils_parse_rss.py - ParseRSS)**
    * *Extracts podcast episode URLs and metadata.*
    * *Stores initial data in podcast.db.*
    * *Uses ai_rss_feeds.json for reference.*
2. **Download MP3 (utils_podcast.py - Podcasts.download_podcasts)**
    * *Fetches audio files from podcast sources.*
    * *Saves MP3 files to the output folder.*
    * *Updates podcast.db with download status.*
3. **Transcription (utils_podcast.py - Podcasts.transcribe_podcasts)**
    * *Calls the transcription API (FastAPI service).*
    * *Extracts text from MP3 files and saves as .txt.*
    * *Removes processed MP3 files.*
    * *Updates podcast.db.*
4. **Summarization (utils_podcast.py - Podcasts.summarize_podcasts)**
    * *Calls OpenAI API to generate concise summaries.*
    * *Uses ai_rss_prompts.json for guidance.*
    * *Stores summaries in podcast.db.*
5. **Global Database Update**
    * *Aggregates processed data.*
    * *Sends relevant insights to the MySQL database ai-subject-monitoring.*

## Data Storage

* **Input Files:**
    * *ai_rss_feeds.json: Stores podcast RSS feed information.*
    * *ai_rss_prompts.json: Stores predefined prompts for AI summarization.*
* **Output Files:**
    * *XX_podcast.mp3: Raw downloaded podcast files.*
    * *XX_podcast.txt: Transcriptions of processed podcasts.*

## Deployment

* The system runs on a **Linux machine**.
* crontab schedules and automates execution.
* Requires **Python**, **FastAPI**, **SQLite**, and **MySQL**.

# Files format

## .ENV format

```dotenv
DEBUG=4 # 0: off, 1: on, 2: on with debug messages, 3: on with only SQL queries, 4: for pytest
LOG_RETENTION_DAYS=40
LOGS_PATH='./logs/'

RSS_FEEDS='my_file_rss_feeds.json'
FOLDER_PATH='podcasts'
PREFIX='podcast_'

OPENAI_PROMPTS='my_file_rss_prompts.json'
OPENAI_API_KEY='key'
SUMMARY_DAYS_LIMIT=63
```

## json file format for podcasts

```json
[
    {"category": "my_category", "name": "my_name", "rss_feed": "URL"}
]
```

## json file format for OpenAI prompts

```json
{
    "podcasts": [
        {
            "category": "IA",
            "role": "OpenAI role: system, content",
            "prompt": "OpenAI role: user, content"
        },
        ...
    ]
}
```

# launchers

## API

```bash
uvicorn app.main:app --reload --port 9000
```

## app

```bash
PYTHONPATH=$(pwd) python3 src/main.py
```

## Pytest

```bash
PYTHONPATH=$(pwd) pytest
```

or

```bash
rm podcast_pytest.db && PYTHONPATH=$(pwd) pytest
```
