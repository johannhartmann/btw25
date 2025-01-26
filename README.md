# BTW25 Text Analysis Tool

This tool performs linguistic analysis and text processing on German political documents, specifically designed for analyzing election manifestos and political texts. It uses spaCy for natural language processing and includes custom sentiment analysis using the SentiWS lexicon.

## Features

- PDF text extraction from URLs
- German language text processing using spaCy
- Sentiment analysis using SentiWS
- Data export to TSV format
- Visualization capabilities using matplotlib, plotly, and seaborn
- Streamlit web interface for interactive analysis

## Installation

1. Clone this repository:
```bash
git clone https://github.com/johannhartmann/btw25.git
cd btw25
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

3. Download the spaCy German model:
```bash
python -m spacy download de_core_news_sm
```

## Components

### Streamlit Interface
The project includes an interactive web interface built with Streamlit that allows users to explore and analyze the election manifestos. To start the interface, run:
```bash
streamlit run frequencies_plotly.py
# or
streamlit run heatmap.py
```

### frequencies_plotly.py
An interactive visualization tool that:
- Displays word frequencies across different party manifestos
- Provides KWIC (Key Word In Context) analysis
- Shows collocations for selected terms
- Includes comparative frequency analysis between parties
- Offers downloadable data tables
- Contains detailed methodology information

### heatmap.py
A visualization tool that generates heatmaps showing:
- Relative frequencies of the most common words in party manifestos
- Separate analyses for different parts of speech (nouns, adjectives, verbs)
- Customizable number of words to display (25-50 terms)
- Color-coded visualization of word frequency distributions across parties

Both tools are designed for analyzing German political texts and include proper citations and timestamps for academic use.