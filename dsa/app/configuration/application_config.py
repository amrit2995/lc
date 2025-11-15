import os
from typing import Any
import json
import yaml
from yaml import YAMLError
from config.configs import PROFILE, DEFAULT_PROFILE, CONFIG_FILE_PATH, STRING_EMPTY
from helpers.singleton import SingletonMeta
from helpers.common import UtilityClass



def _apply_configs(config_path: str, configs: dict) -> Any:
    applied_config: dict = configs.copy()
    for navigation in config_path.split('.'):
        if applied_config is None:
            return None
        applied_config = applied_config.get(navigation, None)
    return applied_config


class ApplicationConfig(metaclass=SingletonMeta):
    def __init__(self) -> None:
        self._default_configs: dict = {}
        self._profile_configs: dict = {}
        self._secrets_configs: dict = {}
        UtilityClass.handleInfoLogs('Loading Base Configurations from Yaml')
        self._load_configs()
        

    def _load_configs(self) -> None:
        env_name = os.getenv(PROFILE, DEFAULT_PROFILE)
        UtilityClass.handleInfoLogs(f'Active profile : {env_name}')

        try:
            with open(CONFIG_FILE_PATH) as config:
                configs = yaml.safe_load_all(config)
                for attr in configs:
                    if not attr.get(PROFILE, None):
                        self._default_configs = attr
                    elif attr.get(PROFILE) == env_name:
                        self._profile_configs = attr
                        if self._profile_configs and self._profile_configs["secrets_path"]:
                            self._read_secrets(self._profile_configs["secrets_path"])

        except FileNotFoundError as exception:
            UtilityClass.handleErrorLogs(f'FileNotFoundError in Loading the file: {repr(exception)}')
            raise exception
        except YAMLError as exception:
            UtilityClass.handleErrorLogs(f'YAMLError in Loading the file: {repr(exception)}')
            raise exception
        finally:
            config.close()
        
    def _read_secrets(self,secrets_path):
        with open(secrets_path, "r") as file:
            self._secrets_configs = json.load(file)
            os.environ["SECRETS_CONFIG"] = json.dumps(self._secrets_configs)


        

    def parse_config(self, config_path: str) -> Any:
        if config_path is None or config_path == STRING_EMPTY:
            raise ValueError('Config Path Cannot be None')

        env_config = os.getenv(config_path, None)
        return env_config if env_config else self._parse(config_path)
    
    def get_secrets_config(self):
        return self._secrets_configs

    def _parse(self, config_path: str) -> Any:
        default_config = _apply_configs(config_path=config_path, configs=self._default_configs)
        profile_config = _apply_configs(config_path=config_path, configs=self._profile_configs)

        if profile_config is None:
            return default_config
        elif default_config is None:
            return profile_config
        elif isinstance(default_config, dict) and isinstance(profile_config, dict):
            return {**default_config, **profile_config}
        else:
            return profile_config
