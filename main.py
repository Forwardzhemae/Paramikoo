import paramiko


def fetch_logs_stealthily(target_ip, port, username, password, log_path):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(hostname=target_ip, port=port, username=username, password=password)

        stdin, stdout, stderr = client.exec_command(f'cat {log_path}')

        logs_in_memory = stdout.read().decode('utf-8')
        error_output = stderr.read().decode('utf-8')

        if error_output:
            print(f"Ошибка чтения: {error_output}")
            return None

        print(f"Успешно выгружено {len(logs_in_memory)} символов.")

        return logs_in_memory

    except Exception as e:
        print(f"Сбой подключения: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    fetch_logs_stealthily('host-server', 22, 'root', 'root', '/var/log/fake_auth.log')