import pandas as pd
from google_play_scraper import reviews, Sort
import datetime
from tqdm import tqdm
import time

def scrape_playstore_reviews(app_id, start_year=2025, lang='id', country='id'):
    """
    Scrape Google Play Store reviews for a specific app ID from a given year onwards.
    """
    print(f"Starting review scraping for App ID: {app_id}")
    print(f"Target: Reviews from {start_year} onwards...")

    all_reviews = []
    continuation_token = None
    
    # Target date variable
    target_date = datetime.datetime(start_year, 1, 1)
    
    # We use a loop with continuation tokens to fetch reviews progressively
    # Sorting by NEWEST to easily filter by date and stop when we hit old dates
    with tqdm(desc="Fetching reviews") as pbar:
        while True:
            # Fetch a batch of reviews
            result, continuation_token = reviews(
                app_id,
                lang=lang, 
                country=country, 
                sort=Sort.NEWEST, 
                count=1000, # Max count per request
                continuation_token=continuation_token
            )
            
            if not result:
                break
                
            # Filter and process reviews
            reached_old_reviews = False
            valid_reviews_in_batch = 0
            
            for r in result:
                review_date = r['at']
                
                # Check if the review is from our target year or newer
                if review_date >= target_date:
                    all_reviews.append({
                        'reviewId': r['reviewId'],
                        'userName': r['userName'],
                        'content': r['content'],
                        'score': r['score'],
                        'thumbsUpCount': r['thumbsUpCount'],
                        'reviewCreatedVersion': r['reviewCreatedVersion'],
                        'at': review_date,
                        'replyContent': r['replyContent'],
                        'repliedAt': r['repliedAt']
                    })
                    valid_reviews_in_batch += 1
                else:
                    # Since it's sorted by NEWEST, once we see a date older than our target,
                    # we know all subsequent reviews will be older too.
                    reached_old_reviews = True
                    break
            
            pbar.update(valid_reviews_in_batch)
            
            # Stop if we reached older reviews or if there's no more token
            if reached_old_reviews or continuation_token is None:
                break
                
            # Slight delay to be polite to the server
            time.sleep(1)

    print(f"\nDone! Successfully collected {len(all_reviews)} reviews from {start_year}.")
    
    # Save to DataFrame and CSV
    if all_reviews:
        df = pd.DataFrame(all_reviews)
        filename = f"playstore_reviews_{app_id.replace('.', '_')}_{start_year}.csv"
        df.to_csv(filename, index=False)
        print(f"Data saved to: {filename}")
        return df
    else:
        print("No reviews found for the given criteria.")
        return None

if __name__ == "__main__":
    # Target App: Example (WhatsApp)
    TARGET_APP_ID = 'com.whatsapp'
    START_YEAR = datetime.datetime.now().year - 1
    
    df_result = scrape_playstore_reviews(TARGET_APP_ID, START_YEAR)
    
    if df_result is not None:
        print("\nPreview data:")
        print(df_result[['userName', 'score', 'at', 'content']].head())
