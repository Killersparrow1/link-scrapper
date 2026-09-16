# Link Scrapper

A Python-based interactive TUI (Terminal User Interface) web scraping tool for extracting and collecting links from web pages. This user-friendly utility features a modern terminal interface that makes it easy to crawl websites, parse HTML content, and extract all hyperlinks without needing to write any code.

## Overview

Link Scrapper is a versatile web scraping utility with an intuitive terminal-based user interface designed to automate the process of discovering and collecting URLs from web pages. Whether you're conducting SEO research, validating links, analyzing website structure, or gathering data for content discovery, Link Scrapper provides an efficient and flexible solution with a clean, modern TUI.

Perfect for both technical and non-technical users who want to quickly extract and analyze links from websites directly in the terminal.

## How It Works

Link Scrapper follows a straightforward workflow:

1. **URL Input** - Enter the target URL in the TUI
2. **HTTP Request** - Makes HTTP requests to fetch the web page content
3. **HTML Parsing** - Parses the HTML structure using Python parsing libraries
4. **Link Extraction** - Identifies and extracts all `<a>` tags and their `href` attributes
5. **Link Classification** - Categorizes links (internal, external, anchor links, etc.)
6. **Visual Display** - Shows results in an organized table view in the terminal
7. **Data Export** - Export results in multiple formats with a single command

### Data Flow Diagram

```
URL Input (TUI) → HTTP Request → Response → HTML Parser → Extract Links → Classify → Display in Terminal → Export Option
```

## Features

### Core Scraping Features
- 🕷️ **Interactive TUI** - User-friendly terminal interface with intuitive navigation
- 📝 **Link Collection** - Gather and organize URLs with metadata
- 🔗 **URL Processing** - Handle various URL formats, protocols (HTTP/HTTPS), relative URLs, and anchor links
- 🔍 **Link Classification** - Distinguish between internal and external links automatically
- 📊 **Real-time Display** - View results in an organized table format as they're processed
- 📈 **Statistics** - Automatic calculation of link counts and categorization

### TUI Features
- ✨ **Clean, Modern Terminal Interface** - Beautiful ASCII/Unicode design that's easy to navigate
- 🎯 **One-Command Scraping** - Simple commands to scrape and analyze websites
- 🔄 **Live Progress Indicator** - See scraping progress in real-time in the terminal
- 📋 **Results Table** - View all extracted links in a sortable, filterable table
- 🎨 **Color-Coded Output** - Different colors for different link types
- 📌 **History** - Quick access to recently scraped URLs
- 🔐 **SSL Verification Toggle** - Easy option to handle SSL certificate issues
- ⬆️⬇️ **Keyboard Navigation** - Arrow keys to navigate, Enter to select

### Export & Analysis
- 💾 **Multiple Export Formats** - JSON, CSV, Excel, and Plain Text
- 📄 **One-Command Export** - Export results easily
- 📊 **Statistics Panel** - View detailed breakdown of links
- 🔗 **Link Filtering** - Filter results by link type, domain, or custom criteria
- 📑 **Batch Reports** - Generate comprehensive reports

## Requirements

- **Python** 3.7 or higher
- **requests** - For making HTTP requests
- **BeautifulSoup4** - For HTML parsing
- **Rich** or **Textual** - For beautiful terminal UI (depending on implementation)

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
pip install requests beautifulsoup4 rich
```

## Usage

### Launching the Application

Simply run the main script to launch the TUI:

```bash
python link_scrapper.py
```

Or if it's a different filename:

```bash
python main.py
```

### TUI Walkthrough

#### 1. **Main Menu**
   ```
   ╔═══════════════════════════════════╗
   ║      Link Scrapper v1.0           ║
   ║    Terminal User Interface        ║
   ╠═══════════════════════════════════╣
   ║  [1] Start New Scrape             ║
   ║  [2] View History                 ║
   ║  [3] Export Results               ║
   ║  [4] Settings                     ║
   ║  [5] Help                         ║
   ║  [Q] Quit                         ║
   ╚═══════════════════════════════════╝
   ```

#### 2. **Input Section**
   - Paste or type the URL you want to scrape
   - Press Enter to start
   - Watch the progress indicator as the scraper works

#### 3. **Results Section**
   - View all extracted links in a formatted table
   - Columns typically include:
     - **URL** - The link href
     - **Text** - Link anchor text
     - **Type** - Internal or External
     - **Status** - Valid, Broken, etc.
   - Use arrow keys to navigate through results
   - Press 'c' to copy a link, 'v' to validate, 'e' to export

#### 4. **Filters & Options**
   - Navigate with arrow keys
   - Press 'f' to filter by link type (Internal/External/All)
   - Press 's' to search for specific links
   - Press 'o' to sort by any column

#### 5. **Statistics Panel**
   - Total links found
   - Internal links count
   - External links count
   - Broken links (if checked)
   - Processing time

### Command Reference

**Navigation**
```
↑/↓        - Move up/down in menus and tables
←/→        - Navigate between sections
Enter      - Select/Confirm
Esc        - Go back/Cancel
Tab        - Move to next field
Shift+Tab  - Move to previous field
```

**Actions**
```
S          - Start new scrape
H          - View history
E          - Export results
F          - Filter results
K          - Check/validate links
C          - Copy selected link
V          - Open in browser
D          - Delete from history
?          - Show help
Q          - Quit
```

## TUI Sections

### Main Dashboard
```
┌─────────────────────────────────────────────────────────────┐
│ Link Scrapper Dashboard                              [⚙ ✕]  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Enter URL: https://example.com                           │
│             [Scrape] [Clear] [History]                    │
│                                                             │
│  Status: ⠋ Scraping... (23/45 links found)                │
│                                                             │
│ Results (↑/↓ navigate, c=copy, v=validate, e=export):     │
│ ┌──────────────────────────────────────────────────────┐  │
│ │ URL                    │ Text      │ Type │ Status   │  │
│ ├──────────────────────────────────────────────────────┤  │
│ │ /about                 │ About Us  │ INT  │ ✓ Valid  │  │
│ │ https://example.com    │ Home      │ INT  │ ✓ Valid  │  │
│ │ https://external.com   │ External  │ EXT  │ ✓ Valid  │  │
│ │ /services              │ Services  │ INT  │ ✓ Valid  │  │
│ └──────────────────────────────────────────────────────┘  │
│                                                             │
│ Statistics: Total: 45 | Internal: 35 | External: 10       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Settings Panel
```
┌─────────────────────────────────────────┐
│ Settings                                │
├─────────────────────────────────────────┤
│                                         │
│ Network:                                │
│  └─ Timeout (seconds)        [  10  ]  │
│  └─ Verify SSL Certificate   [  ON  ]  │
│  └─ Use Proxy                [  OFF ]  │
│                                         │
│ Scraping:                               │
│  └─ Include Anchor Links     [  ON  ]  │
│  └─ Follow Redirects         [  ON  ]  │
│  └─ Extract Link Text        [  ON  ]  │
│                                         │
│ Export:                                 │
│  └─ Default Format           [  JSON]  │
│  └─ Save Location            [~/...]   │
│                                         │
│         [Save] [Reset] [Back]           │
└─────────────────────────────────────────┘
```

### Results Display
```
Links found: 45 | Internal: 35 | External: 10 | Time: 2.34s

URL                          Text              Type  Status
─────────────────────────────────────────────────────────────
https://example.com/about    About Us          INT   ✓ Valid
https://example.com/contact  Contact           INT   ✓ Valid
https://external-site.com    Partners          EXT   ✓ Valid
/blog                        Blog Posts        INT   ✓ Valid
#section                     Section Link      ANC   ✓ Valid
https://old-link.com         Old Link          EXT   ✗ Broken

[↑/↓] Navigate | [C]opy | [E]xport | [F]ilter | [V]alidate | [Q]uit
```

## Export Options

Press 'E' to export and choose your format:

```
Select Export Format:
[1] JSON (.json)
[2] CSV (.csv)
[3] Excel (.xlsx)
[4] Plain Text (.txt)
[5] Markdown (.md)

Choice: _
```

## Output Examples

### Table View (in Terminal)
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

| Shortcut | Action |
|----------|--------|
| `S` | Start new scrape |
| `H` | View history |
| `E` | Export results |
| `F` | Filter results |
| `K` | Check/validate links |
| `C` | Copy selected link |
| `V` | Open link in browser |
| `D` | Delete history entry |
| `↑/↓` | Navigate table |
| `Enter` | Select/Confirm |
| `Esc` | Go back |
| `?` | Show help |
| `Q` | Quit application |

## Error Handling

Link Scrapper handles common errors gracefully with visual feedback in the TUI:

- **Connection Errors** - Shows error message and suggests troubleshooting steps
- **Timeout Errors** - Displays timeout notification with retry option
- **Invalid URLs** - Validates URLs before scraping and shows warning
- **HTML Parse Errors** - Continues processing and logs errors
- **SSL Certificate Issues** - Offers option to disable verification

Error messages appear in:
- Status bar at the bottom of the TUI
- Error log accessible from the main menu
- Inline notifications during operations

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
- **Responsive TUI** - Scraping runs in background to keep interface responsive
- **Memory Usage** - Optimized for handling large link collections
- **Processing Speed** - Typical websites scraped in 1-5 seconds
- **Batch Processing** - Queue multiple URLs for sequential scraping
- **Terminal Compatibility** - Works in most modern terminals (256 color support recommended)

## Terminal Requirements

- **Terminal Type**: Most modern terminals (bash, zsh, Windows Terminal, iTerm2, etc.)
- **Colors**: 256-color or True Color support recommended for best appearance
- **Size**: Minimum 80x24 terminal (larger recommended for better table display)
- **Unicode**: UTF-8 encoding support for better visual elements

## Limitations

- **JavaScript-Rendered Content** - Only extracts links from static HTML (does not execute JavaScript)
- **Dynamic Links** - May miss links loaded dynamically after page render
- **Protected Content** - Cannot scrape password-protected or authenticated pages without credentials
- **Robots.txt** - Respects website robots.txt policies by default
- **Rate Limiting** - Includes delays to avoid overwhelming target servers

## Troubleshooting

### Common Issues & Solutions

**Issue: TUI doesn't display correctly**
```bash
# Ensure terminal supports Unicode and colors
export TERM=xterm-256color
python link_scrapper.py

# Or try with basic colors:
export COLORTERM=truecolor
python link_scrapper.py
```

**Issue: Characters are garbled**
- Check your terminal encoding is set to UTF-8
- Try a different terminal emulator
- Run with: `export LC_ALL=en_US.UTF-8`

**Issue: SSL Certificate Error**
- Go to Settings (press 4)
- Toggle "Verify SSL Certificate" OFF
- Try scraping again

**Issue: Timeout Errors**
- Go to Settings (press 4)
- Increase the "Timeout (seconds)" value
- Try scraping again

**Issue: No Links Found**
- Check if the URL is accessible (try in browser)
- Verify the HTML structure contains `<a>` tags
- Check the error log in the TUI

**Issue: Slow Performance**
- Close other terminal windows to free up resources
- Try scraping a simpler/smaller website first
- Check your internet connection

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
- Your Python version, OS, and terminal type
- Full error log from the TUI error menu

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
- Interactive TUI application
- Basic link scraping functionality
- JSON/CSV/Excel export
- Internal/external link classification
- Real-time results display in terminal
- Settings panel
- Link validation
- Statistics dashboard
- Color-coded output
- Full keyboard navigation

### Planned Features
- Batch URL processing
- Link availability checker
- Sitemaps.xml support
- Database export
- Advanced filtering
- Multi-threading support
- Config file support

---

Happy scraping! 🕷️✨

For detailed feature tutorials, check out the [Wiki](https://github.com/Killersparrow1/link-scrapper/wiki)
