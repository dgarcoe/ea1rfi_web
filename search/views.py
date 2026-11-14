from django.core.paginator import Paginator
from django.shortcuts import render
from wagtail.models import Page, Site

def search(request):
    query = request.GET.get('query', '').strip()[:200]
    site = Site.find_for_request(request)
    results = Page.objects.none()
    if query and site:
        results = Page.objects.live().public().descendant_of(site.root_page).search(query)
    return render(request, 'search/search.html', {'query': query, 'results': Paginator(results, 12).get_page(request.GET.get('page'))})
