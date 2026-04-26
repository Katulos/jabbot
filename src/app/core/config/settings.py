import logging
import os

from dynaconf import Dynaconf, ValidationError, Validator

_BASE_DIR = os.getcwd()


settings = Dynaconf(
    settings_files=[
        "?/etc/jabbot/settings.yml",
        "?/etc/jabbot/.secrets.yml",
        "?~/.config/jabbot/settings.yml",
        "?~/.config/jabbot/.secrets.yml",
        os.path.join(_BASE_DIR, "settings.yml"),
        os.path.join(_BASE_DIR, ".secrets.yml"),
    ],
)

settings.validators.register(
    # debug
    Validator("debug", default=False, is_type_of=bool),
)

try:
    settings.validators.validate_all()
except ValidationError as e:
    logging.error(e.message)
