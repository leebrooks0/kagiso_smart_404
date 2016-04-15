import re

from wagtail.wagtailcore.models import Page


def get_instant_redirect(slug, root_page):
    cleaned_slug = re.match('/.*/(.*)/', slug).group(1)

    try:
        return Page.objects.descendant_of(root_page).get(
            slug=cleaned_slug)
    except (Page.MultipleObjectsReturned, Page.DoesNotExist):
        return None


def suggest_page_from_misspelled_slug(slug, root_page):
    sql = '''SELECT p.*, similarity(slug, %(slug)s) AS similarity
             FROM wagtailcore_page p
             WHERE slug %% %(slug)s
             ORDER BY similarity DESC
             '''
    page = Page.objects.raw(sql, {'slug': slug})
    suggested_pages = None

    # page is currently a RawQuerySet...
    if list(page) and root_page in page[0].get_ancestors().specific():
        suggested_pages = list(page)

    return suggested_pages
