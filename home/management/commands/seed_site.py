from django.core.management.base import BaseCommand
from django.db import transaction
from wagtail.models import Site
from home.models import HomePage, AboutPage, SectionPage

class Command(BaseCommand):
    help = 'Crea las páginas iniciales sin sobrescribir contenido existente. No crea artículos ficticios.'

    @transaction.atomic
    def handle(self, *args, **options):
        home = HomePage.objects.first()
        if not home:
            self.stderr.write('No existe la portada. Ejecuta migrate primero.')
            return
        if home.title == 'Home':
            home.title = 'Inicio'
            home.introduction = 'Soy Daniel García. Este es mi espacio para compartir experiencias de radioafición y mis trabajos sobre historia y patrimonio de Galicia y Aldearrubia.'
            home.save_revision().publish()
        definitions = [
            (AboutPage, 'sobre-mi', {'title': 'Sobre mí', 'introduction': 'Daniel García Coego · EA1RFI', 'body': '<p>La radioafición y la investigación histórica forman parte de mis intereses. En este cuaderno reúno experiencias, apuntes y trabajos sobre los lugares y temas que voy explorando.</p>'}),
            (SectionPage, 'radioaficion', {'title': 'Radioafición', 'kind': 'radio', 'introduction': 'Experiencias entre antenas y ondas. Mi estación, activaciones, proyectos y aprendizajes como EA1RFI.'}),
            (SectionPage, 'historia', {'title': 'Historia y patrimonio', 'kind': 'history', 'introduction': 'Mis trabajos de historia local: lugares, documentos y memoria de Galicia y Aldearrubia.'}),
        ]
        for model, slug, fields in definitions:
            if not home.get_children().filter(slug=slug).exists():
                page = model(slug=slug, show_in_menus=True, **fields)
                home.add_child(instance=page)
                page.save_revision().publish()
        Site.objects.filter(root_page=home, site_name='').update(site_name='Daniel García · EA1RFI')
        self.stdout.write(self.style.SUCCESS('Estructura inicial lista. El contenido existente se ha conservado.'))
