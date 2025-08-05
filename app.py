from flask import Flask, request, render_template, jsonify
import requests
import json
import sqlite3
from urllib.parse import urlencode
import re
from database import init_db, log_query
import time
from html import unescape  # To decode HTML entities like &nbsp;

app = Flask(__name__)

# Delhi High Court base URL
ECOURTS_URL = "https://delhihighcourt.nic.in/app/"

def clean_html_text(text):
    """Remove HTML tags and decode entities, preserving basic structure."""
    if not text or not isinstance(text, str):
        return "N/A"
    # Remove <br> tags and decode &nbsp; to space
    text = re.sub(r'<br>', ' ', text)  # Replace <br> with space
    text = re.sub(r'&\w+;', ' ', text)  # Replace HTML entities (e.g., &nbsp;) with space
    text = re.sub(r'<[^>]+>', '', text)  # Remove any remaining tags
    text = unescape(text)  # Decode HTML entities
    return ' '.join(text.split())  # Normalize spaces

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/fetch_case", methods=["POST"])
def fetch_case():
    try:
        case_type = request.form["case_type"].replace("WP(C)", "W.P.(C)").strip()  # Normalize to W.P.(C)
        case_number = request.form["case_number"]
        filing_year = int(request.form["filing_year"])  # Ensure integer
        captcha = request.form["captcha"]

        # Use a session to maintain cookies
        session = requests.Session()

        # Initial request to establish session on the specific endpoint
        session.get(ECOURTS_URL + "get-case-type-status", headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Referer": ECOURTS_URL + "get-case-type-status"
        }, timeout=30)

        # Prepare query parameters for GET request
        params = {
            "draw": "3",
            "columns[0][data]": "DT_RowIndex",
            "columns[0][name]": "DT_RowIndex",
            "columns[0][searchable]": "true",
            "columns[0][orderable]": "false",
            "columns[0][search][value]": "",
            "columns[0][search][regex]": "false",
            "columns[1][data]": "ctype",
            "columns[1][name]": "ctype",
            "columns[1][searchable]": "true",
            "columns[1][orderable]": "true",
            "columns[1][search][value]": "",
            "columns[1][search][regex]": "false",
            "columns[2][data]": "pet",
            "columns[2][name]": "pet",
            "columns[2][searchable]": "true",
            "columns[2][orderable]": "true",
            "columns[2][search][value]": "",
            "columns[2][search][regex]": "false",
            "columns[3][data]": "orderdate",
            "columns[3][name]": "orderdate",
            "columns[3][searchable]": "true",
            "columns[3][orderable]": "true",
            "columns[3][search][value]": "",
            "columns[3][search][regex]": "false",
            "order[0][column]": "0",
            "order[0][dir]": "asc",
            "order[0][name]": "DT_RowIndex",
            "start": "0",
            "length": "50",
            "search[value]": "",
            "search[regex]": "false",
            "case_type": case_type,  # Now "W.P.(C)"
            "case_number": case_number,
            "case_year": filing_year,  # Integer
            "_": str(int(time.time() * 1000))  # Dynamic timestamp
        }

        # Log the request URL for debugging
        request_url = ECOURTS_URL + "get-case-type-status?" + urlencode(params, doseq=True)
        print(f"Request URL: {request_url}")

        # Headers to mimic a browser
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Referer": ECOURTS_URL + "get-case-type-status",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest"
        }

        # Make GET request to Delhi High Court with session
        time.sleep(2)  # Optional delay to avoid rate limiting
        response = session.get(ECOURTS_URL + "get-case-type-status", params=params, headers=headers, timeout=30)

        # Log query to database
        log_query(case_type, case_number, filing_year, response.text)

        # Parse JSON response
        data = json.loads(response.text) if response.text else {}
        
        case_details = {
            "parties": "N/A",
            "filing_date": "N/A",
            "next_hearing": "N/A",
            "order_link": "N/A"
        }

        # Extract details from JSON response
        if data and "data" in data:
            for row in data["data"]:
                if str(row.get("cno")) == case_number and row.get("cyear") == filing_year:
                    case_details["parties"] = clean_html_text(row.get("pet", "N/A"))
                    case_details["filing_date"] = clean_html_text(row.get("orderdate", "N/A")).split("Last Date: ")[1].split(" ")[0] if "Last Date" in clean_html_text(row.get("orderdate", "")) else "N/A"
                    case_details["next_hearing"] = clean_html_text(row.get("h_d_dt", "N/A"))
                    # Extract order link from ctype
                    order_link_match = re.search(r'https:\/\/delhihighcourt\.nic\.in\/app\/case-type-status-details\/[^\'"]+', row.get("ctype", ""))
                    case_details["order_link"] = order_link_match.group(0) if order_link_match else "N/A"

        # Check for errors
        if "error" in data or "Page Expired" in response.text or data.get("recordsTotal") == 0:
            case_details["parties"] = "No case found or invalid input"

        with open("response.html", "w", encoding="utf-8") as f:
            f.write(response.text)  # Save JSON for debugging

        return jsonify(case_details)

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"})

if __name__ == "__main__":
    init_db()  # Initialize database
    app.run(debug=True)