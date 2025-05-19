# McMaster Web Scraper

A web scraping application built with Node.js to extract product information from McMaster-Carr website.

## Prerequisites

- Node.js (v14 or higher)
- npm (Node Package Manager)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd mcmaster-scraper
```

2. Install dependencies:
```bash
npm install puppeteer-extra puppeteer-extra-plugin-stealth csv-parser csv-writer
```

## Project Structure

- `scraper.js` - Main scraping script using Puppeteer
- `urls.csv` - Input file containing URLs to scrape
- `output.csv` - Output file where scraped data will be stored

## Usage

1. Create a `urls.csv` file with a list of McMaster-Carr URLs to scrape. Format should be:
```csv
url
https://www.mcmaster.com/product1
https://www.mcmaster.com/product2
```

2. Run the scraper:
```bash
node scraper.js
```

The script will:
- Read URLs from `urls.csv`
- Scrape data from each URL
- Save results to `output.csv`

## Output Format

The scraper will generate an `output.csv` file with the following columns:
- Head type
- Socket head profile
- Reach
- Country of Origin
- URL



## Dependencies

The Node.js version uses the following packages:
```json:package.json
startLine: 2
endLine: 8
```

## Troubleshooting

- If you encounter "Error: Protocol error", try running with non-headless mode
- Make sure you have a stable internet connection
- Verify that the URLs in urls.csv are valid McMaster-Carr product pages

## License

MIT

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request
