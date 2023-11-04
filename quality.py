# quality.py

from pytube import YouTube

# Метод получения качеств видео
def get_quality(url):
	url = url
	video = YouTube(url)
	quality = set()

	# Цикл передачи качества в множество
	for stream in video.streams.filter(type = "video"):
		quality.add(int(stream.resolution[0:-1]))

	# Переводим множество в список и сортируем по возрастанию 
	# качество
	quality = list(quality)
	quality.sort()
	
	available_qualities = "Доступные качества для этого видео: "

	# Цикл передачи в строку доступных качеств
	for quality_str in quality:
		if quality_str == 1080 or quality_str == 1440 or quality_str == 2160 or quality_str == 4320:
			continue

		else:
			available_qualities += str(quality_str) + "p, "

	return available_qualities
