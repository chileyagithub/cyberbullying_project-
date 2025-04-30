import os
import django
from dotenv import load_dotenv

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cyberbullying.settings')
django.setup()

from django.conf import settings
from detection_system.utils import notify_admin
from detection_system.models import Message

import requests
import torch
from transformers import pipeline
import tweepy

# Load environment variables from .env
load_dotenv()
TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')

print("Bearer Token:", TWITTER_BEARER_TOKEN)

PERSPECTIVE_KEY = os.getenv('PERSPECTIVE_API_KEY')
TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')

# Initialize toxic BERT classifier
classifier = pipeline('text-classification', model='unitary/toxic-bert')

BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAK2V0wEAAAAAPIwFW%2B" \
"mLonk3FoIf7Chfkh5miZI%3DVwq9f7ejI6vvKUhYx6jwsNtUD2T2ufnKQAk2efxJTA2EORGO0J"

class MyStream(tweepy.StreamingClient):
    def on_tweet(self, tweet):
        print(tweet.text)

stream = MyStream(bearer_token=BEARER_TOKEN)
stream.filter()

# Analyze text using Google's Perspective API
def analyze_toxicity_perspective(text):
    url = 'https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze'
    payload = {
        'comment': {'text': text},
        'languages': ['en'],
        'requestedAttributes': {'TOXICITY': {}}
    }
    try:
        resp = requests.post(url, params={'key': PERSPECTIVE_KEY}, json=payload, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            score = data.get('attributeScores', {}).get('TOXICITY', {}).get('summaryScore', {}).get('value')
            return score
    except Exception as e:
        print(f"[Perspective API Error] {e}")
    return None

# Check toxicity using both Perspective and BERT
def check_toxicity(text):
    score = analyze_toxicity_perspective(text)
    is_toxic_perspective = score is not None and score > 0.7
    result = classifier(text)[0]
    is_toxic_bert = result['label'].lower() == 'toxic'
    return is_toxic_perspective or is_toxic_bert, score

# Twitter stream client
class ToxicStream(tweepy.StreamingClient):
    def on_tweet(self, tweet):
        try:
            text = tweet.text
            is_toxic, score = check_toxicity(text)
            Message.objects.create(text=text, is_toxic=is_toxic)
            if is_toxic:
                notify_admin(text)
            print(f"[{'TOXIC' if is_toxic else 'SAFE'}] {text[:50]}...")
        except Exception as e:
            print(f"[Tweet Error] {e}")

    def on_request_error(self, status_code):
        print(f"[Stream Error] Status code: {status_code}")
        return False  # Stop stream on error


if __name__ == '__main__':
    if not TWITTER_BEARER_TOKEN:
        print("TWITTER_BEARER_TOKEN not found in environment variables.")
        exit(1)

    stream = ToxicStream(bearer_token=TWITTER_BEARER_TOKEN)

    # Remove old stream rules if any
    existing_rules = stream.get_rules().data
    if existing_rules:
        rule_ids = [rule.id for rule in existing_rules]
        stream.delete_rules(rule_ids)

    # Add new rule
    stream.add_rules(tweepy.StreamRule("bullying OR hate OR insult OR abuse"))

    print(" Twitter stream is starting...")
    stream.filter(tweet_fields=['text'])
