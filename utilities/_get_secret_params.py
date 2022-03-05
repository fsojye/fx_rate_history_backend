import logging
import subprocess

SECRETS_FILE = '.env.secret'
CONFIG_FILE = '.env'


def main():
    logging.basicConfig(level=logging.INFO)
    client = SecretsClient()
    with open(CONFIG_FILE, 'w') as config_file:
        with open(SECRETS_FILE, 'r') as secrets_file:
            while line_ := secrets_file.readline():
                k, v = line_.rstrip().split(' = ', 1)
                logging.info(f'Writing {k} value to {CONFIG_FILE}')
                ssm_key = v.split('sls://', 1)
                if len(ssm_key) == 2:
                    v = client.get_parameter(ssm_key[-1])
                config_file.write(f'{k} = {v}\n')


class SecretsClient:
    def __init__(self):
        pass

    def _client(self, key):
        _command = "npx sls param get --name"
        return subprocess.run(_command.split(' ') + [key, "/dev/null"], capture_output=True)

    def get_parameter(self, key):
        logging.info(f"Retrieving [{key}] value from sls")
        return self._client(key).stdout.decode().strip()


if __name__ == "__main__":
    main()
