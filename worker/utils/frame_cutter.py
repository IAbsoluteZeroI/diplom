import cv2
from supervision.video.dataclasses import VideoInfo

def extract_frames(video_path, output_folder):
    # Получаем информацию о видео
    video_info = VideoInfo.from_video_path(video_path)
    total_frames = video_info.total_frames

    # Открываем видеофайл
    video_capture = cv2.VideoCapture(video_path)
    # Проверяем, что видеофайл успешно открыт
    if not video_capture.isOpened():
        print("Ошибка при открытии видеофайла")
        return

    # Счетчик кадров
    frame_count = 0

    # Читаем кадры из видеофайла
    while frame_count < total_frames:
        # Читаем следующий кадр
        success, frame = video_capture.read()

        # Проверяем, успешно ли кадр был прочитан
        if not success:
            break

        # Увеличиваем счетчик кадров
        frame_count += 1

        # Сохраняем каждый 15-й кадр
        if frame_count % 15 == 0:
            # Формируем имя файла для сохранения текущего кадра
            frame_filename = f"{output_folder}/frame_{video_path}_{frame_count}.jpg"

            # Сохраняем текущий кадр в файл
            cv2.imwrite(frame_filename, frame)

    # Закрываем видеофайл
    video_capture.release()

    print(f"Извлечено {frame_count} кадров")


# Путь к видеофайлу
video_path = "lift.avi"
# Папка для сохранения кадров
output_folder = "frames"

# Извлекаем кадры из видео
extract_frames(video_path, output_folder)
