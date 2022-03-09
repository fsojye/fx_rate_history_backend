import json
import sys

sys.path.insert(0, 'src')  # noqa

from app import api, app  # noqa

app.config['SERVER_NAME'] = ''

with app.app_context():
    file_ = sys.argv[1]
    with open(file_, 'w') as f:
        json.dump(json.loads(json.dumps(api.__schema__)), f, indent=2)
