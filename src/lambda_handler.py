from apis.controllers import DataCollectorController


def data_collector_handler(event, context):
    DataCollectorController.handle()
