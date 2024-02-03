# downloader.py

import os

from pytube import YouTube


# Метод скачивания видео
def video_download(url, quality):
	url = YouTube(url)
	yt = url.streams
	video = yt.filter(res = quality).first()
	video.download(filename = f"{url.video_id}.mp4")


# Метод скачивания аудиодорожки
def audio_download(url):
	url = YouTube(url)
	yt = url.streams
	audio = yt.filter(only_audio = True).first()
	audio.download(filename = f"{url.video_id}.mp3")


# Метод удаления видео
def video_delete(url):
	url = YouTube(url)
	yt = url.streams
	os.remove(f"{url.video_id}.mp4")


def audio_delete(url):
	url = YouTube(url)
	yt = url.streams
	os.remove(f"{url.video_id}.mp3")
