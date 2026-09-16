from dataclasses import dataclass

@dataclass
class Page:
    number: int
    word_count: int

@dataclass
class Chapter:
    title: str
    pages: list

@dataclass
class Book:
    title: str
    chapters: list


def build_chapter(chapter_dict):
    pages = []
    for page_dict in chapter_dict["pages"]:
        curr_page = Page(page_dict["number"], page_dict["word_count"])
        pages.append(curr_page)
        curr_chapter = Chapter(chapter_dict["title"], pages)
    return curr_chapter

def build_book(raw_data):
    chapters = []
    for chapter_dict in raw_data["chapters"]:
        curr_chapter = build_chapter(chapter_dict)
        chapters.append(curr_chapter)
        curr_book = Book(raw_data["title"], chapters)
    return curr_book 

raw_data = {
    "title": "Example Book",
    "chapters": [
        {"title": "Intro", "pages": [{"number": 1, "word_count": 250}, {"number": 2, "word_count": 300}]},
        {"title": "Middle", "pages": [{"number": 3, "word_count": 400}]},
    ]
}


result = build_book(raw_data)
print(result)
print(result.chapters[0].pages[0].word_count)  # Output: 250