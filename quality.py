# quality.py

from pytube import YouTube

# Метод получения качеств видео
def get_quality(url):
	url = url
	video = YouTube(url, 
				use_oauth = True,
				allow_oauth_cache = True
			)
	
	quality = set()

	# Цикл передачи качества в множество
	for stream in video.streams.filter(type = "video"):
		quality.add(int(stream.resolution[0:-1]))

	# Переводим множество в список и сортируем по возрастанию 
	# качество
	quality = list(quality)
	quality.sort()
	
	return quality
