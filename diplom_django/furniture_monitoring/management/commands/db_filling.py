import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from ...models import Camera
from ...models import Place

class Command(BaseCommand):
    help = 'Imports cameras from a CSV file'

    def handle(self, *args, **kwargs):
        
        try:data = pd.read_csv('csv/camera.csv')
        except Exception as e: ...
        
        for _, row in data.iterrows():
            camera = Camera(
                id=row['id'],
                name=row['name'],
                floor=row['floor'],
                wing=row['wing']
            )
            camera.save()

            self.stdout.write(self.style.SUCCESS(f'Successfully added camera {camera.name}'))
        
        try:data = pd.read_csv('csv/place.csv')
        except Exception as e: ...
        
        for _, row in data.iterrows():
            place = Place(
                id=row['id'],
                name=row['name'],
                description=row['description']
            )
            place.save()

            self.stdout.write(self.style.SUCCESS(f'Successfully added camera {place.name}'))
