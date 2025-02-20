import json
import os
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
def extract_tweet_ids_from_archive(file_path):
    '''
    引数:
        archive_file_path (str): アーカイブのパス
    '''
    extracted_tweet_ids_list = []
    with open(file_path, 'r', encoding='utf-8') as file:
        data = file.read()
        data = data.replace('window.YTD.tweets.part0 = ', '')
        tweets_data = json.loads(data)

        for tweet in tweets_data:
            tweet_id = tweet['tweet']['id_str']
            extracted_tweet_ids_list.append(tweet_id)
    return extracted_tweet_ids_list

# ツイートを削除する関数
def delete_tweets(extracted_tweet_ids: list) -> None:
    '''
    引数:
        extracted_tweet_ids (list): 削除対象のツイートIDのリスト
    '''
    url_delete_tweet = "https://api.twitter.com/1.1/statuses/destroy/"
    deleted_count = 0
    failed_count = 0
    for tweet_id in extracted_tweet_ids:
        del_response = requests.post(url_delete_tweet + f"{tweet_id}.json", auth=auth)
        if del_response.status_code == 200:
            deleted_count += 1
            print(f"Deleted tweet ID: {tweet_id}, deleted count: {deleted_count}")
        else:
            failed_count += 1
            print(f"Failed to delete tweet ID: {tweet_id},\
                    Status Code: {del_response.status_code},\
                    failed count: {failed_count}")

# 実行
archive_file_path = 'tweets.js' # アーカイブファイルのパスを指定
tweet_ids = extract_tweet_ids_from_archive(archive_file_path)
delete_tweets(tweet_ids)
