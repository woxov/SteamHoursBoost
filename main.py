import os
import sys
import time
import platform
from getpass import getpass

try:
    from steam.client import SteamClient
except ImportError:
    print("Установка необходимых зависимостей...")
    os.system("pip install -U steam[client]")
    from steam.client import SteamClient


def clear_screen() -> None:
    """Очистка экрана для разных ОС"""
    command = "cls" if platform.system().lower() == "windows" else "clear"
    os.system(command)


def _authenticate_steam(client: SteamClient, username: str, password: str) -> bool:
    """Аутентификация в Steam с поддержкой 2FA"""
    sentry_path = "steam_sentry.bin"
    if os.path.exists(sentry_path):
        client.set_credential_location(sentry_path)

    while True:
        guard_code = input(
            "Введите код Steam Guard (оставьте пустым, если не требуется): "
        )
        result = client.login(
            username=username, password=password, two_factor_code=guard_code
        )
        if result == 1:
            return True
        if result not in (None, "invalid_2fa"):
            print(f"Ошибка входа: код {result}")
            return False
        print("Неверный код. Попробуйте снова.")


def _format_elapsed_time(seconds: int) -> str:
    """Форматирование времени в HH:MM:SS"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def _display_status(username: str, app_id: int, elapsed_seconds: int) -> None:
    """Вывод статуса"""
    clear_screen()
    hours = elapsed_seconds / 3600
    print("╔═══════════════════════════════╗")
    print("║    Steam Idler - Активно      ║")
    print("╚═══════════════════════════════╝")
    print(f"Аккаунт:     {username}")
    print(f"App ID:      {app_id}")
    print(f"Время:       {_format_elapsed_time(elapsed_seconds)}")
    print(f"Часов:       {hours:.2f}h")
    print("\n[Ctrl+C для выхода]")


def steam_idle(username: str, password: str, app_id: int) -> None:
    """Эмуляция игровой сессии для фарма часов"""
    client = SteamClient()

    try:
        if not _authenticate_steam(client, username, password):
            print("Ошибка: не удалось войти в Steam")
            return

        print(f"✓ Успешный вход: {client.user.name}")
        client.games_played([app_id])
        print(f"✓ Фарм начат (App ID: {app_id})\n")

        start_time = time.time()
        last_update = 0
        last_heartbeat = 0

        while True:
            elapsed_time = int(time.time() - start_time)

            if elapsed_time - last_update >= 1:
                _display_status(client.user.name, app_id, elapsed_time)
                last_update = elapsed_time

            if elapsed_time - last_heartbeat >= 30:
                client.games_played([app_id])
                last_heartbeat = elapsed_time

            try:
                client.run_forever(timeout=0.1)
            except:
                pass
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n\nЗавершение работы...")
    except Exception as e:
        print(f"✗ Ошибка: {e}")
    finally:
        client.games_played([])
        client.logout()
        print("✓ Выход из Steam выполнен")


if __name__ == "__main__":
    clear_screen()
    print("╔═══════════════════════════════════════════════════╗")
    print("║      Steam Idler - Программа для фарма часов     ║")
    print("╚═══════════════════════════════════════════════════╝\n")

    username = input("Введите логин Steam: ").strip()
    password = getpass("Введите пароль Steam: ")
    app_id_input = input("Введите App ID игры: ").strip()

    try:
        app_id = int(app_id_input)
        if app_id <= 0:
            raise ValueError("App ID должен быть положительным числом")
    except ValueError as e:
        print(f"✗ Ошибка: {e}")
        sys.exit(1)

    steam_idle(username, password, app_id)
