import arxiv
import re
import requests

from common.utils import make_raw_content_filename


def search_arxiv(search_term: str):
    search = arxiv.Search(
        query="cat:cs.AI", max_results=100, sort_by=arxiv.SortCriterion.SubmittedDate
    )
    search_result = list(search.results())
    return search_result


def process_search_results(search_result):
    dataset = []
    for p in search_result:
        paper_dict = {}
        for l in p.links:
            if "pdf" in l.href:
                paper_dict["pdf_url"] = l.href
        if not paper_dict.get("pdf_url"):
            raise ValueError()
        paper_dict["id"] = p.entry_id
        paper_dict["pdf_url_cleaned"] = re.sub(r"v\d+$", "", paper_dict["pdf_url"])
        paper_dict["published_date"] = p.published
        paper_dict["title"] = p.title
        paper_dict["summary"] = p.summary
        paper_dict["pdf_download_url"] = (
            "https://export." + paper_dict["pdf_url_cleaned"].split("://")[-1]
        )
        dataset.append(paper_dict)
    return dataset


def download_and_(papers):
    for p in papers:
        r = requests.get(p["pdf_download_url"])
        with open(f"{make_raw_content_filename(p)}", "wb") as f:
            f.write(r.content)
