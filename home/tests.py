from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from wagtail.models import Page, PageViewRestriction
from home.models import HomePage, SectionPage, ArticlePage

class PersonalSiteTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('seed_site', verbosity=0)
        cls.home = HomePage.objects.first()
        cls.history = SectionPage.objects.get(kind='history')
        cls.radio = SectionPage.objects.get(kind='radio')
        cls.galicia = cls.history.add_child(instance=ArticlePage(title='Historia de Ansemil', slug='ansemil', introduction='Notas sobre el monasterio.', body='<p>Documentación y patrimonio.</p>', region='galicia'))
        cls.galicia.save_revision().publish()
        cls.aldearrubia = cls.history.add_child(instance=ArticlePage(title='Archivo de Aldearrubia', slug='archivo', introduction='Fuentes locales.', body='<p>Memoria documental.</p>', region='aldearrubia'))
        cls.aldearrubia.save_revision().publish()
        cls.draft = cls.history.add_child(instance=ArticlePage(title='Borrador secreto', slug='borrador', introduction='Sin publicar.', body='<p>Pendiente.</p>', live=False))
        cls.private = cls.history.add_child(instance=ArticlePage(title='Investigación reservada', slug='privada', introduction='Documento privado.', body='<p>Reservado.</p>'))
        cls.private.save_revision().publish()
        PageViewRestriction.objects.create(page=cls.private, restriction_type='password', password='test-only')
        cls.galicia.tags.add('Monasterios')
        cls.galicia.save_revision().publish()
        call_command('update_index', verbosity=0)

    def test_public_routes(self):
        for url in ['/', '/sobre-mi/', '/radioaficion/', '/historia/', '/historia/ansemil/', '/search/', '/admin/login/']:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_region_and_tag_filters(self):
        response = self.client.get('/historia/?region=galicia')
        self.assertContains(response, 'Historia de Ansemil')
        self.assertNotContains(response, 'Archivo de Aldearrubia')
        response = self.client.get('/historia/?tag=monasterios')
        self.assertContains(response, 'Historia de Ansemil')
        self.assertNotContains(response, 'Archivo de Aldearrubia')
        self.assertEqual(self.client.get('/historia/?page=invalid').status_code, 200)

    def test_drafts_and_private_pages_are_not_listed(self):
        for url in ['/', '/historia/', '/search/?query=secreto', '/search/?query=reservada']:
            response = self.client.get(url)
            self.assertNotContains(response, 'Borrador secreto')
            self.assertNotContains(response, 'Investigación reservada')

    def test_search(self):
        self.assertContains(self.client.get('/search/?query=Ansemil'), 'Historia de Ansemil')
        self.assertContains(self.client.get('/search/?query=monasterio'), 'Historia de Ansemil')

    def test_seed_is_idempotent_and_preserves_edits(self):
        count = Page.objects.count()
        self.home.introduction = 'Texto editado por Daniel'
        self.home.save_revision().publish()
        call_command('seed_site', verbosity=0)
        self.assertEqual(count, Page.objects.count())
        self.home.refresh_from_db()
        self.assertEqual(self.home.introduction, 'Texto editado por Daniel')

    def test_article_editor(self):
        user = get_user_model().objects.create_superuser('editor', 'editor@example.com', 'test-password-only')
        self.client.force_login(user)
        self.assertEqual(self.client.get(f'/admin/pages/{self.galicia.pk}/edit/').status_code, 200)
