from django.core.paginator import Paginator
from django.db import models
from django.utils import timezone
from modelcluster.fields import ParentalKey
from modelcluster.tags import ClusterTaggableManager
from taggit.models import TaggedItemBase
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page
from wagtail.search import index

FEATURES = ['h2', 'h3', 'bold', 'italic', 'ol', 'ul', 'hr', 'link', 'document-link', 'image', 'embed', 'blockquote']

class HomePage(Page):
    headline = models.CharField('Titular', max_length=160, default='Ondas, lugares e historias.')
    introduction = models.TextField('Presentación', blank=True)
    hero_image = models.ForeignKey('wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL, related_name='+', verbose_name='Imagen de portada')
    content_panels = Page.content_panels + [FieldPanel('headline'), FieldPanel('introduction'), FieldPanel('hero_image')]
    subpage_types = ['home.AboutPage', 'home.SectionPage']
    max_count = 1

    def get_context(self, request):
        context = super().get_context(request)
        context['sections'] = SectionPage.objects.child_of(self).live().public()
        context['latest'] = ArticlePage.objects.descendant_of(self).live().public().order_by('-date', '-first_published_at')[:6]
        return context

class AboutPage(Page):
    introduction = models.TextField('Entradilla', blank=True)
    body = RichTextField('Contenido', features=FEATURES, blank=True)
    portrait = models.ForeignKey('wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL, related_name='+', verbose_name='Retrato')
    content_panels = Page.content_panels + [FieldPanel('introduction'), FieldPanel('portrait'), FieldPanel('body')]
    parent_page_types = ['home.HomePage']
    subpage_types = []

class SectionPage(Page):
    kind = models.CharField('Sección', max_length=20, choices=[('radio', 'Radioafición'), ('history', 'Historia y patrimonio')])
    introduction = models.TextField('Presentación', blank=True)
    content_panels = Page.content_panels + [FieldPanel('kind'), FieldPanel('introduction')]
    parent_page_types = ['home.HomePage']
    subpage_types = ['home.ArticlePage']

    def get_context(self, request):
        context = super().get_context(request)
        articles = ArticlePage.objects.child_of(self).live().public().order_by('-date', '-first_published_at')
        region = request.GET.get('region', '')
        tag = request.GET.get('tag', '')
        if region in dict(ArticlePage.REGIONS):
            articles = articles.filter(region=region)
        if tag:
            articles = articles.filter(tags__slug=tag)
        context.update(articles=Paginator(articles, 9).get_page(request.GET.get('page')), region=region, tag=tag)
        return context

class ArticleTag(TaggedItemBase):
    content_object = ParentalKey('home.ArticlePage', on_delete=models.CASCADE, related_name='tagged_items')

class ArticlePage(Page):
    REGIONS = [('galicia', 'Galicia'), ('aldearrubia', 'Aldearrubia'), ('other', 'Otros lugares')]
    date = models.DateField('Fecha del artículo', default=timezone.now)
    introduction = models.TextField('Entradilla', max_length=500)
    cover = models.ForeignKey('wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL, related_name='+', verbose_name='Imagen de portada')
    caption = models.CharField('Pie y crédito de la imagen', max_length=300, blank=True)
    body = RichTextField('Artículo', features=FEATURES)
    region = models.CharField('Zona (historia)', max_length=20, choices=REGIONS, blank=True)
    location = models.CharField('Lugar', max_length=180, blank=True)
    sources = RichTextField('Fuentes y bibliografía', features=FEATURES, blank=True)
    tags = ClusterTaggableManager(through=ArticleTag, blank=True, verbose_name='Etiquetas')
    content_panels = Page.content_panels + [FieldPanel('date'), FieldPanel('introduction'), FieldPanel('cover'), FieldPanel('caption'), FieldPanel('body'), FieldPanel('region'), FieldPanel('location'), FieldPanel('sources'), FieldPanel('tags')]
    search_fields = Page.search_fields + [index.SearchField('introduction'), index.SearchField('body'), index.SearchField('location'), index.SearchField('sources')]
    parent_page_types = ['home.SectionPage']
    subpage_types = []

    def get_context(self, request):
        context = super().get_context(request)
        context['section'] = self.get_parent().specific
        context['related'] = ArticlePage.objects.sibling_of(self).live().public().exclude(pk=self.pk).order_by('-date')[:3]
        return context
