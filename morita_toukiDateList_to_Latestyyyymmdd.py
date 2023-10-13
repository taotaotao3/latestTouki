import re
import pandas as pd

def detect(target_list = ["令和４年７月４日登記", "2023年6月24日", "Some text without a date"]):
    comparing_list = []
    # 元号とその開始年を定義
    ERA_START_YEARS = {
        '明治': 1868,
        '大正': 1912,
        '昭和': 1926,
        '平成': 1989,  # Heisei
        '令和': 2019,  # Reiwa
        # 必要に応じて他の元号を追加
    }

    def convert_japanese_era_to_ad(year, era_name):
        """
        日本の元号と年を西暦に変換する。
        """
        start_year = ERA_START_YEARS.get(era_name)
        if start_year is None:
            return None  # 未知の元号
        return start_year + year - 1

    date_patterns = [
        re.compile(r'(平成|令和|昭和)([0-9０-９]+)年\s*([0-9０-９]+)月\s*([0-9０-９]+)日'),  # 元号を含む日付、スペースを許容
        re.compile(r'(\d{4})年(\d{1,2})月(\d{1,2})日'),  # yyyy年mm月dd日
        re.compile(r'(\d{4})/(\d{1,2})/(\d{1,2})'),  # yyyy/mm/dd
        re.compile(r'(平成|令和|昭和)([0-9０-９]+)年法務省令第[0-9０-９]+号.*?の規定により.*?(平成|令和|昭和)([0-9０-９]+)年.*?([0-9０-９]+)\r\n月.*?([0-9０-９]+)日', re.DOTALL),  # 改行とテキストを許容
        # 必要に応じて他のパターンを追加
    ]

    exceptions = []

    for index, content in enumerate(target_list, start=1):
        date_found = False
        content_no_newline = content.replace('\n', '').replace('\r', '')  # 改行を削除
        for pattern in date_patterns:
            match = pattern.search(content_no_newline)
            if match:
                groups = match.groups()

                # 元号を含む日付の処理
                if len(groups) == 4 and groups[0] in ERA_START_YEARS:
                    era_name, year, month, day = groups
                    # 全角数字を半角数字に変換
                    year = int(year.translate(str.maketrans('０-９', '0-9')))
                    month = int(month.translate(str.maketrans('０-９', '0-9')))
                    day = int(day.translate(str.maketrans('０-９', '0-9')))

                    year_ad = convert_japanese_era_to_ad(year, era_name)
                    if year_ad:
                        date_str = f"{year_ad:04d}-{month:02d}-{day:02d}"
                        try:
                            standardized_date = pd.to_datetime(date_str).strftime('%Y%m%d')
                            date_found = True
                            break
                        except ValueError:
                            pass  # 解析エラーが発生した場合は例外リストに追加するため、passします。
                    else:
                        pass  # 未知の元号の場合も例外リストに追加するため、passします。

                # その他の日付フォーマットの処理
                else:
                    try:
                        date_str = '-'.join(groups)  # '年'、'月'、'日'または'/'で区切られた部分を結合
                        standardized_date = pd.to_datetime(date_str).strftime('%Y%m%d')
                        comparing_list.append(standardized_date)

                        date_found = True
                        break
                    except ValueError:
                        pass  # 解析エラーが発生した場合は例外リストに追加するため、pass

        if not date_found:
            exceptions.append((index, content))  # 日付が見つからない、または解析エラーが発生した場合

    # 例外を出力
    for line_number, exception in exceptions:
        print(f"行{line_number}: {exception}")

    # 文字列としての日付をpandasのTimestampオブジェクトに変換
    dates = [pd.Timestamp(date) for date in comparing_list]
    # 最も新しい日付を取得
    most_recent_date = max(dates)
    print(most_recent_date.strftime('%Y%m%d'))  # YYYYMMDD形式で出力
    return most_recent_date

if __name__ == "__main__":
    detect()