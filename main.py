import paramiko


def fetch_logs_stealthily(target_ip, port, username, password, log_path):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(hostname=target_ip, port=port, username=username, password=password, timeout=5)
        # Читаем последние 1000 строк, чтобы не положить RAM гигабайтным файлом
        stdin, stdout, stderr = client.exec_command(f'tail -n 1000 {log_path}')

        logs_in_memory = stdout.read().decode('utf-8')
        error_output = stderr.read().decode('utf-8')

        if error_output:
            print(f"Ошибка чтения: {error_output}")
            return None

        print(f"[+] Успешно выгружено в RAM: {len(logs_in_memory)} символов.")
        return logs_in_memory

    except Exception as e:
        print(f"[-] Сбой подключения к источнику: {e}")
        return None
    finally:
        client.close()


def forward_logs_from_memory(dest_ip, port, username, password, logs_data, dest_path):
    """Переброска логов напрямую из RAM в файл на сервере-приемнике по SSH"""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(hostname=dest_ip, port=port, username=username, password=password, timeout=5)
        stdin, stdout, stderr = client.exec_command(f'cat >> {dest_path}')

        # Пишем данные прямо в стандартный поток ввода (stdin) удаленного процесса
        stdin.write(logs_data)
        stdin.channel.shutdown_write()

        error_output = stderr.read().decode('utf-8')
        if error_output:
            print(f"[-] Ошибка записи на приемник: {error_output}")
        else:
            print(f"[+] Логи скрытно доставлены на {dest_ip}:{dest_path}")

    except Exception as e:
        print(f"[-] Сбой подключения к приемнику: {e}")
    finally:
        client.close()


if __name__ == "__main__":
    logs = fetch_logs_stealthily('host-server', 22, 'root', 'root', '/var/log/fake_auth.log')
    if logs:
        print(f"Содержимое в памяти: {logs.strip()}")
        # Для теста отправляем в другой файл (или на второй контейнер-приемник)
        forward_logs_from_memory('host-server', 22, 'root', 'root', logs, '/var/log/collected.log')