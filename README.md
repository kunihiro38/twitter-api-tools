# twitter-api-tools

## 概要

- Twitterの全ツイート一括削除
- twitter API ver.1

### 1. image の構築とコンテナ起動
```
docker-compose up -d --build
```
### 2. コンテナへ接続
```
% docker exec -it python3_for_twt /bin/bash
# ls
main.py
```
### 3. プログラムの実行
```
# python main.py
```
### 4. コンテナの削除
```
% docker-compose down
```

## 参考

https://zenn.dev/shomtsm/articles/52864a4b7b5eec