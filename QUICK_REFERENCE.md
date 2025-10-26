# 🚀 JARVIS MASTER - Quick Reference Card

## ⚡ Quick Start

```bash
# Setup (first time only)
python setup_jarvis.py

# Start JARVIS
python start_jarvis.py

# Run tests
python test_jarvis_complete.py
```

---

## 💬 Common Commands

### Conversational
```
Hello Jarvis
How are you?
What can you do?
Help
Status
```

### Web Search
```
Search for [topic]
Find information about [topic]
Look up [topic]
```

### Indian Finance 🇮🇳
```
What's the Bitcoin price in INR?
Show me currency exchange rates
Check mutual fund NAV
SBI Bluechip fund NAV
```

### Railway 🚂
```
Show trains from Muzaffarnagar
Train schedule for [train number]
Railway information
```

### Entertainment 😄
```
Tell me a joke
Tell me a programming joke
Show me a dog image
Give me a cat fact
Give me an inspirational quote
```

### Knowledge 📚
```
What is [topic]?
Tell me about [topic]
Explain [concept]
```

### Math 🔢
```
Calculate 25 * 4 + 10
Solve 100 / 5
What is 15 + 30?
```

---

## 🎯 Features at a Glance

| Feature | Status | API Key Required |
|---------|--------|------------------|
| Web Search | ✅ | No |
| Web Scraping | ✅ | No |
| Bitcoin Price (INR) | ✅ | No |
| Currency Rates | ✅ | No |
| Mutual Funds | ✅ | No |
| Entertainment | ✅ | No |
| Wikipedia | ✅ | No |
| Conversations | ✅ | No |
| Math | ✅ | No |
| Weather | ✅ | Yes (optional) |
| News | ✅ | Yes (optional) |
| Railway | ✅ | Yes (optional) |

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `jarvis_master.py` | Main entry point |
| `start_jarvis.py` | Simple launcher |
| `setup_jarvis.py` | Setup script |
| `test_jarvis_complete.py` | Test suite |
| `JARVIS_COMPLETE_GUIDE.md` | Complete documentation |
| `README_JARVIS_MASTER.md` | Quick start guide |

---

## 🔧 Configuration

### No API Keys (Default)
Most features work without any configuration!

### With API Keys (Optional)
Create `.env` file:
```env
OPENWEATHER_API_KEY=your_key_here
NEWS_API_KEY=your_key_here
RAILWAY_API_KEY=your_key_here
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Slow first response | Normal - models loading |
| Missing dependencies | Run `python setup_jarvis.py` |
| Web search not working | Install: `pip install duckduckgo-search` |
| Import errors | Check Python version (3.8+) |

---

## 📊 System Status

Check anytime by typing: `status`

Shows:
- System operational status
- Session information
- Interaction count
- Feature availability
- Brain status

---

## 💡 Pro Tips

1. **First query is slow** - Models are loading. Subsequent queries are fast.
2. **Most features work offline** - Except web search and real-time data.
3. **No API keys needed** - For most features!
4. **Type naturally** - No special commands required.
5. **Context aware** - Jarvis remembers your conversation.

---

## 🎓 Example Session

```
$ python start_jarvis.py

Jarvis: Good morning, sir. Jarvis at your service. How may I assist you today?

You: Hello Jarvis

Jarvis: Good morning, Heoster. Jarvis at your service. Systems are online and ready.

You: What's the Bitcoin price in INR?

Jarvis: [Shows detailed Bitcoin price in Indian Rupees with exchange rates]

You: Tell me a joke

Jarvis: [Shares a random joke]

You: Search for Python tutorials

Jarvis: [Performs web search, scrapes results, provides detailed information]

You: Thanks!

Jarvis: You're most welcome, sir. I'm here whenever you need assistance.

You: exit

Jarvis: Until next time, Heoster. Jarvis standing by.
```

---

## 📚 More Information

- **Complete Guide**: [JARVIS_COMPLETE_GUIDE.md](JARVIS_COMPLETE_GUIDE.md)
- **Quick Start**: [README_JARVIS_MASTER.md](README_JARVIS_MASTER.md)
- **Summary**: [JARVIS_MASTER_SUMMARY.md](JARVIS_MASTER_SUMMARY.md)

---

## 🎉 That's It!

You're ready to use JARVIS MASTER!

```bash
python start_jarvis.py
```

**Enjoy your personal AI assistant!** 🚀

---

**Built with ❤️ by Codeex AI Company**
