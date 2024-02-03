# Bot.py

import asyncio

import pytube
from pytube import YouTube
from aiogram import Bot, Dispatcher, types, executor
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext

from downloader import *
from BotToken import bot_token
from quality import get_quality


# Регистрация бота
storage = MemoryStorage()

bot = Bot(token = bot_token)
dp = Dispatcher(bot, storage = storage)


# Создание клавиатуры стандартной
keyboard_standart = types.ReplyKeyboardMarkup(resize_keyboard = True)


# Кнопки "Скачать аудио" и "Скачать видео"
kb_audio_dl = types.KeyboardButton("Скачать аудио")
kb_video_dl = types.KeyboardButton("Скачать видео")

# Добавление кнопок на стандартную клавиатуру
keyboard_standart.add(kb_audio_dl).insert(kb_video_dl)


# Создание кнопки отмена
keyboard_cancel = types.ReplyKeyboardMarkup(resize_keyboard = True)
kb_cancel = types.KeyboardButton("Отмена")
keyboard_cancel.add(kb_cancel)


# Удаление клавиатуры
keyboard_delete = types.ReplyKeyboardRemove()


# Класс состояния аудио
class AudioDownload(StatesGroup):
	get_url = State()

# Класс состояния видео
class VideoDownload(StatesGroup):
	get_url = State()
	get_quality = State()


# Приветствие нового пользователя
@dp.message_handler(commands = ["start"])
async def welcome(message: types.Message):
	await message.answer(
		f"Приветсвую вас, {message.from_user.first_name}!\nВыберите действие👇",
		reply_markup = keyboard_standart
	)


# Переход в состояние принятия ссылки
@dp.message_handler(state = None)
async def get_command(message: types.Message):
	if message.text == "Скачать аудио":
		await message.answer(
			"Пришлите ссылку на видео", 
			reply_markup = keyboard_cancel
		)
		
		await AudioDownload.get_url.set()

	elif message.text == "Скачать видео":
		await message.answer(
			"Пришлите ссылку на видео", 
			reply_markup = keyboard_cancel
		)
		
		await VideoDownload.get_url.set()

	else:
		await message.answer(
			"Команда не найдена", 
			reply_markup = keyboard_standart
		)


# Состояние получения ссылки на видео и конвертация в аудио
@dp.message_handler(state = AudioDownload.get_url)
async def get_video_url(message: types.Message, state: FSMContext):
	if message.text == "Отмена":
		await state.reset_state()
		await message.answer(
			"Конвертация в аудио отменена", 
			reply_markup = keyboard_standart
		)

	else:		
		try:
			youtube = YouTube(message.text)	
			await message.answer(
				"Видео конвертируется в аудио...", 
				reply_markup = keyboard_delete
			)

			audio_download(message.text)

			await bot.send_chat_action(
					message.from_user.id,
					types.ChatActions.UPLOAD_AUDIO
				)

			await asyncio.sleep(5)
			
			with open(f"{youtube.video_id}.mp3", "rb") as audio:
				await message.answer_audio(
					audio, 
					caption = youtube.title,
					reply_markup = keyboard_standart
				)
			
			await state.finish()

			audio_delete(message.text)

		except pytube.exceptions.RegexMatchError:
			await message.answer(
				"Ссылка неверная.\nВведите ссылку на видео в YouTube!"
			)


# Состояние получения ссылки на видео
@dp.message_handler(state = VideoDownload.get_url)
async def get_video_url(message: types.Message, state: FSMContext):
	if message.text == "Отмена":
		await state.reset_state()
		await message.answer(
			"Скачивание видео отменено", 
			reply_markup = keyboard_standart
		)

	else:
		try:
			await bot.send_chat_action(
				message.from_user.id,
				types.ChatActions.TYPING
			)
			
			youtube = YouTube(message.text)
			await state.update_data(url = message.text)

			keyboard_quality = types.ReplyKeyboardMarkup(resize_keyboard = True)
			qualities = get_quality(message.text)
			
			for q in qualities:
				if q > 720:
					continue

				else:
					keyboard_quality.insert(f"{q}p")

			keyboard_quality.add(kb_cancel)

			await message.answer(
				"Выберите качество видео", 
				reply_markup = keyboard_quality
			)
			
			await VideoDownload.next()

		except pytube.exceptions.RegexMatchError:
			await message.answer(
				"Ссылка неверная.\nВведите ссылку на видео в YouTube!"
			)

# Состояние получения качества видео
@dp.message_handler(state = VideoDownload.get_quality)
async def get_quality_video(message: types.Message, state: FSMContext):
	if message.text == "Отмена":
		await state.reset_state()
		await message.answer(
			"Скачивание видео отменено", 
			reply_markup = keyboard_standart
		)

	else:
		try:
			quality_list = [
				"144p", "240p", "360p", 
				"480p", "720p"
			]
			
			if message.text not in quality_list:
				await message.answer("Такого качества нет")
			
			elif message.text in quality_list:
				await message.answer(
					"Видео обрабатывается...", 
					reply_markup = keyboard_delete
				)
				
				data = await state.get_data()
				video_download(data["url"], message.text)
			
				youtube = YouTube(data["url"])

				await bot.send_chat_action(
					message.from_user.id,
					types.ChatActions.UPLOAD_VIDEO
				)

				await asyncio.sleep(5)

				with open(f"{youtube.video_id}.mp4", "rb") as video:
					await message.answer_video(
						video, 
						caption = youtube.title,
						reply_markup = keyboard_standart
					)
				
				video_delete(data["url"])

				await state.finish()

		except:
			await message.answer(
				"Ошибка при скачивании видео⚠️", 
				reply_markup = keyboard_standart
			)

			await state.reset_state()



# Запуск бота
async def on_startup(_):
	await bot.send_message(1142268145, "Бот успешно запущен")

executor.start_polling(
	dp, skip_updates = True, on_startup = on_startup
)
