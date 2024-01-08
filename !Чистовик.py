import asyncio
import pandas as pd
from aiogram import types, executor, Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext

TOKEN = '6423235894:AAG-Sw7El5m70tE51Ct-UYVGkuqXxOByZ8A'
storage = MemoryStorage()
bot = Bot(TOKEN)
dp = Dispatcher(bot=bot, storage=storage)

file_name = 'lab_pi_101.xlsx'
dataframe = pd.read_excel(file_name)
all_groups = dataframe['Группа'].unique().tolist()
all_groups.sort()

class ProfileStatesGroup(StatesGroup):
    choosing_group = State()
    check = State()
    DA = State()

def process(vibor):
    grupa = dataframe['Группа'] == vibor
    marks = dataframe['Оценка'].count()
    marks_grupa = dataframe['Группа'] == vibor
    kolvo_marks_grupa=dataframe[marks_grupa]['Оценка'].count()
    students_grupa = dataframe[marks_grupa]['Личный номер студента'].unique()
    formi_control = dataframe[marks_grupa]['Уровень контроля'].unique()
    Years = sorted(dataframe['Год'].unique())
    return(f"В исходном датасете содержалось,{marks}, оценок из них, {kolvo_marks_grupa}, оценок относятся к группе, {vibor}, \n В датасете находятся оценки {len(students_grupa)} студентов со следующими личными номерами: {', '.join(map(str,students_grupa))} \n Используемые формы контроля: {', '.join(map(str,formi_control))}, \n Данные представлены по следующим учебным годам: {', '.join(map(str,Years))}")  
    

def get_KeyBoard() -> ReplyKeyboardMarkup:
    KeyBoard = ReplyKeyboardMarkup(resize_keyboard=True)
    KeyBoard.add(KeyboardButton('/Список_групп'))
    return KeyBoard

@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.answer('Для вывода списка групп нажмите кнопку "Список групп" или введите команду "/Список_групп"',
                         reply_markup=get_KeyBoard())

@dp.message_handler(commands=['Список_групп', 'список_групп'])
async def process_choose_group_command(message: types.Message):
    await message.answer(f'Список групп из файла: {", ".join(map(str, all_groups))}. \n Выберите нужную группу и введите её!',
                         reply_markup=types.ReplyKeyboardRemove())
    await ProfileStatesGroup.choosing_group.set()

@dp.message_handler(state=ProfileStatesGroup.choosing_group)
async def choose_group(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['group'] = message.text
    await message.answer(f'Вы указали группу {data["group"]}. вы уверены?')
    await ProfileStatesGroup.DA.set()

@dp.message_handler(state=ProfileStatesGroup.DA)
async def choose_group(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['ответ'] = message.text.lower()    

    if data["ответ"]=='да':

        if data['group'] in dataframe['Группа'].unique():
            await message.answer('группа найдена в файле')
            async with state.proxy() as data:
                await message.answer(process(data["group"]))
                await message.answer('данные выведены. если необходимо, вы можете выбрать другую группу',
                                     reply_markup=get_KeyBoard())
                await ProfileStatesGroup.choosing_group.set()         

        else:
            await message.answer('группа не найдена. проверьте свой  выбор и написание группы',
                                 reply_markup=get_KeyBoard())
            pass
    else: 
        await ProfileStatesGroup.choosing_group.set()
        await message.answer('произошла ошибка, нажмите кнопку для вывода списка групп',
                             reply_markup=get_KeyBoard())
            
    await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
        