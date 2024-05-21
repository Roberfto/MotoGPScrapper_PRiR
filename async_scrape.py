import asyncio
import aiohttp
from bs4 import BeautifulSoup
from pymongo import MongoClient
import os
from concurrent.futures import ProcessPoolExecutor
import multiprocessing

# Ładowanie zmiennej środowiskowej
mongo_uri = os.getenv('MONGO_URI')
client = MongoClient(mongo_uri)
db = client['Projekt']
collection = db['scraper']


async def fetch(session, url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        async with session.get(url, headers=headers) as response:
            response.raise_for_status()
            result = await response.text()
            print(f"Data fetched from {url}: {result[:500]}...")
            return result
    except Exception as e:
        print(f"Failed to fetch data from {url}: {e}")
        return None


def process_data(html):
    if html is None:
        return []
    base_url = "https://www.motogp.com"
    soup = BeautifulSoup(html, 'html.parser')
    months = soup.find_all('div', class_='calendar-listings__month')
    data = []
    for month in months:
        month_name = month.find('div', class_='calendar-listings__month-title').text.strip()
        events = []
        for event in month.find_all('li', class_='calendar-listing__event-container'):
            event_name = event.find('div', class_='calendar-listing__title').text.strip()
            event_url = event.find('a')['href']
            event_full_url = base_url + event_url if not event_url.startswith('http') else event_url
            track_layout_div = event.find('div', class_='calendar-listing__track-layout js-circuit-track')
            event_track_image_url = track_layout_div.find('img')['src'] if track_layout_div and track_layout_div.find(
                'img') else None

            # Extract new additional image (calendar-listing_flag)
            additional_image_url = None
            flag_img_tag = event.find('img', class_='calendar-listing_flag')
            if flag_img_tag:
                additional_image_url = flag_img_tag['src']

            date_start_day = event.find('div', class_='calendar-listing__date-start-day').text.strip()
            date_start_month = event.find('div', class_='calendar-listing__date-start-month').text.strip()
            event_date = f"{date_start_day} {date_start_month}"
            events.append({
                'name': event_name,
                'url': event_full_url,
                'track_image_url': event_track_image_url,
                'additional_image_url': additional_image_url,
                'date': event_date
            })
            print(
                f"Extracted: {event_name}, Track Image URL: {event_track_image_url}, Flag Image URL: {additional_image_url}")
        data.append({
            'month': month_name,
            'events': events
        })
    return data


def save_to_db(data):
    if not data:
        print("No data to save")
        return
    for month_data in data:
        for event in month_data['events']:
            existing_event = collection.find_one({'url': event['url']})
            if not existing_event:
                try:
                    result = collection.insert_one({
                        'name': event['name'],
                        'url': event['url'],
                        'track_image_url': event['track_image_url'],
                        'additional_image_url': event['additional_image_url'],
                        'date': event['date']
                    })
                    print(f"Data saved successfully, inserted_id: {result.inserted_id}")
                except Exception as e:
                    print(f"Failed to save data: {e}")
            else:
                collection.update_one(
                    {'_id': existing_event['_id']},
                    {'$set': {
                        'name': event['name'],
                        'track_image_url': event['track_image_url'],
                        'additional_image_url': event['additional_image_url'],
                        'date': event['date']
                    }}
                )
                print(f"Data updated for event: {event['name']}, Flag Image URL: {event['additional_image_url']}")



async def main(urls):
    async with aiohttp.ClientSession() as session:
        htmls = await asyncio.gather(*(fetch(session, url) for url in urls))

    with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
        processed_data = list(executor.map(process_data, htmls))

    for data in processed_data:
        save_to_db(data)


if __name__ == "__main__":
    asyncio.run(main(["https://www.motogp.com/en/calendar"]))
