from django.core.management.base import BaseCommand

from distribution import main


class Command(BaseCommand):
    def handle(self, *args, **options):
        main()
