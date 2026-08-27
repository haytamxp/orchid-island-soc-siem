"""
Application configuration for Orchid Island SOC/SIEM.
"""

import os

from dotenv import load_dotenv


load_dotenv()


def _env_bool(
    name: str,
    default: bool = False,
) -> bool:
    """
    Read a boolean environment variable safely.
    """

    value = os.getenv(
        name,
        str(default),
    )

    return value.lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


class Config:
    """
    Centralized application configuration.
    """

    # ========================================================
    # Application
    # ========================================================

    APP_NAME = os.getenv(
        "APP_NAME",
        "Orchid Island SOC/SIEM",
    )

    FLASK_HOST = os.getenv(
        "FLASK_HOST",
        "0.0.0.0",
    )

    FLASK_PORT = int(
        os.getenv(
            "FLASK_PORT",
            "5000",
        )
    )

    FLASK_DEBUG = _env_bool(
        "FLASK_DEBUG",
        False,
    )

    # ========================================================
    # Database
    # ========================================================

    DB_HOST = os.getenv(
        "DB_HOST",
        "localhost",
    )

    DB_PORT = int(
        os.getenv(
            "DB_PORT",
            "3306",
        )
    )

    DB_NAME = os.getenv(
        "DB_NAME",
        "siem_db",
    )

    DB_USER = os.getenv(
        "DB_USER",
        "siem_user",
    )

    DB_PASSWORD = os.getenv(
        "DB_PASSWORD",
        "",
    )

    # ========================================================
    # Gemini AI
    # ========================================================

    GEMINI_API_KEY = os.getenv(
        "GEMINI_API_KEY",
        "",
    )

    GEMINI_MODEL = os.getenv(
        "GEMINI_MODEL",
        "gemini-3.6-flash",
    )

    # ========================================================
    # Wazuh
    # ========================================================

    WAZUH_MANAGER_URL = os.getenv(
        "WAZUH_MANAGER_URL",
        "",
    )

    WAZUH_API_USER = os.getenv(
        "WAZUH_API_USER",
        "",
    )

    WAZUH_API_PASSWORD = os.getenv(
        "WAZUH_API_PASSWORD",
        "",
    )

    # ========================================================
    # Suricata
    # ========================================================

    SURICATA_EVE_LOG_PATH = os.getenv(
        "SURICATA_EVE_LOG_PATH",
        "/var/log/suricata/eve.json",
    )

    # ========================================================
    # VirusTotal
    # ========================================================

    VIRUSTOTAL_API_KEY = os.getenv(
        "VIRUSTOTAL_API_KEY",
        "",
    )

    # ========================================================
    # Cloudflare
    # ========================================================

    CLOUDFLARE_API_TOKEN = os.getenv(
        "CLOUDFLARE_API_TOKEN",
        "",
    )

    CLOUDFLARE_ZONE_ID = os.getenv(
        "CLOUDFLARE_ZONE_ID",
        "",
    )

    # ========================================================
    # Telegram
    # ========================================================

    TELEGRAM_BOT_TOKEN = os.getenv(
        "TELEGRAM_BOT_TOKEN",
        "",
    )

    TELEGRAM_CHAT_ID = os.getenv(
        "TELEGRAM_CHAT_ID",
        "",
    )

    # ========================================================
    # SMTP
    # ========================================================

    SMTP_HOST = os.getenv(
        "SMTP_HOST",
        "smtp.gmail.com",
    )

    SMTP_PORT = int(
        os.getenv(
            "SMTP_PORT",
            "587",
        )
    )

    SMTP_USERNAME = os.getenv(
        "SMTP_USERNAME",
        "",
    )

    SMTP_PASSWORD = os.getenv(
        "SMTP_PASSWORD",
        "",
    )

    NOTIFICATION_EMAIL = os.getenv(
        "NOTIFICATION_EMAIL",
        "",
    )