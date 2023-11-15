import json
import re
import smtplib
import time
from email.mime.text import MIMEText

from aiogram.filters import BaseFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from config import load_config, Config

with open("data.json", "r", encoding="utf8") as json_file:
    data = json.load(json_file)

# Загружаем конфиг в переменную config
config: Config = load_config('.env')  # добавляем путь перед . если надо

# словарь для хранения языков пользователей и времени последнего репорта
users = {}


class UsersReport(StatesGroup):
    # Класс опросник, сюда вписываются данные которые вводит пользователь
    enter_name = State()
    enter_email = State()
    enter_game = State()
    enter_report = State()


class IsValidEmail(BaseFilter):
    # рукописный фильтр проверяющий сообщение на валидность почты
    def is_valid_email(self, email: str) -> bool:
        """
        функция проверки почты
        :param email: строка введенная для проверки на валидность
        :return: булевое значение валидности почты
        """
        email_pattern = data["email_pattern"]

        # Используем метод match для проверки соответствия ввода регулярному выражению
        if re.match(email_pattern, email):
            return True
        return False

    async def __call__(self, message: Message) -> bool:
        return self.is_valid_email(message.text)


def time_check(time_report: float) -> bool:
    """
    Проверка времени от последнего репорта
    :param time_report: время последнего репорта
    :return: True or False
    """
    return time.time() - time_report > 600


def time_display(t: float) -> str:
    """
    преобразование float в формат времени (минуты-секунды)
    :param t: float от time
    :return: формат '--m:--s'
    """
    minutes = int(t // 60)  # Получаем полные минуты
    seconds = int(t % 60)  # Получаем остаток в секундах
    return f"{minutes:02d}m:{seconds:02d}s"


def make_row_keyboard(items: list[str], text: str = None) -> ReplyKeyboardMarkup:
    """
    Создаёт реплай-клавиатуру с кнопками ряд по 2шт/3шт если количество кратно 2, 3 соответственно
    :param text: сообщение для параметра input_field_placeholder
    :param items: список текстов для кнопок
    :return: объект реплай-клавиатуры
    """
    btns: ReplyKeyboardBuilder = ReplyKeyboardBuilder()
    gms = [KeyboardButton(text=item) for item in items]

    btns.row(*gms, width=2) if not len(gms) % 2 else btns.row(*gms, width=3)

    return btns.as_markup(one_time_keyboard=True, resize_keyboard=True,
                          input_field_placeholder=text)


def send_email(subject: str, message: str) -> bool:
    """
    Функция отправляет сообщение с одной почты на другую
    :param subject: тема письма
    :param message: тело письма
    :return: булевый эквивалент итога отправки
    """
    sender_email = config.db.sender_email  # почта для отправки сообщений
    sender_password = config.db.sender_password  # пароль для почты для отправки сообщений
    recipient_email = config.db.recipient_email  # почта для принятия сообщений

    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = recipient_email

    try:
        server = smtplib.SMTP('smtp.yandex.com', 587)  # адрес почтового сервиса Яндекс, порт 587 для шифрования TLS
        server.starttls()  # Устанавливаем соединение с сервером
        server.login(sender_email, sender_password)  # аутентификация на сервере
        server.sendmail(sender_email, recipient_email, msg.as_string())  # фактическая отправка электронного письма
        server.quit()  # закрывам соединение с сервером
        return True
    except Exception as error:
        print("Error sending email:", str(error))  # вывод ошибки
        return False
