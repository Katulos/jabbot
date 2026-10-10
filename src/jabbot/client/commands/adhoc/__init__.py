import importlib.util
import logging
import os
import sys
from abc import ABC, abstractmethod
from collections.abc import Callable
from pathlib import Path
from typing import Any


class BaseAdhocCommand(ABC):
    @property
    @abstractmethod
    def node(self) -> str:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    def description(self) -> str:
        return ""

    @abstractmethod
    async def execute_initial(self, iq: Any, session: dict) -> dict:
        pass

    @abstractmethod
    async def execute_complete(
        self,
        payload: Any,
        session: dict,
    ) -> dict | None:
        pass

    async def execute_cancel(self, session: dict) -> dict | None:
        return None


class AdhocCommandRegistry:
    _instance = None
    _commands: dict[str, dict] = {}
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_instance(cls) -> "AdhocCommandRegistry":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def load_commands(
        self,
        client: Any,
        commands_dir: str = os.path.dirname(__file__),
    ) -> None:
        if self._initialized:
            logging.warning("Adhoc commands already loaded")
            return

        commands_path = Path(commands_dir)

        if not commands_path.exists():
            logging.error(f"Commands directory not found: {commands_dir}")
            return

        package_name = __name__
        if package_name not in sys.modules:
            sys.modules[package_name] = sys.modules[__name__]

        if "commands" not in sys.modules:
            sys.modules["commands"] = sys.modules[__name__]

        command_files = [
            f
            for f in commands_path.glob("*.py")
            if f.stem != "__init__" and not f.stem.startswith("_")
        ]

        loaded_count = 0
        for file_path in command_files:
            try:
                module_name = f"{__name__}.{file_path.stem}"

                spec = importlib.util.spec_from_file_location(
                    module_name,
                    str(file_path),
                )
                if spec is None or spec.loader is None:
                    logging.error(f"Failed to create spec for {file_path}")
                    continue

                module = importlib.util.module_from_spec(spec)

                module.__package__ = __name__

                sys.modules[module_name] = module
                spec.loader.exec_module(module)

                for attr_name in dir(module):
                    attr = getattr(module, attr_name)

                    if (
                        isinstance(attr, type)
                        and issubclass(attr, BaseAdhocCommand)
                        and attr is not BaseAdhocCommand
                    ):
                        command_instance = attr()

                        initial_handler = self._create_initial_handler(
                            client,
                            command_instance,
                        )
                        complete_handler = self._create_complete_handler(
                            client,
                            command_instance,
                        )
                        cancel_handler = self._create_cancel_handler(
                            client,
                            command_instance,
                        )

                        client["xep_0050"].add_command(
                            node=command_instance.node,
                            name=command_instance.name,
                            handler=initial_handler,
                        )

                        self._commands[command_instance.node] = {
                            "instance": command_instance,
                            "complete_handler": complete_handler,
                            "cancel_handler": cancel_handler,
                        }

                        loaded_count += 1
                        logging.info(
                            f"Loaded Adhoc command: {command_instance.name} (node: {command_instance.node})",
                        )

            except Exception as e:
                logging.error(
                    f"Error loading command from file {file_path}: {e}",
                    exc_info=True,
                )

        self._initialized = True
        logging.info(f"Total Adhoc commands loaded: {loaded_count}")

    def _create_initial_handler(
        self,
        client: Any,
        command: BaseAdhocCommand,
    ) -> Callable:

        async def handler(iq: Any, session: dict) -> dict:
            try:
                session["_client"] = client

                command_data = self._commands.get(command.node, {})
                session["_complete_handler"] = command_data.get(
                    "complete_handler",
                )
                session["_cancel_handler"] = command_data.get(
                    "cancel_handler",
                )

                result = await command.execute_initial(iq, session)

                return result
            except Exception as e:
                logging.error(
                    f"Error in execute_initial for command {command.node}: {e}",
                    exc_info=True,
                )
                session["notes"] = [
                    ("error", f"Command execution error: {str(e)}"),
                ]
                return session

        return handler

    def _create_complete_handler(
        self,
        client: Any,
        command: BaseAdhocCommand,
    ) -> Callable:

        async def handler(payload: Any, session: dict) -> dict | None:
            try:
                result = await command.execute_complete(payload, session)
                return result
            except Exception as e:
                logging.error(
                    f"Error in execute_complete for command {command.node}: {e}",
                    exc_info=True,
                )
                session["notes"] = [
                    ("error", f"Command execution error: {str(e)}"),
                ]
                return session

        return handler

    def _create_cancel_handler(
        self,
        client: Any,
        command: BaseAdhocCommand,
    ) -> Callable:

        async def handler(session: dict) -> dict | None:
            try:
                result = await command.execute_cancel(session)
                return result
            except Exception as e:
                logging.error(
                    f"Error in execute_cancel for command {command.node}: {e}",
                    exc_info=True,
                )
                return session

        return handler

    def get_command(self, node: str) -> dict | None:
        return self._commands.get(node)

    def get_all_commands(self) -> dict[str, dict]:
        return self._commands.copy()
