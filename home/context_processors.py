from wagtail.models import Site

def navigation(request):
    site = Site.find_for_request(request)
    root = site.root_page if site else None
    return {'site_root': root, 'navigation': root.get_children().live().public().in_menu() if root else []}
