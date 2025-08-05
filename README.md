# Court Data Fetcher & Mini-Dashboard

## Overview
This web application fetches case metadata and the latest orders/judgments from the Delhi High Court via the eCourts portal[](https://services.ecourts.gov.in). It provides a simple form for users to input Case Type, Case Number, Filing Year, and CAPTCHA, then displays the case details (parties' names, filing date, next hearing date, and latest order PDF link). Queries are logged in an SQLite database.

## Target Court
- **Delhi High Court** (https://delhihighcourt.nic.in/, accessed via https://services.ecourts.gov.in)

## Features
- **UI**: HTML form with dropdowns/inputs for Case Type, Case Number, Filing Year, and CAPTCHA.
- **Backend**: Flask-based server that scrapes eCourts using `requests` and `BeautifulSoup`.
- **Storage**: SQLite database to log queries and raw responses.
- **Display**: Parsed case details with a downloadable PDF link for the latest order.
- **Error Handling**: User-friendly messages for invalid inputs or site issues.
- **CAPTCHA Handling**: Manual CAPTCHA input (users visit eCourts, view CAPTCHA image, and enter the code).

## Setup Instructions
1. **Prerequisites**:
   - Python 3.8+
   - VS Code
   - Install dependencies:
     ```bash
     pip install flask requests beautifulsoup4 lxml