import app  # Replace with your actual application
import serverless_wsgi
from apis.controllers import DataCollectorController

# If you need to send additional content types as text, add then directly
# to the whitelist:
#
# serverless_wsgi.TEXT_MIME_TYPES.append("application/custom+json")


def handler(event, context):
    return serverless_wsgi.handle_request(app.app, event, context)


def data_collector_handler(event, context):
    with app.app_context():
        DataCollectorController.handle()
