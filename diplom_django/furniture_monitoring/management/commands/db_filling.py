import pandas as pd
from django.core.management.base import BaseCommand
from ...models import Camera, Place

class Command(BaseCommand):
    help = 'Imports places and cameras from CSV files'

    def handle(self, *args, **kwargs):
        # Import places
        try:
            place_data = pd.read_csv('csv/place.csv')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error reading place.csv: {e}'))
            return

        for _, row in place_data.iterrows():
            place = Place(
                id=row['id'],
                name=row['name'],
                description=row.get('description', '')
            )
            place.save()
            self.stdout.write(self.style.SUCCESS(f'Successfully added place {place.name}'))

        # Import cameras
        try:
            camera_data = pd.read_csv('csv/camera.csv')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error reading cameras.csv: {e}'))
            return

        for _, row in camera_data.iterrows():
            place_id = row.get('place')
            place = Place.objects.get(id=place_id) if place_id and not pd.isna(place_id) else None

            camera = Camera(
                id=row['id'],
                name=row['name'],
                floor=row['floor'],
                wing=row['wing'],
                place=place
            )
            camera.save()
            self.stdout.write(self.style.SUCCESS(f'Successfully added camera {camera.name}'))
