from dataclasses import dataclass
from environs import Env
from typing import Optional

@dataclass
class DatabaseConfig:
    sender_email: str  # Почта с которой отправляются репорты
    sender_password: str  # Пароль от почты
    recipient_email: str  # Почта на которую отправляются репорты


@dataclass
class TgBot:
    token: str  # Токен для доступа к телеграм-боту


@dataclass
class Config:
    tg_bot: TgBot
    db: DatabaseConfig


def load_config(path: Optional[str]) -> Config:
    env: Env = Env()  # Создаем экземпляр класса Env
    env.read_env(path)  # Добавляем в переменные окружения данные, прочитанные из файла .env
    return Config(tg_bot=TgBot(token=env('BOT_TOKEN')),
                  db=DatabaseConfig(sender_email=env('sender_email'),
                                    sender_password=env('sender_password'),
                                    recipient_email=env('recipient_email')))
