import pandas as pd
from django.core.management.base import BaseCommand
from ...models import Camera, Place, LineCounter, CameraGraph, Object

class Command(BaseCommand):
    help = 'Imports from CSV files'

    def handle(self, *args, **kwargs):
        # Import places
        try:place_data = pd.read_csv('csv/place.csv')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error reading place.csv: {e}'))
            return

        for _, row in place_data.iterrows():
            place = Place(
                id=row['id']+1,
                name=row['name'],
                description=row.get('description', '')
            )
            place.save()
            
            
        # Import objects
        try:object_data = pd.read_csv('csv/object.csv')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error reading object.csv: {e}'))
            return

        for _, row in object_data.iterrows():
            object = Object(
                id=row['id'],
                name=row['name'],
            )
            object.save()
            
        # Import grapf
        try:grapf_data = pd.read_csv('csv/graph.csv')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error reading grapf.csv: {e}'))
            return

        for _, row in grapf_data.iterrows():
            grapf = CameraGraph(
                id=row['id'],
                cam_id1 = row['cam_id1'],
                cam_id2 = row['cam_id2'],
                weight = row['weight'],
            )
            grapf.save()

        # Import cameras
        try:camera_data = pd.read_csv('csv/camera.csv')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error reading cameras.csv: {e}'))
            return

        for _, row in camera_data.iterrows():
            place_id = row.get('place')+1
            place = Place.objects.get(id=place_id) if place_id and not pd.isna(place_id) else None

            camera = Camera(
                id=row['id'],
                name=row['name'],
                floor=row['floor'],
                wing=row['wing'],
                place=place,
                video_path=row['path']
            )
            camera.save()
            
        # Import linecounter
        try:camera_data = pd.read_csv('csv/linecounter.csv')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error reading linecounter.csv: {e}'))
            return

        for _, row in camera_data.iterrows():
            camera_id = row.get('camera')
            camera = Camera.objects.get(id=camera_id) if camera_id and not pd.isna(camera_id) else None

            if camera is None:
                self.stdout.write(self.style.WARNING(f'Skipping linecounter for missing camera_id {camera_id}'))
                continue

            start_x = row['x1']
            start_y = row['y1']
            end_x = row['x2']
            end_y = row['y2']
            line_id = row['line']

            # Check if a linecounter with these parameters already exists
            if not LineCounter.objects.filter(camera=camera, start_x=start_x, start_y=start_y, end_x=end_x, end_y=end_y).exists():
                linecounter = LineCounter(
                    camera=camera,
                    start_x=start_x,
                    start_y=start_y,
                    end_x=end_x,
                    end_y=end_y,
                    line_id=line_id,
                )
                linecounter.save()
            else:
                self.stdout.write(self.style.WARNING(f'Linecounter for camera {camera_id} with these coordinates already exists'))

