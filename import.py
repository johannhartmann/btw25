import spacy
import fitz  # PyMuPDF for extracting text from PDFs
import csv
import requests
import io
import sys
import json
from fake_useragent import UserAgent
import re

# Load spaCy model for German
nlp = spacy.load("de_core_news_sm")

def load_sentiws():
    """Load SentiWS data from local files and return dictionaries for positive and negative words."""
    positive = {}
    negative = {}

    def load_file(filepath, sentiment_dict):
        with open(filepath, "r", encoding="utf-8") as file:
            for line in file:
                parts = line.strip().split("\t")
                if len(parts) >= 2:
                    word = parts[0].split("|")[0].lower()
                    sentiment_dict[word] = sentiment_dict.get(word, 0) + 1

    load_file("SentiWS_v2.0_Positive.txt", positive)
    load_file("SentiWS_v2.0_Negative.txt", negative)

    return positive, negative

def clean_text(text):
    """Clean text by removing unwanted characters like separators and excessive punctuation."""
    print("Cleaning text...")
    # Remove sequences of dots, dashes, or other non-alphanumeric characters
    text = re.sub(r"[\.-]{2,}", " ", text)
    # Remove excessive whitespace
    text = re.sub(r"\s+", " ", text).strip()
    print("Text cleaning complete.")
    return text

def calculate_sentiments(text, positive, negative):
    """Calculate sentiment counts for the given text using SentiWS."""
    print("Calculating sentiments...")
    positive_count = 0
    negative_count = 0
    neutral_count = 0

    doc = nlp(text)
    for token in doc:
        lemma = token.lemma_.lower()
        if lemma in positive:
            positive_count += 1
        elif lemma in negative:
            negative_count += 1
        else:
            neutral_count += 1

    print(f"Sentiments calculated: Positive={positive_count}, Negative={negative_count}, Neutral={neutral_count}")
    return positive_count, negative_count, neutral_count

def extract_text_from_pdf_url(url):
    """Download and extract text from a PDF file via URL."""
    print(f"Downloading PDF from {url}...")
    user_agent = UserAgent().random
    headers = {"User-Agent": user_agent}
    response = requests.get(url, headers=headers)
    if response.status_code == 403:
        raise Exception(f"Access denied (403) for URL: {url}")
    response.raise_for_status()
    print("Download complete. Extracting text...")
    with fitz.open(stream=io.BytesIO(response.content), filetype="pdf") as pdf:
        text = "".join(page.get_text() for page in pdf)
    print("Text extraction complete.")
    return text

def process_text(text, party, year):
    """Process text with spaCy and create structured data."""
    print(f"Processing text for party {party}, year {year}...")
    text = clean_text(text)  # Clean the text before processing
    doc = nlp(text)
    data = []
    for token in doc:
        data.append({
            "token": token.text,
            "pos": token.tag_,  # STTS tag
            "lemma": token.lemma_,
            "party": party,
            "year": str(year)  # Ensure year is a string for TSV output
        })
    print(f"Processing complete for party {party}, year {year}.")
    return data

def save_to_tsv(data, output_file):
    """Save processed data to a single TSV file."""
    print(f"Saving data to {output_file}...")
    fieldnames = ["token", "pos", "lemma", "party", "year"]
    with open(output_file, "a", encoding="utf-8", newline="") as tsvfile:
        writer = csv.DictWriter(tsvfile, fieldnames=fieldnames, delimiter="\t")
        if tsvfile.tell() == 0:
            writer.writeheader()  # Write header only if the file is empty
        writer.writerows(data)
    print(f"Data saved to {output_file}.")

def save_sentiments_to_tsv(sentiments, output_file):
    """Save sentiment analysis results to a TSV file."""
    print(f"Saving sentiments to {output_file}...")
    fieldnames = ["Party", "Year", "Positive", "Negative", "Neutral"]
    with open(output_file, "w", encoding="utf-8", newline="") as tsvfile:
        writer = csv.DictWriter(tsvfile, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(sentiments)
    print(f"Sentiments saved to {output_file}.")

def main():
    """Main function to process a list of PDFs from a JSON file and output results as TSV."""
    with open("party.json", "r", encoding="utf-8") as json_file:
        programs = json.load(json_file)

    output_file = "btw25.tsv"
    sentiment_output_file = "sent25.tsv"
    sentiments = []

    # Load sentiment data from SentiWS files
    positive, negative = load_sentiws()

    # Clear existing data in the output file
    with open(output_file, "w", encoding="utf-8") as f:
        pass

    for program in programs:
        try:
            party = program["Party"]
            year = program["Year"]
            url = program["URL"]

            # Extract text from the PDF URL
            text = extract_text_from_pdf_url(url)

            # Process text and generate structured data
            data = process_text(text, party, year)

            # Save to TSV
            save_to_tsv(data, output_file)

            # Calculate sentiments
            print(f"Analyzing sentiments for {party}, {year}...")
            positive_count, negative_count, neutral_count = calculate_sentiments(text, positive, negative)
            sentiments.append({
                "Party": party,
                "Year": year,
                "Positive": positive_count,
                "Negative": negative_count,
                "Neutral": neutral_count
            })
        except Exception as e:
            print(f"Error processing {program['Party']} ({program['Year']}): {e}", file=sys.stderr)

    # Save sentiments to TSV
    save_sentiments_to_tsv(sentiments, sentiment_output_file)

if __name__ == "__main__":
    main()

    print("Script completed.")