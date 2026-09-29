import importlib
import logging
from abc import ABC, abstractmethod
from pathlib import Path

from slixmpp import ClientXMPP


class BaseCommand(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        pass

    @property
    def aliases(self) -> list[str]:
        return []

    @abstractmethod
    async def execute(self, client: ClientXMPP, msg: dict, args: str) -> None:
        pass

    def get_usage(self) -> str:
        return f"/{self.name} - {self.description}"


class CommandRegistry:
    _instance = None
    _commands: dict[str, BaseCommand] = {}
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_instance(cls) -> "CommandRegistry":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def load_commands(self, commands_dir: str | None = None) -> None:
        if self._initialized:
            logging.warning("Commands already loaded")
            return

        if commands_dir is None:
            commands_path = Path(__file__).parent
        else:
            commands_path = Path(commands_dir)

        if not commands_path.exists():
            logging.error(f"Commands directory not found: {commands_path}")
            return

        command_files = [
            f
            for f in commands_path.glob("*.py")
            if f.stem != "__init__" and not f.stem.startswith("_")
        ]

        loaded_count = 0
        for file_path in command_files:
            try:
                module_name = f"{__package__}.{file_path.stem}"

                module = importlib.import_module(module_name)

                for attr_name in dir(module):
                    attr = getattr(module, attr_name)

                    if (
                        isinstance(attr, type)
                        and issubclass(attr, BaseCommand)
                        and attr is not BaseCommand
                    ):
                        command_instance = attr()

                        self._commands[command_instance.name.lower()] = (
                            command_instance
                        )

                        for alias in command_instance.aliases:
                            self._commands[alias.lower()] = command_instance

                        loaded_count += 1
                        logging.info(
                            f"Loaded command: /{command_instance.name}",
                        )

            except Exception as e:
                logging.error(
                    f"Error loading command from file {file_path}: {e}",
                )

        self._initialized = True
        logging.info(f"Total commands loaded: {loaded_count}")

    def get_command(self, command_name: str) -> BaseCommand | None:
        return self._commands.get(command_name.lower())

    def get_all_commands(self) -> dict[str, BaseCommand]:
        return self._commands.copy()

    def get_help_text(self) -> str:
        help_lines = ["Available commands:"]

        seen_commands = set()
        for _cmd_name, command in sorted(self._commands.items()):
            if command.name not in seen_commands:
                help_lines.append(
                    f"  /{command.name} - {command.description}",
                )
                seen_commands.add(command.name)

        return "\n".join(help_lines)


def register_command(command_class: type[BaseCommand]) -> type[BaseCommand]:
    instance = command_class()
    registry = CommandRegistry.get_instance()
    registry._commands[instance.name.lower()] = instance

    for alias in instance.aliases:
        registry._commands[alias.lower()] = instance

    logging.info(f"Registered command: /{instance.name}")
    return command_class
