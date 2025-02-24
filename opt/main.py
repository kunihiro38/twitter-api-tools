
import csv
import json
import os
import sys
import time
import requests
from dotenv import load_dotenv
from requests_oauthlib import OAuth1

# .envを読み込む
load_dotenv()

API_KEY = os.environ['API_KEY']
API_SECRET_KEY = os.environ['API_SECRET_KEY']
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
ACCESS_TOKEN_SECRET = os.environ['ACCESS_TOKEN_SECRET']


# OAuth認証
auth = OAuth1(API_KEY, API_SECRET_KEY, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

# アーカイブデータからツイートIDを抽出する関数
def extract_ids_from_archive(file_path, action_items):
    '''
    引数:
        archive_file_path (str): アーカイブのパス
    '''
    extracted_ids_list = []
    with open(file_path, 'r', encoding='utf-8') as file:
        data = file.read()
        data = data.replace(f'window.YTD.{action_items}.part0 = ', '')
        tweets_data = json.loads(data)

        if action_items == "tweets":
            for tweet in tweets_data:
                tweet_id = tweet['tweet']['id_str']
                extracted_ids_list.append(tweet_id)

        elif action_items == "like":
            for like in tweets_data:
                like_id = like["like"]["tweetId"]
                extracted_ids_list.append(like_id)

    return extracted_ids_list


# ツイートを削除する関数
def delete_twitter_content(extracted_ids, url_endpoint):
    '''
    引数:
        extracted_tweet_ids (list): 削除対象のツイートIDのリスト
    '''
    deleted_count = 0
    failed_count = 0
    for tweet_id in extracted_ids:
        del_response = requests.post(url_endpoint + f"{tweet_id}.json", auth=auth)
        if del_response.status_code == 200:
            deleted_count += 1
            print(f"Deleted tweet ID: {tweet_id}, deleted count: {deleted_count}")
        elif del_response.status_code == 429:
            print("Rate limit exceeded. Waiting for 15 minutes...")
            break
        elif del_response.status_code == 404:
            failed_count += 1
            print(
                f"Failed to delete tweet ID: {tweet_id}, "
                f"Already deleted or does not exist."
                f"Status Code: {del_response.status_code}, "
                f"failed count: {failed_count}"
            )
        elif del_response.status_code == 403:
            response_data = del_response.json()
            # print(response_data)
            if "errors" in response_data:
                for error in response_data["errors"]:
                    if error["code"] == 453:
                        print(error["message"], "Elevated 以上のアクセス権が必要（無料の Essential では不可）")
                        sys.exit() # 強制終了
            failed_count += 1
            print(
                f"Failed to delete tweet ID: {tweet_id}, "
                f"Forbidden."
                f"Status Code: {del_response.status_code}, "
                f"failed count: {failed_count}"
            )
        else:
            print(del_response.status_code)

# 特定のユーザーのツイートを取得する
def get_user_tweets(screen_name, max_tweets=3200):
    url = "https://api.twitter.com/1.1/statuses/user_timeline.json"
    params = {
        "screen_name": screen_name,
        "count": 200,
        "tweet_mode": "extended"
    }

    all_tweets = []
    while len(all_tweets) < max_tweets:
        response = requests.get(url, auth=auth, params=params)

        if response.status_code == 200:
            tweets = response.json()
            if not tweets:
                break

            all_tweets.extend(tweets)
            last_tweet_id = tweets[-1]["id"] - 1
            params["max_id"] = last_tweet_id
        else:
            print("Error", response.json())
            break

        time.sleep() # API制限を回避するために少し待機
    return all_tweets[:max_tweets]

def save_tweets_to_csv(tweets, filename="tweets.csv"):
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Created At", "Tweet"])

        for tweet in tweets:
            writer.writerow([tweet["created_at"], tweet["full_text"]])

    print(f"Saved {len(tweets)} tweets to {filename}")


# ツイート全消しの実行
# action_items = "tweets"
# archive_tweets_file_path = 'data/tweets.js'
# tweet_ids = extract_ids_from_archive(archive_tweets_file_path, action_items)
# url_delete_tweet_endpoint = "https://api.twitter.com/1.1/statuses/destroy/"
# delete_twitter_content(tweet_ids, url_delete_tweet_endpoint)

# いいね全消しの実行
# action_items = "like"
# archive_likes_file_path = 'data/like.js'
# like_ids = extract_ids_from_archive(archive_likes_file_path, action_items)
# url_delete_like_endpoint = "https://api.twitter.com/1.1/favorites/destroy/"
# delete_twitter_content(like_ids, url_delete_like_endpoint)

# 特定のユーザーのツイートを取得する
screen_name = "iiGIANT"

# 実行
tweets = get_user_tweets(screen_name)
save_tweets_to_csv(tweets)
