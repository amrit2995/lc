from martech_sdk.utils import logging

class Adapter:
    @staticmethod
    def env(env, service='service', **kwargs):
        if env == 'stage':
            logging.info(f"Env is stage. Changing it to Prod to hit {service}.")
            env = 'prod'
        logging.info(f"Env after Adapter: {env}")
        return env