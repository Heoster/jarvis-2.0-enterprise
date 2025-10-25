# Web Search Quick Start 🔍

## How to Search with Jarvis

Just ask naturally! Jarvis will automatically search the web and show you detailed results with scraped content.

## Example Queries

```
✅ "search for Python tutorials"
✅ "what is machine learning"
✅ "find information about AI"
✅ "look up latest news on technology"
✅ "tell me about quantum computing"
```

## What You Get

📄 **Page Titles** - Clear heading for each result
🔗 **Source URLs** - Links to original pages
📝 **Summaries** - Quick overview from search
📖 **Full Content** - Actual text scraped from pages
🎯 **Headings** - H1, H2, H3 preserved with formatting

## Test It Now

Run this command to test:
```bash
python test_search_display.py
```

Or just ask Jarvis:
```
"search for Python programming"
```

## Expected Output Format

```
================================================================================
🔍 SEARCH RESULTS FOR: 'your query'
================================================================================

✅ Successfully scraped 3 pages with detailed content:

────────────────────────────────────────────────────────────────────────────────
📄 RESULT #1
────────────────────────────────────────────────────────────────────────────────

TITLE: Page Title Here

🔗 SOURCE: https://example.com

📝 SEARCH SUMMARY:
Brief description from search results...

📖 SCRAPED CONTENT:
────────────────────────────────────────────────────────────────────────────────

═══ MAIN HEADING ═══

▸ Subheading

Actual content from the page with preserved formatting...

• Section heading
  - List item
  - Another item

More content here...

────────────────────────────────────────────────────────────────────────────────
(Showing 1500 of 5000 characters)

💾 Full content available: 5000 characters total

[Results 2 and 3 follow same format]

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

## Troubleshooting

**Not seeing results?**
1. Check your internet connection
2. Make sure your query includes search keywords
3. Run `python test_search_display.py` to verify
4. Check console logs for errors

**Results too short?**
- Jarvis shows first 1500 characters per result
- Full content is available (see character count)
- Ask for more details on specific results

**Taking too long?**
- Scraping 3 pages takes 5-10 seconds
- Results are cached for 1 hour
- Repeat queries are instant

## Need More Help?

📖 Read the full guide: `WEB_SEARCH_GUIDE.md`
🧪 Run tests: `python test_web_search.py`
📝 Check logs: Look for 🔍 emoji in console

---

**Ready to search? Just ask Jarvis!** 🚀
