#!/usr/bin/python3.9

import logging
import urllib
import shutil
import os
import glob
import conf

from aiogram import Bot, Dispatcher, executor, types

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

### переменные ###
if os.name == 'nt':
    path = 'C:\python\MarketingBot'
    os.chdir('C:\python\MarketingBot')
else:
    path = '/opt/reports'
    os.chdir('/opt/marketing_parsers/')
storage = MemoryStorage()

# задаем уровень логов
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# инициализируем бота
bot = Bot(token=conf.token)
dp = Dispatcher(bot, storage=storage)

# States
class Form(StatesGroup):
    files_name = State()  # Will be represented in storage as 'Form:files_name'
    search = State()
    place = State()
    files = State()
    msg = State()
    finish = State()

@dp.message_handler(content_types=['document'])
async def scan_message(msg: types.Message):
    if msg.from_user.id == conf.letkin or msg.from_user.id == conf.Omega:
        document_id = msg.document.file_id
        name = msg.document.file_name
        with open('files.txt', 'r') as f:
            files_name = f.read().split('\n')
        if name in files_name:
            print(f'trying upload file {name}')
            if name == 'tags_wb.xlsx':
                file_info = await bot.get_file(document_id)
                fi = file_info.file_path
                urllib.request.urlretrieve(f'https://api.telegram.org/file/bot{conf.token}/{fi}',f'./{name}')
                await bot.send_message(msg.from_user.id, 'Файл успешно сохранён')
                shutil.move(name, f'parsers/wb_tag/{name}')

            elif name in ('all_sku.xlsx', 'dns_sku.txt', 'citilink.xlsx', 'castorama_sku.xlsx'):
                file_info = await bot.get_file(document_id)
                fi = file_info.file_path
                urllib.request.urlretrieve(f'https://api.telegram.org/file/bot{conf.token}/{fi}',f'./{name}')
                await bot.send_message(msg.from_user.id, 'Файл успешно сохранён')
                shutil.move(name, f'/opt/parser_id/{name}')
 
            else:
                file_info = await bot.get_file(document_id)
                fi = file_info.file_path
                urllib.request.urlretrieve(f'https://api.telegram.org/file/bot{conf.token}/{fi}',f'./{name}')
                await bot.send_message(msg.from_user.id, 'Файл успешно сохранён')
                shutil.move(name, f'parsers/{name}')
        else:
            await bot.send_message(msg.from_user.id, f'Файла нет в списке. {files_name}')
    else:
        await bot.send_message(msg.from_user.id, f'У вас недостаточно прав для этого.')



##### настройка команда ######
@dp.message_handler(commands="set_commands", state="*")
async def cmd_set_commands(message: types.Message):
    if message.from_user.id == conf.Omega:  # Подставьте сюда свой Telegram ID
        commands = [types.BotCommand(command="/wb", description="Отчёты WB"),
	types.BotCommand(command="/wb_tags", description="Отчёты WB TAGS"),
	types.BotCommand(command="/aliexpress", description="Отчёт Алиэкспресс"),
	types.BotCommand(command="/citilink", description="Отчёт Ситилинк"),
	types.BotCommand(command="/sber", description="Отчёт Goods(СберМегаМаркет)"),
	types.BotCommand(command="/dns", description="Отчёт DNS-SHOP."),
	types.BotCommand(command="/ozon", description="Отчёт OZON."),
	types.BotCommand(command="/vseinstrumenti", description="Отчёт VSE INSTRUMENTI."),
	types.BotCommand(command="/castorama", description="Отчёт Castorama."),
	types.BotCommand(command="/cancel", description="отмена запроса.")]
        await bot.set_my_commands(commands)
        await message.answer("Команды настроены.")

### омтена запроса ###
@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Cancelling state %r', current_state)
    # Cancel state and inform user about it
    await state.finish()
    # And remove keyboard (just in case)
    await message.reply('Cancelled.', reply_markup=types.ReplyKeyboardRemove())



### Создание кнопок
def build_menu(buttons,n_cols,header_buttons=None,footer_buttons=None):
  menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
  if header_buttons:
    menu.insert(0, header_buttons)
  if footer_buttons:
    menu.append(footer_buttons)
  return menu

async def get_keyboard(wfiles):
    # Генерация клавиатуры.
    buttons = []
    for each in wfiles:
        buttons.append(types.InlineKeyboardButton(text=str(each), callback_data=str(each)))
    buttons.append(types.InlineKeyboardButton(text='Поиск', callback_data='poisk'))
    keyboard = types.InlineKeyboardMarkup(row_width=1, one_time_keyboard=True)
    keyboard.add(*buttons)
    return keyboard
###########################



### команда для выбора и загрузки файла ###
@dp.message_handler(commands=['wb'], state="*")
async def wb(message: types.Message, state: FSMContext):
    files = []
    temp_path = os.path.join(path,'wb')
    files = glob.glob(temp_path+'/*')
    files.sort(key=os.path.getmtime, reverse=True)
    for i in range(len(files)):
        files[i] = files[i].replace(temp_path + '/','')
    wfiles = files.copy()
    if len(wfiles) > 6:
        del wfiles[7:]
    if len(files) == 0:
        await message.answer('В данной категории еще нет отчётов')
        await state.finish()
    else:
        otvet = await message.answer("Выберите нужный файл", reply_markup=await get_keyboard(wfiles))
        await state.update_data(msg=otvet.message_id)
        await state.update_data(files=wfiles)
        await state.update_data(place='wb')
        await Form.files_name.set()

@dp.message_handler(commands=['wb_tags'], state="*")
async def wb_tags(message: types.Message, state: FSMContext):
    files = []
    temp_path = os.path.join(path,'wb_tags')
    files = glob.glob(temp_path+'/*')
    files.sort(key=os.path.getmtime, reverse=True)
    for i in range(len(files)):
        files[i] = files[i].replace(temp_path + '/','')
    wfiles = files.copy()
    if len(wfiles) > 6:
        del wfiles[7:]
    if len(files) == 0:
        await message.answer('В данной категории еще нет отчётов')
        await state.finish()
    else:
        otvet = await message.answer("Выберите нужный файл", reply_markup=await get_keyboard(wfiles))
        await state.update_data(msg=otvet.message_id)
        await state.update_data(files=wfiles)
        await state.update_data(place='wb_tags')
        await Form.files_name.set()

@dp.message_handler(commands=['aliexpress'], state="*")
async def aliexpress(message: types.Message, state: FSMContext):
    files = []
    temp_path = os.path.join(path,'aliexpress')
    files = glob.glob(temp_path+'/*')
    files.sort(key=os.path.getmtime, reverse=True)
    for i in range(len(files)):
        files[i] = files[i].replace(temp_path + '/','')
    wfiles = files.copy()
    if len(wfiles) > 6:
        del wfiles[7:]
    if len(files) == 0:
        await message.answer('В данной категории еще нет отчётов')
        await state.finish()
    else:
        otvet = await message.answer("Выберите нужный файл", reply_markup=await get_keyboard(wfiles))
        await state.update_data(msg=otvet.message_id)
        await state.update_data(files=wfiles)
        await state.update_data(place='aliexpress')
        await Form.files_name.set()

@dp.message_handler(commands=['dns'], state="*")
async def dns(message: types.Message, state: FSMContext):
    files = []
    temp_path = os.path.join(path,'dns')
    files = glob.glob(temp_path+'/*')
    files.sort(key=os.path.getmtime, reverse=True)
    for i in range(len(files)):
        files[i] = files[i].replace(temp_path + '/','')
    wfiles = files.copy()
    if len(wfiles) > 6:
        del wfiles[7:]
    if len(files) == 0:
        await message.answer('В данной категории еще нет отчётов')
        await state.finish()
    else:
        otvet = await message.answer("Выберите нужный файл", reply_markup=await get_keyboard(wfiles))
        await state.update_data(msg=otvet.message_id)
        await state.update_data(files=wfiles)
        await state.update_data(place='dns')
        await Form.files_name.set()

@dp.message_handler(commands=['ozon'], state="*")
async def ozon(message: types.Message, state: FSMContext):
    files = []
    temp_path = os.path.join(path,'ozon')
    files = glob.glob(temp_path+'/*')
    files.sort(key=os.path.getmtime, reverse=True)
    for i in range(len(files)):
        files[i] = files[i].replace(temp_path + '/','')
    wfiles = files.copy()
    if len(wfiles) > 6:
        del wfiles[7:]
    if len(files) == 0:
        await message.answer('В данной категории еще нет отчётов')
        await state.finish()
    else:
        otvet = await message.answer("Выберите нужный файл", reply_markup=await get_keyboard(wfiles))
        await state.update_data(msg=otvet.message_id)
        await state.update_data(files=wfiles)
        await state.update_data(place='ozon')
        await Form.files_name.set()

@dp.message_handler(commands=['citilink'], state="*")
async def citilink(message: types.Message, state: FSMContext):
    files = []
    temp_path = os.path.join(path,'citilink')
    files = glob.glob(temp_path+'/*')
    files.sort(key=os.path.getmtime, reverse=True)
    for i in range(len(files)):
        files[i] = files[i].replace(temp_path + '/','')
    wfiles = files.copy()
    if len(wfiles) > 6:
        del wfiles[7:]
    if len(files) == 0:
        await message.answer('В данной категории еще нет отчётов')
        await state.finish()
    else:
        otvet = await message.answer("Выберите нужный файл", reply_markup=await get_keyboard(wfiles))
        await state.update_data(msg=otvet.message_id)
        await state.update_data(files=wfiles)
        await state.update_data(place='citilink')
        await Form.files_name.set()

@dp.message_handler(commands=['sber'], state="*")
async def sber(message: types.Message, state: FSMContext):
    files = []
    temp_path = os.path.join(path,'sber')
    files = glob.glob(temp_path+'/*')
    files.sort(key=os.path.getmtime, reverse=True)
    for i in range(len(files)):
        files[i] = files[i].replace(temp_path + '/','')
    wfiles = files.copy()
    if len(wfiles) > 6:
        del wfiles[7:]
    if len(files) == 0:
        await message.answer('В данной категории еще нет отчётов')
        await state.finish()
    else:
        otvet = await message.answer("Выберите нужный файл", reply_markup=await get_keyboard(wfiles))
        await state.update_data(msg=otvet.message_id)
        await state.update_data(files=wfiles)
        await state.update_data(place='sber')
        await Form.files_name.set()

@dp.message_handler(commands=['vseinstrumenti'], state="*")
async def vseinstrumenti(message: types.Message, state: FSMContext):
    files = []
    temp_path = os.path.join(path,'vseinstrumenti')
    files = glob.glob(temp_path+'/*')
    files.sort(key=os.path.getmtime, reverse=True)
    for i in range(len(files)):
        files[i] = files[i].replace(temp_path + '/','')
    wfiles = files.copy()
    if len(wfiles) > 6:
        del wfiles[7:]
    if len(files) == 0:
        await message.answer('В данной категории еще нет отчётов')
        await state.finish()
    else:
        otvet = await message.answer("Выберите нужный файл", reply_markup=await get_keyboard(wfiles))
        await state.update_data(msg=otvet.message_id)
        await state.update_data(files=wfiles)
        await state.update_data(place='vseinstrumenti')
        await Form.files_name.set()

@dp.message_handler(commands=['castorama'], state="*")
async def castorama(message: types.Message, state: FSMContext):
    files = []
    temp_path = os.path.join(path,'castorama')
    files = glob.glob(temp_path+'/*')
    files.sort(key=os.path.getmtime, reverse=True)
    for i in range(len(files)):
        files[i] = files[i].replace(temp_path + '/','')
    wfiles = files.copy()
    if len(wfiles) > 6:
        del wfiles[7:]
    if len(files) == 0:
        await message.answer('В данной категории еще нет отчётов')
        await state.finish()
    else:
        otvet = await message.answer("Выберите нужный файл", reply_markup=await get_keyboard(wfiles))
        await state.update_data(msg=otvet.message_id)
        await state.update_data(files=wfiles)
        await state.update_data(place='castorama')
        await Form.files_name.set()


@dp.callback_query_handler(state=Form.files_name)
async def process_callback_kb1btn1(query: types.CallbackQuery, state: FSMContext):
    msg = query.data
    usr = query.from_user.id
    async with state.proxy() as data:
        pass
    files = data['files']
    if msg in files:
        await types.ChatActions.upload_document()
        file = os.path.join(os.path.join(path,data['place']), msg)
        xlsx = types.InputFile(file)
        await bot.send_document(usr, document=xlsx)
        await bot.delete_message(usr,data['msg'])
        await state.finish()
    elif msg == 'poisk':
        await bot.send_message(usr,'Введите дату в формате dd.mm.yyyy')
        await bot.delete_message(usr,data['msg'])
        await Form.search.set()
    else:
        await bot.send_message(usr,'wtf !?. Начните сначала')
        await state.finish()

@dp.message_handler(state=Form.search)
async def search(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
            pass
    date = message.text
    files = data['files']
    sfile = []
    temp_path = os.path.join(path,data['place'])
    for i in range(len(files)):
        if date in files[i]:
            files[i] = files[i].replace(temp_path,'')
            sfile.append(files[i])
        else:
            pass
    if len(sfile) == 0:
        await message.answer('Файлов по вашему запросу не найдено')
        await state.finish()
    else:
        otvet = await message.answer("Выберите нужный файл", reply_markup=await get_keyboard(sfile))
        await state.update_data(msg=otvet.message_id)
        sfile = []
        await Form.files_name.set()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
