import logging
import os
from app import create_app


logging.basicConfig(level=logging.DEBUG)
config_file = os.path.abspath(os.path.join(os.path.realpath(__file__), os.path.pardir, "config.py"))


app = create_app(config_file)


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port="80"
    )
