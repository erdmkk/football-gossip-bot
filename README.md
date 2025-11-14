# ⚽ Football Gossip Bot

🔥 Automated Twitter bot that tracks and tweets about football stars' Twitter follow/unfollow activities, creating viral sports gossip content.

## 🎯 Features

- 🔍 Monitors top 50+ football players' Twitter following lists
- 🚨 Detects follow/unfollow changes in real-time
- 🤖 Automatically generates engaging tweets
- 📊 Drama scoring algorithm for viral potential
- 🗄️ SQLite database for historical tracking
- ⏰ Automated scheduling
- 🐳 Docker support

## 📸 Example Tweets

```
🚨 JUST IN: Cristiano Ronaldo just UNFOLLOWED Piers Morgan!

What happened? 👀🍿

#CR7 #Ronaldo
```

```
⚡ Lionel Messi started following Tom Brady!

The GOATs recognizing GOATs 🐐🤝🐐

#Messi #TomBrady
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Twitter API Developer Account (with elevated access)
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/erdmkk/football-gossip-bot.git
cd football-gossip-bot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your Twitter API credentials
```

### Configuration

Edit `.env` file:

```env
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_SECRET=your_access_secret
TWITTER_BEARER_TOKEN=your_bearer_token

# Bot Settings
CHECK_INTERVAL_MINUTES=60
MIN_DRAMA_SCORE=30
AUTO_TWEET=true
```

### Run

```bash
# Run the bot
python src/main.py

# Run with Docker
docker-compose up -d
```

## 📊 How It Works

1. **Monitor**: Checks athletes' following lists every hour
2. **Detect**: Compares with previous snapshot to find changes
3. **Score**: Calculates drama score based on multiple factors
4. **Generate**: Creates engaging tweet content
5. **Post**: Automatically tweets high-scoring gossip

### Drama Score Algorithm

```python
Factors:
- Unfollow > Follow (higher drama)
- Rival teams/players (+40 points)
- Athlete popularity (follower count)
- Recent news mentions (+30 points)
- Interaction history
```

## 📁 Project Structure

```
football-gossip-bot/
├── src/
│   ├── main.py                 # Main application
│   ├── tracker.py              # Follow/unfollow tracker
│   ├── tweet_generator.py      # Tweet content generator
│   ├── database.py             # Database operations
│   ├── drama_scorer.py         # Drama calculation
│   └── config.py               # Configuration
├── data/
│   ├── athletes.json           # List of tracked athletes
│   └── gossip.db              # SQLite database
├── tests/
│   └── test_tracker.py
├── .env.example
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## 🎯 Tracked Athletes

Currently tracking 50+ top football players including:
- ⭐ Cristiano Ronaldo (@Cristiano)
- ⭐ Lionel Messi (@TeamMessi)
- ⭐ Kylian Mbappé (@KMbappe)
- ⭐ Erling Haaland (@ErlingHaaland)
- And many more...

See `data/athletes.json` for full list.

## 💰 Monetization

- 📢 Sponsored tweets
- 🔗 Affiliate links (jerseys, betting)
- 💎 Premium alerts (Telegram/Discord)
- 📊 API access for data

## ⚠️ Important Notes

### Twitter API Limits
- Free tier: Limited (not recommended)
- Basic ($100/mo): 10,000 tweets/month
- Recommended: Start with 20-30 athletes

### Legal & Ethical
- ✅ All data is public
- ✅ No privacy violations
- ⚠️ Respect rate limits
- ⚠️ Follow Twitter ToS

## 🛠️ Development

```bash
# Run tests
pytest tests/

# Format code
black src/

# Lint
flake8 src/
```

## 📈 Roadmap

- [x] Basic follow/unfollow tracking
- [x] Auto-tweet generation
- [ ] Instagram integration
- [ ] Viral tweet detection
- [ ] Betting odds integration
- [ ] Multi-language support
- [ ] Web dashboard
- [ ] Premium tier with Telegram bot

## 🤝 Contributing

Contributions welcome! Please read CONTRIBUTING.md first.

## 📄 License

MIT License - see LICENSE file

## 🙏 Credits

Created by [@erdmkk](https://github.com/erdmkk)

---

**Disclaimer**: This bot is for educational and entertainment purposes. Always respect Twitter's Terms of Service and API usage policies.