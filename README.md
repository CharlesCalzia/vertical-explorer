# Exploration Researcher

An automated research tool that generates vertical analyses using AI, publishes them to Notion and generates a PDF report.

## Overview

Automates the process of generating research reports on various industry verticals using Perplexity's API. The reports are structured according to a customizable template and can be automatically published to a Notion database for easy access and sharing.

## Features

- Generate research reports on multiple industry verticals
- Publish reports directly to Notion
- Export all reports as a single PDF document
- Customizable research template
- Configurable list of industry verticals

## Requirements

- Python 3.7+
- Perplexity API key
- Notion API key and database ID

## Installation

1. Clone this repository
2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Configuration

### Environment Variables

Create a `.env` file in the root directory with the following variables:

```
PERPLEXITY_API_KEY=your_perplexity_api_key
NOTION_SECRET=your_notion_api_key
NOTION_DATABASE_ID=your_notion_database_id
```

### How to Get Your API Keys

#### Perplexity API Key
1. Create an account at [Perplexity AI](https://www.perplexity.ai/)
2. Navigate to your account settings
3. Go to the API section and generate a new API key

#### Notion API Key and Database ID
1. Go to [Notion Developers](https://www.notion.so/my-integrations)
2. Create a new integration
3. Give it a name related to your research project
4. Set the capabilities required (Read & Write content, Insert content)
5. Copy the "Internal Integration Token" - this is your `NOTION_SECRET`
6. Create a database in Notion where you want to store your research
7. Share the database with your integration (click "Share" in the top right of your database, then add your integration)
8. Get the database ID from the URL: `https://www.notion.so/workspace/[database_id]?v=...`
   - The database ID is the part of the URL between the last `/` and the `?`
   - It's a 32-character string (with hyphens removed)

### Customizing Research Topics

Edit the `config.json` file to:
- Change the AI model used
- Modify the template path
- Add or remove industry verticals to research

### Research Template

The `template.md` file defines the structure of your research reports. Modify this file to change the sections and format of your generated reports.

## Usage

Run the main script to generate research for all configured verticals:

```
python research_automation.py
```

This will:
1. Generate research for each vertical in `config.json`
2. Save each report as a markdown file in the `verticals` directory
3. Publish each report to your Notion database
4. Create a combined PDF report of all research

## Output

- Individual markdown files for each vertical in the `verticals` directory
- A combined PDF report in the `verticals` directory (named `research_report.pdf` by default)
- Research pages in your Notion database

### Example Output

An example of the generated PDF report can be found in the repository as [research_report.pdf](research_report.pdf).

## License

[MIT License](LICENSE) 