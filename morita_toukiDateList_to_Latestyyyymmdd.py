import re
import pandas as pd

def detect(target_list=["令和４年７月４日登記", "2023年6月24日", "Some text without a date"]):
    comparing_list = []
    index_list = []  
    ERA_START_YEARS = {
        '明治': 1868,
        '大正': 1912,
        '昭和': 1926,
        '平成': 1989,
        '令和': 2019,
    }

    def convert_japanese_era_to_ad(year, era_name):
        start_year = ERA_START_YEARS.get(era_name)
        if start_year is None:
            return None
        return start_year + year - 1

    date_patterns = [
        re.compile(r'(平成|令和|昭和)([0-9０-９]+)年\s*([0-9０-９]+)月\s*([0-9０-９]+)日'),
        re.compile(r'(\d{4})年(\d{1,2})月(\d{1,2})日'),
        re.compile(r'(\d{4})/(\d{1,2})/(\d{1,2})'),
        re.compile(r'(平成|令和|昭和)([0-9０-９]+)年法務省令第[0-9０-９]+号.*?の規定により.*?(平成|令和|昭和)([0-9０-９]+)年.*?([0-9０-９]+)月.*?([0-9０-９]+)日', re.DOTALL),
    ]

    exceptions = []

    for index, content in enumerate(target_list, start=1):
        date_found = False
        content_no_newline = content.replace('\n', '').replace('\r', '')
        for pattern in date_patterns:
            match = pattern.search(content_no_newline)
            if match:
                groups = match.groups()

                if len(groups) == 4 and groups[0] in ERA_START_YEARS:
                    era_name, year, month, day = groups
                    year = int(year.translate(str.maketrans('０-９', '0-9')))
                    month = int(month.translate(str.maketrans('０-９', '0-9')))
                    day = int(day.translate(str.maketrans('０-９', '0-9')))

                    year_ad = convert_japanese_era_to_ad(year, era_name)
                    if year_ad:
                        date_str = f"{year_ad:04d}-{month:02d}-{day:02d}"
                        try:
                            standardized_date = pd.to_datetime(date_str).strftime('%Y%m%d')
                            comparing_list.append(standardized_date)
                            index_list.append(index)
                            date_found = True
                            break
                        except ValueError as e:
                            exceptions.append((index, str(e)))
                            continue

                else:
                    try:
                        date_str = '-'.join(groups)
                        standardized_date = pd.to_datetime(date_str).strftime('%Y%m%d')
                        comparing_list.append(standardized_date)
                        index_list.append(index)
                        date_found = True
                        break
                    except ValueError as e:
                        exceptions.append((index, str(e)))
                        continue

        if not date_found:
            exceptions.append((index, content))

    # 例外の出力をここで行います
    for line_number, exception in exceptions:
        print(f"A case occurred where date conversion was not possible. list num:{line_number}: {exception}")

    if comparing_list:  # comparing_listが空でないことを確認
        dates = [pd.Timestamp(date) for date in comparing_list]
        most_recent_date = max(dates)
        most_recent_index = index_list[dates.index(most_recent_date)]
        return most_recent_index, most_recent_date
    else:
        return None, None  # 日付が一つも解析できなかった場合

if __name__ == "__main__":
    index, most_recent_date = detect()
    if most_recent_date:  # 最新の日付があることを確認
        print(f"The most recent date is at index {index}, date: {most_recent_date.strftime('%Y%m%d')}")
    else:
        print("No valid dates were found.")
