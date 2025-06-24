# File Templates

This directory contains template files used by the AI agents for document generation and workflow automation.

## Structure

Each agent can have its own subdirectory with relevant templates:

- **procurement-agent/**: Templates for procurement documents, contracts, SOWs
- **hr-agent/**: Templates for HR documents, policies, reports
- **finance-agent/**: Templates for financial reports, budgets, analysis
- **operations-agent/**: Templates for operational procedures, checklists
- **general-agent/**: General-purpose templates for various document types

## Usage

Templates are loaded by the document generation tools and customized based on user input and context from the knowledge base.

## Template Format

Templates can be in various formats:
- `.docx` - Microsoft Word documents
- `.xlsx` - Microsoft Excel spreadsheets  
- `.txt` - Plain text templates
- `.md` - Markdown templates
- `.html` - HTML templates

## Adding New Templates

1. Place template files in the appropriate agent subdirectory
2. Update the corresponding agent's document generation tool to reference the new template
3. Test the template generation with sample data

## Example Templates

Sample generic templates are provided to demonstrate the structure and format expected by the document generation system. 