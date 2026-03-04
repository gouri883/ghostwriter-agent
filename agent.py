import os
import feedparser
from dotenv import load_dotenv
from groq import Groq
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

# Load environment variables
load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")

client = Groq(api_key=API_KEY)

print("Fetching tech news...\n")

# TechCrunch RSS
feed = feedparser.parse("https://feeds.feedburner.com/TechCrunch")

headlines = []

for entry in feed.entries[:5]:
    headlines.append(entry.title)

for h in headlines:
    print("-", h)

print("\nGenerating article with AI...\n")

prompt = f"""
Write a short tech news article based on these headlines:

{headlines}

Choose the most interesting topic and write a 200 word article.
"""

response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {"role": "user", "content": prompt}
    ]
)

article = response.choices[0].message.content

print("Generated Article:\n")
print(article)

# ------------------------
# SAVE ARTICLE
# ------------------------

date = datetime.now().strftime("%Y-%m-%d")

if not os.path.exists("articles"):
    os.makedirs("articles")

file_path = f"articles/{date}.txt"

with open(file_path, "w", encoding="utf-8") as f:
    f.write(article)

print("\nArticle saved to:", file_path)

# ------------------------
# SEND EMAIL
# ------------------------

subject = "Daily AI Tech News"

msg = MIMEText(article)
msg["Subject"] = subject
msg["From"] = EMAIL_SENDER
msg["To"] = EMAIL_RECEIVER

server = smtplib.SMTP("smtp.gmail.com", 587)
server.starttls()

server.login(EMAIL_SENDER, EMAIL_PASSWORD)

server.send_message(msg)

server.quit()

print("\nEmail sent successfully!")