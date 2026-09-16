# Link Scrapper

A Python-based interactive GUI web scraping tool for extracting and collecting links from web pages. This user-friendly utility features a modern graphical interface that makes it easy to crawl websites, parse HTML content, and extract all hyperlinks without needing to write any code.

## Overview

Link Scrapper is a versatile web scraping utility with an intuitive graphical user interface designed to automate the process of discovering and collecting URLs from web pages. Whether you're conducting SEO research, validating links, analyzing website structure, or gathering data for content discovery, Link Scrapper provides an efficient and flexible solution with a clean, modern interface.

Perfect for both technical and non-technical users who want to quickly extract and analyze links from websites.

## How It Works

Link Scrapper follows a straightforward workflow:

1. **URL Input** - Enter the target URL in the GUI
2. **HTTP Request** - Makes HTTP requests to fetch the web page content
3. **HTML Parsing** - Parses the HTML structure using Python parsing libraries
4. **Link Extraction** - Identifies and extracts all `<a>` tags and their `href` attributes
5. **Link Classification** - Categorizes links (internal, external, anchor links, etc.)
6. **Visual Display** - Shows results in an organized table/list view
7. **Data Export** - Export results in multiple formats with a single click

### Data Flow Diagram

```
URL Input (GUI) → HTTP Request → Response → HTML Parser → Extract Links → Classify → Display in GUI → Export Option
```

## Features

### Core Scraping Features
- 🕷️ **Interactive GUI** - User-friendly interface with drag-and-drop URL input
- 📝 **Link Collection** - Gather and organize URLs with metadata
- 🔗 **URL Processing** - Handle various URL formats, protocols (HTTP/HTTPS), relative URLs, and anchor links
- 🔍 **Link Classification** - Distinguish between internal and external links automatically
- 📊 **Real-time Display** - View results in an organized table format as they're processed
- 📈 **Statistics** - Automatic calculation of link counts and categorization

### GUI Features
- ✨ **Clean, Modern Interface** - Intuitive design that's easy to navigate
- 🎯 **One-Click Scraping** - Simply paste a URL and click the scrape button
- 🔄 **Live Progress Indicator** - See scraping progress in real-time
- 📋 **Results Table** - View all extracted links in a sortable, filterable table
- 🖥️ **Dark/Light Theme** (Optional) - Customize the interface appearance
- 📌 **History** - Quick access to recently scraped URLs
- 🔐 **SSL Verification Toggle** - Easy option to handle SSL certificate issues

### Export & Analysis
- 💾 **Multiple Export Formats** - JSON, CSV, Excel, and Plain Text
- 📄 **One-Click Export** - Export results with a single button click
- 📊 **Statistics Panel** - View detailed breakdown of links
- 🔗 **Link Filtering** - Filter results by link type, domain, or custom criteria
- 📑 **Batch Reports** - Generate comprehensive reports

## Requirements

- **Python** 3.7 or higher
- **tkinter** - For GUI (usually included with Python)
- **requests** - For making HTTP requests
- **BeautifulSoup4** - For HTML parsing
- **Pillow** (Optional) - For enhanced image display in GUI

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Killersparrow1/link-scrapper.git
cd link-scrapper
```

### 2. Create a Virtual Environment (Optional but Recommended)

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install requests beautifulsoup4 pillow
```

## Usage

### Launching the Application

Simply run the main script to launch the GUI:

```bash
python link_scrapper.py
```

Or if it's a different filename:

```bash
python main.py
```

### GUI Walkthrough

#### 1. **Input Section**
   - Paste or type the URL you want to scrape
   - Click "Scrape" or press Enter to start
   - Watch the progress indicator as the scraper works

#### 2. **Results Section**
   - View all extracted links in the results table
   - Columns typically include:
     - **URL** - The link href
     - **Text** - Link anchor text
     - **Type** - Internal or External
     - **Status** - Valid, Broken, etc.

#### 3. **Filters & Options**
   - Filter by link type (Internal/External/All)
   - Search for specific links
   - Sort by any column
   - Copy individual links or all results

#### 4. **Export Section**
   - Select export format (JSON, CSV, Excel, TXT)
   - Choose save location
   - Click "Export" to save results

#### 5. **Statistics Panel**
   - Total links found
   - Internal links count
   - External links count
   - Broken links (if checked)
   - Processing time

### Menu Options

**File Menu**
- New Scrape
- Open Recent
- Export Results
- Exit

**Tools Menu**
- Settings/Preferences
- Check Links (Validate URLs)
- Clear History
- About

**Help Menu**
- Documentation
- Keyboard Shortcuts
- Check for Updates
- Report Bug

## GUI Features in Detail

### Scraping Options (Settings)

Within the GUI, you can configure:

- **Timeout** - Set HTTP request timeout duration
- **User-Agent** - Customize the user agent string
- **SSL Verification** - Enable/disable SSL certificate validation
- **Proxy** - Configure proxy server (if needed)
- **Include Anchor Links** - Choose to include or exclude anchor links
- **Follow Redirects** - Handle URL redirects
- **Extract Link Text** - Capture anchor text along with URLs

### Results Table Features

- **Sortable Columns** - Click column headers to sort
- **Right-Click Context Menu** - Copy, open, or validate individual links
- **Search Bar** - Quick filter by keyword
- **Select All/None** - Bulk selection for export
- **Drag & Drop** - Reorder or manage results

### Visual Indicators

- 🟢 **Green** - Valid/Internal links
- 🔵 **Blue** - External links
- 🟡 **Yellow** - Broken/Invalid links
- ⚪ **Gray** - Anchor links

## Output Examples

### Table View (in GUI)
```
URL                          | Text              | Type       | Status
---------------------------  | ---------------   | ---------- | --------
https://example.com/about    | About Us          | Internal   | ✓ Valid
https://external-site.com    | External Link     | External   | ✓ Valid
/contact                     | Contact           | Internal   | ✓ Valid
#section                     | Section Link      | Anchor     | ✓ Valid
```

### JSON Export
```json
{
  "url": "https://example.com",
  "scraped_at": "2024-01-15 10:30:45",
  "total_links": 45,
  "links": [
    {
      "href": "https://example.com/about",
      "text": "About Us",
      "type": "internal",
      "status": "valid"
    },
    {
      "href": "https://external-site.com",
      "text": "External Link",
      "type": "external",
      "status": "valid"
    }
  ],
  "statistics": {
    "total": 45,
    "internal": 35,
    "external": 10,
    "broken": 0,
    "processing_time_seconds": 2.34
  }
}
```

### CSV Export
```csv
href,text,type,status,scraped_at
https://example.com/about,About Us,internal,valid,2024-01-15 10:30:45
https://external-site.com,External Link,external,valid,2024-01-15 10:30:45
```

## Keyboard Shortcuts

- `Ctrl+N` - New scrape
- `Ctrl+E` - Export results
- `Ctrl+C` - Copy selected link(s)
- `Ctrl+A` - Select all results
- `Ctrl+F` - Open find/filter
- `Ctrl+Q` - Quit application
- `F5` - Refresh results
- `Enter` - Start scraping (when URL field is focused)

## Error Handling

Link Scrapper handles common errors gracefully with visual feedback:

- **Connection Errors** - Shows error message and suggests troubleshooting steps
- **Timeout Errors** - Displays timeout notification with retry option
- **Invalid URLs** - Validates URLs before scraping and shows warning
- **HTML Parse Errors** - Continues processing and logs errors
- **SSL Certificate Issues** - Offers option to disable verification

Error messages appear in:
- Status bar at the bottom
- Pop-up dialogs for critical errors
- Error log (accessible from menu)

## API Usage (Python Module)

You can also use Link Scrapper as a Python module in your own scripts:

```python
from link_scrapper import LinkScrapper

# Create scraper instance
scraper = LinkScrapper()

# Scrape a website
results = scraper.scrape("https://example.com")

# Access results
print(f"Total links found: {results['total_links']}")
print(f"Internal links: {results['internal_links']}")
print(f"External links: {results['external_links']}")

# Get all links
for link in results['links']:
    print(f"{link['href']} - {link['text']} ({link['type']})")

# Export results
scraper.export_to_json(results, "output.json")
scraper.export_to_csv(results, "output.csv")
```

## Performance Considerations

- **Large Websites** - Efficiently handles pages with thousands of links
- **Responsive GUI** - Scraping runs in background thread to keep interface responsive
- **Memory Usage** - Optimized for handling large link collections
- **Processing Speed** - Typical websites scraped in 1-5 seconds
- **Batch Processing** - Queue multiple URLs for sequential scraping

## Limitations

- **JavaScript-Rendered Content** - Only extracts links from static HTML (does not execute JavaScript)
- **Dynamic Links** - May miss links loaded dynamically after page render
- **Protected Content** - Cannot scrape password-protected or authenticated pages without credentials
- **Robots.txt** - Respects website robots.txt policies by default
- **Rate Limiting** - Includes delays to avoid overwhelming target servers

## Troubleshooting

### Common Issues & Solutions

**Issue: GUI doesn't launch**
```bash
# Make sure tkinter is installed
python -m tkinter

# If missing, install it:
# On Ubuntu/Debian
sudo apt-get install python3-tk

# On macOS with homebrew
brew install python-tk
```

**Issue: SSL Certificate Error**
- Go to Settings → Security
- Toggle "Verify SSL Certificate" OFF
- Try scraping again

**Issue: Timeout Errors**
- Go to Settings → Network
- Increase the "Timeout (seconds)" value
- Try scraping again

**Issue: No Links Found**
- Check if the URL is accessible (try in browser)
- Verify the HTML structure contains `<a>` tags
- Enable "Verbose Mode" in Settings to see detailed logs
- Check the error log in the GUI

**Issue: Slow Performance**
- Reduce the number of concurrent requests in Settings
- Close other applications to free up memory
- Try scraping a simpler/smaller website first

## Contributing

Contributions are welcome! Here's how you can help:

1. **Fork** the repository
2. **Create a feature branch** - `git checkout -b feature/your-feature`
3. **Make your changes** and test them thoroughly
4. **Commit with clear messages** - `git commit -m "Add your feature description"`
5. **Push to the branch** - `git push origin feature/your-feature`
6. **Submit a Pull Request** with a detailed description

### Bug Reports

Found a bug? Please open an issue with:
- Detailed description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Screenshots (if applicable)
- Your Python version, OS, and Python environment
- Full error log from the GUI

### Feature Requests

Have a great idea? Open an issue describing:
- The feature you'd like
- Why you think it would be useful
- Any example usage scenarios

## License

This project is open source and available under the MIT License. See the LICENSE file for details.

## Disclaimer

This tool is for educational and legitimate purposes only. Always respect:
- Website terms of service
- robots.txt files
- Server resources and rate limits
- Privacy policies
- Copyright laws

Always obtain permission before scraping websites that don't allow automated access. Excessive scraping may be considered a denial-of-service attack.

## Support & Contact

For questions, issues, or suggestions:
- 🐛 Open an [issue on GitHub](https://github.com/Killersparrow1/link-scrapper/issues)
- 📧 Contact the maintainer: [Killersparrow1](https://github.com/Killersparrow1)
- 💬 Check existing issues for common problems

## Changelog

### Version 1.0.0 (Current)
- Interactive GUI application
- Basic link scraping functionality
- JSON/CSV/Excel export
- Internal/external link classification
- Real-time results display
- Settings panel
- Link validation
- Statistics dashboard

### Planned Features
- Batch URL processing
- Link availability checker
- Sitemaps.xml support
- Browser integration
- Database export
- Advanced filtering
- Multi-threading support

## Screenshots

*[Screenshots would show the main GUI window, results table, export dialog, settings panel, etc.]*

---

## Quick Start Video

*[Link to tutorial video would go here]*

---

Happy scraping! 🕷️✨

For detailed feature tutorials, check out the [Wiki](https://github.com/Killersparrow1/link-scrapper/wiki)
