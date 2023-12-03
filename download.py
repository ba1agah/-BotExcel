import asyncio
import aiogram
import aiohttp
import io
import pandas as pd
from aiogram import types, executor, Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext

TOKEN = '6423235894:AAG-Sw7El5m70tE51Ct-UYVGkuqXxOByZ8A'
storage = MemoryStorage()
bot = Bot(TOKEN)
dp = Dispatcher(bot=bot, storage=storage)

class ProfileStatesGroup(StatesGroup):
    load_file = State()
    spisok = State()
    choss = State()
    DA = State()

def get_KeyBoard() -> ReplyKeyboardMarkup:
    KeyBoard = ReplyKeyboardMarkup(resize_keyboard=True)
    KeyBoard.add(KeyboardButton('/Список'))
    return KeyBoard

@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.answer('Загрузите файл')
    await ProfileStatesGroup.load_file.set()

@dp.message_handler(content_types=['document'],state=ProfileStatesGroup.load_file)
async def load_file(message: types.Message, state: FSMContext):
    file_info = message.document
    file_id = file_info.file_id
    file = await bot.get_file(file_id)
    await message.answer("Файл получен, ожидайте...")
    
    file_path = file.file_path
    print('айди: ', file_id, 'информация: ', file_info)
    file_buffer = io.BytesIO()
    MyBinaryIo = await bot.download_file(file_path,file_buffer)
    print (MyBinaryIo)

    # Создание DataFrame из скачанного файла Excel
    dataframe = pd.read_excel(MyBinaryIo)
    print (dataframe)
    async with state.proxy() as data:
        data['файл'] = dataframe
    await message.answer("Файл сохранен. Напишите команду /список, для вывода групп и информации по ним",
                         reply_markup=get_KeyBoard())
    await ProfileStatesGroup.spisok.set()

@dp.message_handler(commands=['список'],state= ProfileStatesGroup.spisok)
async def process_choss(message:types.message,state: FSMContext):
    print('я начинаю поиск групп')

    async with state.proxy() as data:

        print('датафрейм = дата')
        #gr = list(set(dataframe['Группа'].tolist()))
        #students_ids = data.loc[data['Группа'] == f'{data['Группа']} Группы'].unique()
        gr = data['файл']['Группа'].unique().tolist()
        # gr = data['файл']['Группа'].unique().list()
        print('датаФРЙЕМ ЛОК')
        print(", ".join(map(str,gr)))
        #await message.answer(gr)
        
        await message.answer(f'список: {", ".join(map(str,gr))}, \n по какой группе нужно вывести информацию? введите ее',
                             reply_markup=ReplyKeyboardRemove())
        await ProfileStatesGroup.choss.set()

@dp.message_handler(state=ProfileStatesGroup.choss)
async def choose_group(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data['group'] = message.text
            print(data['group'])
        await message.answer(f'Вы указали группу {data["group"]}. вы уверены?')
        await ProfileStatesGroup.DA.set()

@dp.message_handler(state=ProfileStatesGroup.DA)
async def choose_group(message: types.Message, state: FSMContext):

    def process(vibor):
        grupa = data['файл']['Группа'] == vibor
        marks = data['файл']['Оценка'].count()
        marks_grupa = data['файл']['Группа'] == vibor
        kolvo_marks_grupa=data['файл'][marks_grupa]['Оценка'].count()
        students_grupa = data['файл'][marks_grupa]['Личный номер студента'].unique()
        formi_control = data['файл'][marks_grupa]['Уровень контроля'].unique()
        Years = sorted(data['файл']['Год'].unique())
        return(f"В исходном датасете содержалось {marks} оценок, из них {kolvo_marks_grupa} оценок относятся к группе {vibor}, \nВ датасете находятся оценки {len(students_grupa)} студентов со следующими личными номерами: {', '.join(map(str,students_grupa))} \nИспользуемые формы контроля: {', '.join(map(str,formi_control))}, \nДанные представлены по следующим учебным годам: {', '.join(map(str,Years))}")  
    async with state.proxy() as data:
        data['ответ'] = message.text.lower()  
    
    if data["group"] in data['файл']['Группа'].unique().tolist():
        print('такая группа реально есть в файле. сравниваю ответ да и сообщение пользователя')
        if data['ответ'] == 'да':
            print(data['ответ'])
            await message.answer(f'Группа найдена. Вывод информации по группе {data["group"]}')
            await message.answer(process(data["group"]))
            await message.answer('Если вы хотите выбрать другую группу, введите команду /список',
                                 reply_markup=get_KeyBoard())
            await ProfileStatesGroup.spisok.set()
        else:
            await message.answer('че то не так брат')
            print("ты ошибся, какая то ошибка  ")
    else:
        await message.answer('Неверно указана группа. Напишите заново команду /список или нажмите кнопку')
        await ProfileStatesGroup.spisok.set()
        print('ну получается ОТВЕТ ДАААААААААААААААА')
    await ProfileStatesGroup.choss.set()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)