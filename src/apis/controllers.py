from apis.usecases import fetch_and_store_data


class DataCollectorController:
    def __init__(self):
        pass

    @classmethod
    def handle(cls):
        fetch_and_store_data()
