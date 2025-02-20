# watch-podcast-download
General watch on AI topics through the podcast medium. This project is used to download audios and store them automatically. In a second step, another project will consume the audios to make transcriptions and finally make a weekly summary of this watch sent by email. It's necessary for me to separate the projects because the computer used for downloading doesn't necessarily have the capacity to make transcriptions. Summaries will be made via the OpenAI API.

Some translations by Deepl.com

## .ENV format

```dotenv
DEBUG=4 # 0: off, 1: on, 2: on with debug messages, 3: on with only SQL queries, 4: for pytest
LOG_RETENTION_DAYS=30
LOGS_PATH='./logs/'

RSS_FEEDS='my_file_rss_feeds.json'
FOLDER_PATH='podcasts'
PREFIX='podcast_'

OPENAI_PROMPTS='my_file_rss_prompts.json'
OPENAI_API_KEY='key'
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

## launchers

### API

```bash
uvicorn app.main:app --reload --port 9000
```

### app

```bash
PYTHONPATH=$(pwd) python3 src/main.py
```

### Pytest

```bash
PYTHONPATH=$(pwd) pytest
```

or

```bash
rm podcast_pytest.db && PYTHONPATH=$(pwd) pytest
```