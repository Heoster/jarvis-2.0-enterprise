# Web Search & Scraping Guide

## Overview

Jarvis now includes advanced web search and scraping capabilities that allow you to search the web using DuckDuckGo and retrieve detailed content from web pages, including text and headings.

## Features

✅ **DuckDuckGo Search Integration** - Search the web without API keys
✅ **Intelligent Web Scraping** - Extract content with preserved formatting
✅ **Heading Preservation** - H1, H2, H3, H4 headings are clearly marked
✅ **Automatic Detection** - Jarvis automatically detects when to search
✅ **Content Caching** - Results are cached for 1 hour to improve performance
✅ **Rich Formatting** - Results are displayed with clear visual structure

## How to Use

### Trigger Web Search

Simply ask Jarvis to search for information using natural language:

```
"search for Python programming"
"what is artificial intelligence"
"find information about machine learning"
"look up latest news on AI"
"tell me about quantum computing"
```

### Keywords that Trigger Search

The following keywords will automatically trigger web search:
- `search`
- `find`
- `look up`
- `what is`
- `who is`
- `latest`
- `news about`
- `information on`
- `tell me about`

### What You'll See

When Jarvis performs a web search, you'll see:

1. **Search Header** - Shows what was searched
2. **Result Count** - Number of pages successfully scraped
3. **For Each Result:**
   - **Title** - Page title
   - **Source URL** - Link to the original page
   - **Search Summary** - Snippet from search results
   - **Page Description** - Meta description if available
   - **Scraped Content** - Actual text from the page with:
     - H1 headings marked with `═══ HEADING ═══`
     - H2 headings marked with `▸ Heading`
     - H3/H4 headings marked with `• Heading`
     - List items marked with `- Item`
     - Up to 1500 characters per result
4. **Summary Footer** - Total results and suggestions

## Example Output

```
================================================================================
🔍 SEARCH RESULTS FOR: 'Python programming'
================================================================================

✅ Successfully scraped 3 pages with detailed content:

────────────────────────────────────────────────────────────────────────────────
📄 RESULT #1
────────────────────────────────────────────────────────────────────────────────

TITLE: Python Programming Tutorial

🔗 SOURCE: https://example.com/python-tutorial

📝 SEARCH SUMMARY:
Learn Python programming from basics to advanced concepts...

📖 SCRAPED CONTENT:
────────────────────────────────────────────────────────────────────────────────

═══ PYTHON PROGRAMMING TUTORIAL ═══

▸ Introduction to Python

Python is a high-level programming language...

• Getting Started
  - Install Python
  - Set up your environment
  - Write your first program

▸ Basic Concepts

Variables and data types are fundamental...

────────────────────────────────────────────────────────────────────────────────
(Showing 1500 of 5000 characters)

💾 Full content available: 5000 characters total

================================================================================
✅ SEARCH COMPLETE
================================================================================

I've retrieved and analyzed 3 web pages for you, sir.
The content above includes the actual text scraped from each page.

Would you like me to:
• Search for more specific information?
• Explore any of these sources in more detail?
• Summarize the key points from these results?
```

## Technical Details

### Web Scraper Features

- **Smart Content Extraction** - Finds main content area (article, main, content div)
- **Noise Removal** - Removes scripts, styles, navigation, footers
- **Heading Preservation** - Maintains document structure
- **Link Extraction** - Captures up to 20 relevant links
- **Caching** - 1-hour cache to reduce redundant requests
- **Error Handling** - Graceful fallback on failures

### Scraping Process

1. **Search DuckDuckGo** - Get top results for query
2. **Scrape Pages** - Extract content from each result
3. **Format Content** - Preserve headings and structure
4. **Display Results** - Show formatted content to user

### Content Limits

- **Search Results**: Up to 10 results per search
- **Pages Scraped**: Top 3 results by default
- **Content per Page**: Up to 10,000 characters
- **Display per Result**: Up to 1,500 characters
- **Cache Duration**: 1 hour

## Testing

### Run the Test Script

```bash
python test_search_display.py
```

This will test:
- Web search detection
- Content scraping
- Heading preservation
- Result formatting

### Run Comprehensive Tests

```bash
python test_web_search.py
```

This includes:
- DuckDuckGo search
- Webpage scraping
- Combined search and scrape
- Jarvis brain integration

## Troubleshooting

### No Results Showing

1. **Check Internet Connection** - Ensure you're online
2. **Check Logs** - Look for error messages in console
3. **Try Different Query** - Use clearer search terms
4. **Check Firewall** - Ensure web requests aren't blocked

### Content Not Displaying

1. **Check Query** - Ensure it contains search keywords
2. **View Logs** - Look for "🔍 Query requires web search" message
3. **Test Directly** - Run `test_search_display.py`
4. **Check Scraper** - Run `test_web_search.py`

### Slow Performance

1. **Reduce Results** - Scraping takes time
2. **Use Cache** - Repeat queries use cached results
3. **Check Network** - Slow connection affects speed
4. **Wait Patiently** - Scraping 3 pages takes 5-10 seconds

## Configuration

### Adjust Number of Results

In `core/jarvis_brain.py`, modify:

```python
web_results = await self.web_scraper.search_and_scrape(search_query, num_results=3)
```

Change `num_results=3` to desired number (1-10 recommended).

### Adjust Content Length

In `core/web_scraper.py`, modify:

```python
if len(content) > 10000:
    content = content[:10000]
```

Change `10000` to desired character limit.

### Adjust Display Length

In `core/jarvis_brain.py`, modify:

```python
display_content = content[:1500]
```

Change `1500` to desired display length.

## API Integration

The web search feature works without any API keys! It uses:
- **DuckDuckGo HTML Search** - No API key required
- **Direct HTTP Requests** - Standard web scraping
- **BeautifulSoup** - HTML parsing

## Privacy & Ethics

- **Respects robots.txt** - Follows web standards
- **Rate Limiting** - Caching prevents excessive requests
- **User Agent** - Identifies as a browser
- **No Personal Data** - Only scrapes public content

## Future Enhancements

Planned improvements:
- [ ] PDF content extraction
- [ ] Image description extraction
- [ ] Video transcript scraping
- [ ] Multi-language support
- [ ] Advanced filtering options
- [ ] Custom scraping rules
- [ ] Export results to file

## Support

If you encounter issues:
1. Check this guide
2. Run test scripts
3. Review logs
4. Check GitHub issues
5. Contact support

## Credits

- **DuckDuckGo** - Search engine
- **BeautifulSoup** - HTML parsing
- **aiohttp** - Async HTTP client
- **Jarvis Team** - Integration & development

---

**Last Updated**: 2024
**Version**: 1.0
**Status**: ✅ Fully Operational
