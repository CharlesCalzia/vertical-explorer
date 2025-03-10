import os
import markdown
from weasyprint import HTML, CSS


def create_report(verticals_path="verticals", output_filename=None):
    """Combine all markdown files in verticals directory into a single PDF report"""

    if output_filename is None:
        output_filename = "research_report.pdf"

    # Ensure output path is in the verticals directory
    output_path = os.path.join(verticals_path, output_filename)

    # Initialize HTML content with some basic styling
    html_content = """
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            h1 {{ 
                color: #2c3e50;
                font-size: 24px;
                margin-bottom: 20px;
            }}
            .vertical-title {{ 
                color: #0066cc;
            }}
            h2 {{ color: #34495e; }}
            h3 {{ color: #7f8c8d; }}
            .vertical-section {{ page-break-before: always; }}
        </style>
    </head>
    <body>
    """

    # Get all markdown files
    md_files = [f for f in os.listdir(verticals_path) if f.endswith('.md')]
    md_files.sort()  # Sort files alphabetically

    # Convert each markdown file to HTML and append
    for i, md_file in enumerate(md_files):
        print(f"Processing {md_file}...")
        file_path = os.path.join(verticals_path, md_file)

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Convert markdown to HTML
        html = markdown.markdown(content, extensions=['tables', 'fenced_code'])

        # Add section title (derived from filename)
        section_title = md_file.replace('.md', '').replace('_', ' ').title()
        # Add page-break class to all sections except the first one
        section_class = ' class="vertical-section"' if i > 0 else ''
        html_content += f'\n<div{section_class}><h1 class="vertical-title">{section_title}</h1>\n{html}</div>'

    html_content += "</body></html>"

    # Convert HTML to PDF
    print("Converting to PDF...")
    HTML(string=html_content).write_pdf(
        output_path,
        stylesheets=[CSS(string='''
            @page { margin: 2cm; }
            body { font-size: 12px; }
        ''')]
    )

    print(f"Report generated successfully: {output_path}")
    return output_path


if __name__ == "__main__":
    create_report()
