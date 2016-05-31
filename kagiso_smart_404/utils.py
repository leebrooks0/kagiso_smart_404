from wagtail.wagtailcore.models import Page


def page_slug(slug):
    # Full slug might be /news/sports/somesportsarticle/
    # The page slug is therefore `somesportsarticle`
    slugs = slug.split('/')
    print(slugs)

    # Remove all empty strings
    # '/news/article' => ['', 'news', 'article', '']
    slugs = list(filter(None, slugs))

    page_slug = slugs[-1]
    return page_slug


def slug_matches_one_page_exactly(slug, root_page):
    slug = page_slug(slug)
    try:
        result = Page.objects.descendant_of(root_page).get(
            slug=slug,
            live=True,
            first_published_at__isnull=False
        )
        return result
    except (Page.MultipleObjectsReturned, Page.DoesNotExist):
        return None


def suggest_page_from_misspelled_slug(slug, root_page):
    root_path = root_page.path
    root_path_len = len(root_path)

    sql = '''SELECT p.*, similarity(slug, %(slug)s) AS similarity
             FROM wagtailcore_page p
             WHERE live = true
                 AND first_published_at IS NOT NULL
                 AND substring(path FOR %(root_path_len)s) = %(root_path)s
                 AND slug %% %(slug)s
             ORDER BY similarity DESC
    '''
    data = {
        'slug': slug,
        'root_path': root_path,
        'root_path_len': root_path_len
    }
    suggested_pages = list(Page.objects.raw(sql, data))  # RawQuerySet...
    suggested_pages = [page.specific for page in suggested_pages]

    return suggested_pages[:3]
