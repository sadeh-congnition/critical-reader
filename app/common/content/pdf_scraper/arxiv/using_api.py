import PyPDF2

from common.content.utils import make_clean_content_filename, make_raw_content_filename


def scrape_pdf_using_pypdf2(paper: dict) -> str:
    text = []
    with open(
        f"{make_clean_content_filename(make_raw_content_filename(paper))}", "r"
    ) as f:
        pdf = PyPDF2.PdfReader(f)
        for page in range(len(pdf.pages)):
            page_obj = pdf.pages[page]
            text.append(page_obj.extract_text())
        text = "\n".join(text)
    return text
