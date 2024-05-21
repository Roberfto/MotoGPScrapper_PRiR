from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import asyncio
from async_scrape import main

load_dotenv()

app = Flask(__name__)
mongo_uri = os.getenv('MONGO_URI')

#Mongo Komunikacja ustawienie bazy danych
try:
    client = MongoClient(mongo_uri)
    db = client['Projekt']
    collection = db['scraper']
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        urls = ['https://www.motogp.com/en/calendar']
        asyncio.run(main(urls))
        return redirect(url_for('results'))
    return render_template('index.html')


@app.route('/results')
def results():
    try:
        stories = list(collection.find())
        base_url = "https://www.motogp.com" # Jezeli w linku barkuje dodaje ten link
        for story in stories:
            if not story['url'].startswith(base_url):
                story['url'] = base_url + story['url']

        if not stories:
            return render_template('results.html', message="No stories found.")

        return render_template('results.html', stories=stories)
    except Exception as e:
        print(f"Error retrieving data from MongoDB: {e}")
        return render_template('results.html', message="Error accessing the database.")


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
