from .constants import DIR_PATH


def make_raw_content_filename(paper: dict):
    return f"{DIR_PATH}/raw_{paper['id'].replace('/', '_')}.pdf"


def make_clean_content_filename(raw_content_filename: str):
    return f"{DIR_PATH}/scraped_{raw_content_filename}.txt"
