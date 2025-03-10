import os
import json
import time
import requests
from dotenv import load_dotenv
from notion_client import Client
from notion_utils import add_content_to_notion
from report_creator import create_report

# Load environment variables
load_dotenv()

# Initialize clients and config
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
NOTION_SECRET = os.getenv("NOTION_SECRET")


def load_config():
    """Load configuration from JSON file"""
    with open("config.json", "r", encoding="utf-8") as f:
        return json.load(f)


def read_template(template_path):
    """Read the template file"""
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()


def generate_research(vertical, template, model, verticals_path="verticals"):
    """Generate research using Perplexity API and save to file"""
    # Create verticals directory if it doesn't exist
    os.makedirs(verticals_path, exist_ok=True)

    # Check if we already have this research and if so, return it
    file_path = f"{verticals_path}/{vertical.lower().replace(' ', '_')}.md"
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = (
        f"Conduct a comprehensive and nuanced analysis of the {vertical} sector. "
        "Structure your response exactly according to this template, replacing each section with detailed analysis:\n\n"
        f"{template}\n\n"
        "Follow these requirements:\n\n"
        "1. Provide specific, quantifiable insights and avoid generic observations\n"
        "2. Include concrete examples, market sizes, and growth rates where relevant\n"
        "3. Focus on emerging technologies and innovations that are not yet mainstream\n"
        "4. Identify non-obvious market opportunities and unconventional business models\n"
        "5. Analyze unexpected cross-industry convergences and their implications\n"
        "6. Project detailed scenarios for 2025-2035, including specific technological milestones\n"
        "7. For the 'Further Reading' section, include 5-7 actual URLs to relevant industry reports, "
        "research papers, or authoritative sources\n"
        "8. For the 'Further Topics' section, include 10 topics that are not yet mainstream but are likely to be important in the next decade\n\n"
        "Make your analysis:\n"
        "- Forward-thinking and specific, avoiding general statements\n"
        "- Rich with numerical data and concrete examples\n"
        "- Focused on emerging rather than established trends\n"
        "- Technical and detailed while remaining strategic\n"
        "Do not include any citations or references within the text - save all links for the 'Further Reading' section.\n\n"
        "Challenge conventional wisdom and provide insights that would be valuable to industry leaders "
        "and strategic decision-makers."
    )

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post(
        "https://api.perplexity.ai/chat/completions",
        headers=headers,
        json=payload
    )

    if response.status_code == 200:
        content = response.json()["choices"][0]["message"]["content"]
        # Save the content to file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return content
    else:
        raise Exception(f"API request failed with status code {response.status_code}")


def add_to_notion(vertical, content, client):
    """Add research to Notion database using proper markdown formatting"""
    # Create the page in the database to get its ID
    new_page = client.pages.create(
        parent={"database_id": NOTION_DATABASE_ID},
        properties={
            "Name": {"title": [{"text": {"content": vertical}}]},
        },
    )

    # Add the content to the page
    add_content_to_notion(client, new_page["id"], content)

    return new_page["url"]


def main():
    """Main function to orchestrate the research process"""
    config = load_config()
    template = read_template(config["template"])
    client = Client(auth=NOTION_SECRET)

    for vertical in config["verticals"]:
        try:
            print(f"Processing {vertical}...")

            # Check if research already exists
            file_path = f"{config['verticals_path']}/{vertical.lower().replace(' ', '_')}.md"
            if os.path.exists(file_path):
                print(f"Research for {vertical} already exists, skipping...")
                continue

            # Generate research content
            content = generate_research(
                vertical,
                template,
                config["model"],
                config["verticals_path"]
            )

            print(f"Generated research for {vertical}")

            # Add to Notion
            add_to_notion(vertical, content, client)
            print(f"Added {vertical} research to Notion")

            # Rate limiting for perplexity api
            time.sleep(3)

        except Exception as e:
            print(f"Error processing {vertical}: {str(e)}")
            continue

    # Create report
    create_report()


if __name__ == "__main__":
    main()
