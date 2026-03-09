# Data Folder

This folder contains the Excel files for bulk enrichment.

## Input File

Place your input Excel file as `input.xlsx` with the following columns:

| Column | Required | Description |
|--------|----------|-------------|
| profileUrl | Yes | LinkedIn profile URL |

## Output File

After running the bulk enrichment, the results will be saved to `enriched_output.xlsx` with the following additional columns:

| Column | Description |
|--------|-------------|
| Email | Email address found |
| Phone | Phone number found |
| First Name | First name |
| Last Name | Last name |
| Company | Company name |
| Job Title | Job title |
| Location | City |
| Country | Country |
