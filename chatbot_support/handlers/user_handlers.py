import time

from aiogram import F
from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from untils.until import UsersReport, IsValidEmail, make_row_keyboard, time_check, send_email, \
    time_display, data, users

rt: Router = Router()


# обработака ботом команды /start
@rt.message(Command("start"), F.text)
async def process_start_command(message: Message):
    # добавляем в словарь users язык пользователя, а так же сразу время последнего репорта=0
    if message.from_user.id not in users:
        if message.from_user.language_code == 'ru':
            users[message.from_user.id] = {'language': 'ru', 'time_of_report': 0}
        else:
            users[message.from_user.id] = {'language': 'en', 'time_of_report': 0}
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text=f"{data[users[message.from_user.id]['language']]['process_start_command']['btn_1']}",
        callback_data="start of the survey"))
    builder.row(InlineKeyboardButton(
        text=data[users[message.from_user.id]['language']]['process_start_command']['btn_2'],
        url=data["siteUrl"]))
    await message.answer(
        data[users[message.from_user.id]['language']]['process_start_command']['start of the survey'],
        reply_markup=builder.as_markup())


# обработака ботом нажатие кнопки начала опроса
@rt.callback_query(F.data == "start of the survey")
async def ent_name(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(data[users[callback.from_user.id]['language']]['questions']['name'])
    await state.set_state(UsersReport.enter_name)


# обработака ботом ввода имени
@rt.message(UsersReport.enter_name)
async def name_entered(message: Message, state: FSMContext):
    await state.update_data(name=message.text.title())
    await message.answer(data[users[message.from_user.id]['language']]['questions']['email'])
    await state.set_state(UsersReport.enter_email)


# обработака ботом ввода почты
@rt.message(UsersReport.enter_email, IsValidEmail())
async def email_entered(message: Message, state: FSMContext):
    await state.update_data(email=message.text)
    await message.answer(data[users[message.from_user.id]['language']]['questions']['game'],
                         reply_markup=make_row_keyboard(data['games'],
                                                        text=data[users[message.from_user.id]['language']][
                                                            'input_field_placeholder']))
    await state.set_state(UsersReport.enter_game)


# обработака ботом ввода не правильного формата почты
@rt.message(UsersReport.enter_email)
async def food_chosen_incorrectly(message: Message):
    await message.answer(
        text=data[users[message.from_user.id]['language']]['email_error'])


# обработака ботом ввода названия игры
@rt.message(UsersReport.enter_game, F.text)
async def game_entered(message: Message, state: FSMContext):
    await state.update_data(game=message.text.title())
    await message.answer(data[users[message.from_user.id]['language']]['questions']['report'])
    await state.set_state(UsersReport.enter_report)


# обработака ботом ввода репорта
@rt.message(UsersReport.enter_report, F.text)
async def report_entered(message: Message, state: FSMContext):
    await state.update_data(report=message.text.title())
    user_data = await state.get_data()
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text=data[users[message.from_user.id]['language']]['report_entered']['btn_1'],
        callback_data="sending a report"))
    builder.row(InlineKeyboardButton(
        text=data[users[message.from_user.id]['language']]['report_entered']['btn_2'],
        callback_data="start of the survey"))

    await message.answer(
        f"<b>{data[users[message.from_user.id]['language']]['report_entered']['name_tabl']}</b>\n"
        f"<b>Name:</b> {user_data['name']}\n"
        f'<b>Email:</b> {user_data["email"]}\n'
        f"<b>Game:</b> {user_data['game']}\n"
        f"<b>Bug description:</b> {user_data['report']}",
        reply_markup=builder.as_markup())


# обработака ботом кнопки подтверждения отправки репорта
@rt.callback_query(F.data == "sending a report")
async def final(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    time_last_report = users[callback.from_user.id].get('time_of_report', 0)
    time_left = 600 - (time.time() - time_last_report)
    email_subject = f"Message from user {callback.from_user.id}"  # тема письма
    email_message = f'''
                    Name: {user_data['name']}\n
                    Email: {user_data["email"]}\n
                    Game: {user_data['game']}\n
                    Bug description: {user_data['report']}
                    '''

    # тело письма
    # вывод ответа пользователю если send_email отработала/не отработала
    if time_check(time_last_report) and send_email(email_subject, email_message):
        users[callback.from_user.id]["time_of_report"] = time.time()
        await callback.answer(
            text=f"{data[users[callback.from_user.id]['language']]['final']['text_ok']}",
            show_alert=True)
    elif not time_check(time_last_report):
        await callback.answer(
            text=f"{data[users[callback.from_user.id]['language']]['final']['text_time']} {time_display(time_left)}",
            show_alert=True)
    else:
        await callback.answer(
            text=data[users[callback.from_user.id]['language']]['final']['text_no_ok'], show_alert=True)


# обработака ботом ввода неправильного формата сообщения
@rt.message()
async def any_message(message: Message):
    await message.reply(text=data[users[message.from_user.id]['language']]['wrong_format'])
