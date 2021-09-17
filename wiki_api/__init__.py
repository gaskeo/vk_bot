import wikipediaapi
import random

wiki_wiki = wikipediaapi.Wikipedia('ar')
wikipediaapi.log.propagate = False


def get_random_funny_wiki_page() -> str:
    """
    get random wiki page header from category humor
    :return: random wiki page header

    """
    pages = wiki_wiki.page("Category:فكاهة")
    return random.choice(list(pages.categorymembers.keys()))
