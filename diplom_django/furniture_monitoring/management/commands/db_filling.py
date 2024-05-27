import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from ...models import Camera

class Command(BaseCommand):
    help = 'Imports cameras from a CSV file'

    def handle(self, *args, **kwargs):
        # Укажите путь к CSV файлу прямо здесь
        csv_file = 'csv/camera.csv'

        try:
            data = pd.read_csv(csv_file)
        except Exception as e:
            raise CommandError(f'Error reading CSV file: {e}')

        for _, row in data.iterrows():
            camera = Camera(
                id=row['id'],
                name=row['name'],
                floor=row['floor'],
                wing=row['wing']
            )
            camera.save()

            self.stdout.write(self.style.SUCCESS(f'Successfully added camera {camera.name}'))

