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
    # Core
    Validator("debug", default=False, is_type_of=bool),
    # slixmpp
    Validator("xmpp_jid", is_type_of=str, required=True),
    Validator("xmpp_password", is_type_of=str, required=True),
    Validator(
        "xmpp_resource",
        is_type_of=str,
        required=True,
        apply_default_on_none=True,
        default="jabbot",
    ),
    # Scheduler
    Validator(
        "scheduler_timezone",
        is_type_of=str,
        required=True,
        apply_default_on_none=True,
        default="Europe/Moscow",
    ),
    Validator(
        "coalesce",
        apply_default_on_none=True,
        default=False,
        is_type_of=bool,
    ),
    Validator(
        "max_instances",
        apply_default_on_none=True,
        default=10,
        is_type_of=int,
        required=True,
    ),
    Validator(
        "misfire_grace_time",
        apply_default_on_none=True,
        default=3600,
        is_type_of=int,
        required=True,
    ),
)

try:
    settings.validators.validate_all()
except ValidationError as e:
    logging.error(e.message)
