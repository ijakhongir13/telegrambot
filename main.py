import logging

import aiogram.types
import numpy
import database as db
import datetime
import flask
from flask import Flask, request, Response
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton

app = Flask(__name__)


@app.route('/')
def index():
    return '<h1>Hello World!</h1>'


API_TOKEN = '5835225357:AAGQApnDDPAc273vB-l_gNcL4u2J45SRMSk'
HELP_TEXT = '/start - ботни ишга тушириш\n/about - ушбу телеграм бот хақида\n/help - фойдали буйруқлар\n' \
            '/cancel - жараённи бекор қилиш\n----------------------\n<b><i>Ушбу буйруқлардан бирини ишлатганингиздан ' \
            'сўнг, барча киритган маълумотларингиз ўчиб кетишини инобатга олишингизни сўраймиз!</i></b>'
english_alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
                    'U', 'V', 'W', 'X', 'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n',
                    'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'А', 'Б', 'В', 'Г', 'Д', 'Е', 'Ё', 'Ж',
                    'З', 'И', 'Й', 'К', 'Л', 'М', 'Н', 'О', 'П', 'Р', 'С', 'Т', 'У', 'Ф', 'Х', 'Ц', 'Ч', 'Ш', 'Щ', 'Ъ',
                    'Ы', 'Ь', 'Э', 'Ю', 'Я', 'а', 'б', 'в', 'г', 'д', 'е', 'ё', 'ж', 'з', 'и', 'й', 'к', 'л', 'м', 'н',
                    'о', 'п', 'р', 'с', 'т', 'у', 'ф', 'х', 'ц', 'ч', 'ш', 'щ', 'ъ', 'ы', 'ь', 'э', 'ю', 'я', 'Ў', 'Қ',
                    'Ғ', 'Ҳ', 'ў', 'қ', 'ғ', 'ҳ', ' ']
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

user_contact_markup = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('☎️ Телефон рақамимни юбориш',
                                                                                   request_contact=True))
request_add_markup = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('🙅‍♂️ Қўшимча иловаларим йўқ'))
request1 = KeyboardButton('📝 Таклиф')
request2 = KeyboardButton('‼️ Шикоят')
request3 = KeyboardButton('💼 Ариза')
request4 = KeyboardButton('Бошқа')
request_type_markup = ReplyKeyboardMarkup(resize_keyboard=True).add(request1, request2, request3, request4)
message_types = ['audio', 'document', 'photo', 'video', 'video_note', 'voice', 'contact', 'location']
moderator_chat_id = 6090824712


class User(StatesGroup):
    user_id = State()
    user_name = State()
    user_contact = State()
    request_type = State()
    request_content = State()
    request_add = State()
    request_add_type = State()
    request_number = State()
    request_datetime = State()


async def on_startup(_):
    await db.db_start()
    print("Successfully launched!")


@dp.message_handler(commands=['start'])
async def command_start(message: types.Message, state: FSMContext):
    await state.finish()
    await User.user_name.set()
    await message.answer('Ассалому алайкум!😊\nИсм, Фамилия ва Шарифингизни тўлиқ форматда киритинг:', parse_mode='html',
                         reply_markup=ReplyKeyboardRemove())


@dp.message_handler(state='*', commands=['help'])
async def command_help(message: types.Message, state: FSMContext):
    await state.finish()
    current_state = await state.get_state()
    if current_state is None:
        return await message.answer(HELP_TEXT, parse_mode='html', reply_markup=ReplyKeyboardRemove())
    await message.answer(HELP_TEXT, parse_mode='html', reply_markup=ReplyKeyboardRemove())


@dp.message_handler(state='*', commands=['about'])
async def command_about(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return await message.answer('Ўзбекистон Республикаси Табиат ресурслари вазирлиги қошидаги Ўзбекистон '
                                    'Республикаси гидрометеорология хизмати агентлигининг жисмоний ва юридик '
                                    'шахсларнинг мурожаатларини қабул қилишга мўлжалланган телеграм бот.',
                                    reply_markup=ReplyKeyboardRemove())
    await message.answer('bla bla bla', reply_markup=ReplyKeyboardRemove())


@dp.message_handler(state='*', commands=['cancel'])
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return await message.answer('⛔ Жараён бекор қилинган!')
    logging.info('Cancelling the process %r', current_state)
    await state.finish()
    await message.answer('⛔ Жараён бекор қилинди!', reply_markup=ReplyKeyboardRemove())


@dp.message_handler(state=[None, User.user_name, User.request_type, User.request_content],
                    content_types=[types.ContentType.AUDIO, types.ContentType.ANIMATION, types.ContentType.DOCUMENT,
                                   types.ContentType.GAME, types.ContentType.PHOTO, types.ContentType.STICKER,
                                   types.ContentType.VIDEO, types.ContentType.VIDEO_NOTE, types.ContentType.VOICE,
                                   types.ContentType.CONTACT, types.ContentType.VENUE, types.ContentType.LOCATION,
                                   types.ContentType.POLL, types.ContentType.DICE, types.ContentType.NEW_CHAT_MEMBERS,
                                   types.ContentType.LEFT_CHAT_MEMBER, types.ContentType.INVOICE,
                                   types.ContentType.SUCCESSFUL_PAYMENT, types.ContentType.CONNECTED_WEBSITE,
                                   types.ContentType.MESSAGE_AUTO_DELETE_TIMER_CHANGED,
                                   types.ContentType.MIGRATE_FROM_CHAT_ID, types.ContentType.MIGRATE_TO_CHAT_ID,
                                   types.ContentType.PINNED_MESSAGE, types.ContentType.NEW_CHAT_TITLE,
                                   types.ContentType.NEW_CHAT_PHOTO, types.ContentType.DELETE_CHAT_PHOTO,
                                   types.ContentType.GROUP_CHAT_CREATED, types.ContentType.PASSPORT_DATA,
                                   types.ContentType.PROXIMITY_ALERT_TRIGGERED, types.ContentType.VOICE_CHAT_SCHEDULED,
                                   types.ContentType.VOICE_CHAT_STARTED, types.ContentType.VOICE_CHAT_ENDED,
                                   types.ContentType.VOICE_CHAT_PARTICIPANTS_INVITED, types.ContentType.WEB_APP_DATA,
                                   types.ContentType.FORUM_TOPIC_CREATED, types.ContentType.FORUM_TOPIC_CLOSED,
                                   types.ContentType.FORUM_TOPIC_REOPENED, types.ContentType.VIDEO_CHAT_SCHEDULED,
                                   types.ContentType.VIDEO_CHAT_STARTED, types.ContentType.VIDEO_CHAT_ENDED,
                                   types.ContentType.VIDEO_CHAT_PARTICIPANTS_INVITED,
                                   types.ContentType.FORUM_TOPIC_EDITED, types.ContentType.GENERAL_FORUM_TOPIC_HIDDEN,
                                   types.ContentType.GENERAL_FORUM_TOPIC_UNHIDDEN,
                                   types.ContentType.WRITE_ACCESS_ALLOWED])
async def incorrect_text(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return await message.answer('🚫 Нотўғри форматдаги белги киритили. Илтимос ботни /start буйруғи ёрдамида '
                                    'қайтадан ишга туширинг')
    elif current_state == 'User:user_name':
        return await process_user_name_invalid(message)
    elif current_state == 'User:request_type':
        return await process_request_type_invalid(message)
    elif current_state == 'User:request_content':
        return await process_request_content_invalid(message)
    else:
        return await message.answer('‼️Тизим носозлиги! Қайтадан уриниб кўринг! /start')


@dp.message_handler(state=User.user_contact,
                    content_types=[types.ContentType.AUDIO, types.ContentType.ANIMATION, types.ContentType.DOCUMENT,
                                   types.ContentType.GAME, types.ContentType.PHOTO, types.ContentType.STICKER,
                                   types.ContentType.VIDEO, types.ContentType.VIDEO_NOTE, types.ContentType.VOICE,
                                   types.ContentType.VENUE, types.ContentType.LOCATION, types.ContentType.POLL,
                                   types.ContentType.DICE, types.ContentType.NEW_CHAT_MEMBERS,
                                   types.ContentType.LEFT_CHAT_MEMBER, types.ContentType.INVOICE,
                                   types.ContentType.SUCCESSFUL_PAYMENT, types.ContentType.CONNECTED_WEBSITE,
                                   types.ContentType.MESSAGE_AUTO_DELETE_TIMER_CHANGED,
                                   types.ContentType.MIGRATE_FROM_CHAT_ID, types.ContentType.MIGRATE_TO_CHAT_ID,
                                   types.ContentType.PINNED_MESSAGE, types.ContentType.NEW_CHAT_TITLE,
                                   types.ContentType.NEW_CHAT_PHOTO, types.ContentType.DELETE_CHAT_PHOTO,
                                   types.ContentType.GROUP_CHAT_CREATED, types.ContentType.PASSPORT_DATA,
                                   types.ContentType.PROXIMITY_ALERT_TRIGGERED, types.ContentType.VOICE_CHAT_SCHEDULED,
                                   types.ContentType.VOICE_CHAT_STARTED, types.ContentType.VOICE_CHAT_ENDED,
                                   types.ContentType.VOICE_CHAT_PARTICIPANTS_INVITED, types.ContentType.WEB_APP_DATA,
                                   types.ContentType.FORUM_TOPIC_CREATED, types.ContentType.FORUM_TOPIC_CLOSED,
                                   types.ContentType.FORUM_TOPIC_REOPENED, types.ContentType.VIDEO_CHAT_SCHEDULED,
                                   types.ContentType.VIDEO_CHAT_STARTED, types.ContentType.VIDEO_CHAT_ENDED,
                                   types.ContentType.VIDEO_CHAT_PARTICIPANTS_INVITED,
                                   types.ContentType.FORUM_TOPIC_EDITED, types.ContentType.GENERAL_FORUM_TOPIC_HIDDEN,
                                   types.ContentType.GENERAL_FORUM_TOPIC_UNHIDDEN,
                                   types.ContentType.WRITE_ACCESS_ALLOWED])
async def incorrect_user_contact(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == 'User:user_contact':
        return await process_user_contact_text_invalid(message)
    else:
        return await message.answer('‼️Тизим носозлиги! Қайтадан уриниб кўринг! /start')


@dp.message_handler(state=User.request_add,
                    content_types=[types.ContentType.ANIMATION, types.ContentType.GAME, types.ContentType.STICKER,
                                   types.ContentType.POLL, types.ContentType.DICE, types.ContentType.NEW_CHAT_MEMBERS,
                                   types.ContentType.LEFT_CHAT_MEMBER, types.ContentType.INVOICE,
                                   types.ContentType.SUCCESSFUL_PAYMENT, types.ContentType.CONNECTED_WEBSITE,
                                   types.ContentType.MESSAGE_AUTO_DELETE_TIMER_CHANGED,
                                   types.ContentType.MIGRATE_FROM_CHAT_ID, types.ContentType.MIGRATE_TO_CHAT_ID,
                                   types.ContentType.PINNED_MESSAGE, types.ContentType.NEW_CHAT_TITLE,
                                   types.ContentType.NEW_CHAT_PHOTO, types.ContentType.DELETE_CHAT_PHOTO,
                                   types.ContentType.GROUP_CHAT_CREATED, types.ContentType.PASSPORT_DATA,
                                   types.ContentType.PROXIMITY_ALERT_TRIGGERED, types.ContentType.VOICE_CHAT_SCHEDULED,
                                   types.ContentType.VOICE_CHAT_STARTED, types.ContentType.VOICE_CHAT_ENDED,
                                   types.ContentType.VOICE_CHAT_PARTICIPANTS_INVITED, types.ContentType.WEB_APP_DATA,
                                   types.ContentType.FORUM_TOPIC_CREATED, types.ContentType.FORUM_TOPIC_CLOSED,
                                   types.ContentType.FORUM_TOPIC_REOPENED, types.ContentType.VIDEO_CHAT_SCHEDULED,
                                   types.ContentType.VIDEO_CHAT_STARTED, types.ContentType.VIDEO_CHAT_ENDED,
                                   types.ContentType.VIDEO_CHAT_PARTICIPANTS_INVITED,
                                   types.ContentType.FORUM_TOPIC_EDITED, types.ContentType.GENERAL_FORUM_TOPIC_HIDDEN,
                                   types.ContentType.GENERAL_FORUM_TOPIC_UNHIDDEN,
                                   types.ContentType.WRITE_ACCESS_ALLOWED])
async def incorrect_request_add(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == 'User:request_add':
        return await process_request_add_invalid(message)
    else:
        return await message.answer('‼️Тизим носозлиги! Қайтадан уриниб кўринг! /start')


@dp.message_handler(lambda message: False in list(numpy.isin(list(message.text), english_alphabet)),
                    state=User.user_name)
async def process_user_name_invalid(message: types.Message):
    return await message.answer('🚫 Исм, фамилия ёки шарифингиз нотўғри форматда киритилди. Илтимос қайтадан киритинг:',
                                reply_markup=ReplyKeyboardRemove())


@dp.message_handler(state=User.user_name, content_types=types.ContentType.TEXT)
async def process_user_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['user_name'] = message.text
    await User.next()
    await message.answer('Илтимос, сиз билан боғланиш учун Телефон рақамингизни киритинг, ёки қуйидаги тугмани босинг:',
                         reply_markup=user_contact_markup)


@dp.message_handler(lambda message: not (message.text[0:4] == '+998' and len(message.text) == 13
                                         and message.text[1:13].isdigit()), state=User.user_contact)
async def process_user_contact_text_invalid(message: types.Message):
    return await message.answer('🚫 Илтимос телефон рақамингизни тўғри форматда киритинг, ёки қуйидаги тугмани босинг!',
                                reply_markup=user_contact_markup)


@dp.message_handler(state=User.user_contact, content_types=types.ContentType.TEXT)
async def process_user_contact_text(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['user_contact'] = message.text
    await User.next()
    await message.answer('Илтимос мурожаат турини танланг:', reply_markup=request_type_markup)


@dp.message_handler(lambda message: not (message.contact.phone_number[0:4] == '+998'
                                         and len(message.contact.phone_number) == 13
                                         and message.contact.phone_number[1:13].isdigit()), state=User.user_contact)
async def process_user_contact_object_invalid(message: types.Message):
    return await message.answer('🚫 Илтимос телефон рақамингизни тўғри форматда киритинг, ёки қуйидаги тугмани босинг!',
                                reply_markup=user_contact_markup)


@dp.message_handler(state=User.user_contact, content_types=types.ContentType.CONTACT)
async def process_user_contact_object(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['user_contact'] = message.contact.phone_number
    await User.next()
    await message.answer('Илтимос мурожаат турини танланг:', reply_markup=request_type_markup)


@dp.message_handler(lambda message: message.text not in ['📝 Таклиф', '‼️ Шикоят', '💼 Ариза', 'Бошқа'],
                    state=User.request_type)
async def process_request_type_invalid(message: types.Message):
    return await message.answer('🚫 Илтимос фақатгина қуйидаги келтирилган тугмалардан бирини танланг!',
                                reply_markup=request_type_markup)


@dp.message_handler(state=User.request_type, content_types=types.ContentType.TEXT)
async def process_request_type(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['request_type'] = message.text
    await User.next()
    await message.answer('Илтимос мурожаатингизни матн кўринишида киритинг:', reply_markup=ReplyKeyboardRemove())


@dp.message_handler(lambda message: message.text == '#$@**#@&$@)$(%*&^@#^%$@^&%$*@', state=User.request_content)
async def process_request_content_invalid(message: types.Message):
    return await message.answer('🚫 Нотўғри белги киритилди. Мурожаат фақатгина матн кўринишида киритилиши керак.',
                                reply_markup=ReplyKeyboardRemove())


@dp.message_handler(state=User.request_content, content_types=types.ContentType.ANY)
async def process_request_content(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['request_content'] = message.text
    await User.next()
    await message.answer('Агарда қўшимча файл ёки материалларингиз бўлса киритинг, ёки қуйидаги тугмани босинг, '
                         'ва мурожаатингзини якунланг.', reply_markup=request_add_markup)


@dp.message_handler(lambda message: message.text != '🙅‍♂️ Қўшимча иловаларим йўқ', state=User.request_add)
async def process_request_add_invalid(message: types.Message):
    return await message.answer('‼️Сиз киритган маълумот формати қабул қилинмайди.\nФақатгина файл, расм, аудио ва '
                                'шунга ўхшаш қўшимча маълумотларни юклашингиз мумкин.')


@dp.message_handler(state=User.request_add, content_types=types.ContentType.ANY)
async def process_request_add(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['user_id'] = message.from_user.id
        data['request_number'] = None
        if message.text == '🙅‍♂️ Қўшимча иловаларим йўқ':
            data['request_add_type'] = None
            data['request_add'] = None
        elif message.content_type in message_types:
            data['request_add_type'] = message.content_type
            if message.content_type == 'audio':
                data['request_add'] = message.audio.file_id
            elif message.content_type == 'document':
                data['request_add'] = message.document.file_id
            elif message.content_type == 'photo':
                data['request_add'] = message.photo[-1].file_id
            elif message.content_type == 'video':
                data['request_add'] = message.video.file_id
            elif message.content_type == 'video_note':
                data['request_add'] = message.video_note.file_id
            elif message.content_type == 'voice':
                data['request_add'] = message.voice.file_id
            elif message.content_type == 'contact':
                contact_information = [str(message.contact.phone_number), str(message.contact.first_name),
                                       str(message.contact.last_name), str(message.contact.vcard),
                                       str(message.contact.user_id)]
                contact_information_string = ','.join(contact_information)
                data['request_add'] = contact_information_string
            elif message.content_type == 'location':
                location_information = [str(message.location.latitude), str(message.location.longitude)]
                location_information_string = ','.join(location_information)
                data['request_add'] = location_information_string
        else:
            await message.answer('‼️Тизим носозлиги! Қайтадан уриниб кўринг! /start')
        data['request_datetime'] = datetime.datetime.now().strftime("%H:%M:%S,%d-%m-%Y")
    await db.add_application(state)
    async with state.proxy() as data:
        number = await db.get_request_id(state)
        if number:
            data['request_number'] = 100000 + number
        else:
            await message.answer('‼️Тизим носозлиги! Қайтадан уриниб кўринг! /start')
            await state.finish()
    async with state.proxy():
        await db.set_request_number(state)
    async with state.proxy():
        result = await db.get_all_results(state)
        await bot.send_message(message.chat.id, f'✅ Мурожаатингиз қабул қилинди!\nСизнинг мурожаат рақамингиз: '
                                                f'<b><i>{result[5]}</i></b>\n🙍 Мутахассисларимиз сиз билан тез орада '
                                                f'боғланишади!', reply_markup=ReplyKeyboardRemove(), parse_mode='html')
        await bot.send_message(moderator_chat_id, f'{result[4]}\n🔖 <b><i>Мурожаат рақами:</i> {result[5]}</b>\n'
                                                  f'🙎 <b><i>ФИШ:</i> {result[2]}</b>\n☎️ <b><i>Телефон тақами:</i> '
                                                  f'{result[3]}</b>\n📋 <b><i>Мурожаат матни:</i></b>\n{result[6]}\n'
                                                  f'📎 <b><i>Қўшимча материал:</i></b>',
                               reply_markup=ReplyKeyboardRemove(), parse_mode='html')
        if result[7] is None and result[8] is None:
            await bot.send_message(moderator_chat_id, 'Қўшимча материал <b><i>ЙЎҚ</i></b>',
                                   reply_markup=ReplyKeyboardRemove(), parse_mode='html')
        elif result[8] == 'audio':
            await bot.send_audio(moderator_chat_id, result[7], reply_markup=ReplyKeyboardRemove())
        elif result[8] == 'document':
            await bot.send_document(moderator_chat_id, result[7], reply_markup=ReplyKeyboardRemove())
        elif result[8] == 'photo':
            await bot.send_photo(moderator_chat_id, result[7], reply_markup=ReplyKeyboardRemove())
        elif result[8] == 'video':
            await bot.send_video(moderator_chat_id, result[7], reply_markup=ReplyKeyboardRemove())
        elif result[8] == 'video_note':
            await bot.send_video_note(moderator_chat_id, result[7], reply_markup=ReplyKeyboardRemove())
        elif result[8] == 'voice':
            await bot.send_voice(moderator_chat_id, result[7], reply_markup=ReplyKeyboardRemove())
        elif result[8] == 'contact':
            contact_separated = result[7].split(",")
            await bot.send_contact(moderator_chat_id, contact_separated[0], contact_separated[1], contact_separated[2],
                                   contact_separated[3], reply_markup=ReplyKeyboardRemove())
        elif result[8] == 'location':
            location_separated = result[7].split(",")
            await bot.send_location(moderator_chat_id, location_separated[0], location_separated[1],
                                    reply_markup=ReplyKeyboardRemove())
        else:
            await message.answer('‼️Тизим носозлиги! Қайтадан уриниб кўринг! /start')
    await state.finish()


# if __name__ == '__main__':
#     executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
if __name__ == '__main__':
    app.run()
