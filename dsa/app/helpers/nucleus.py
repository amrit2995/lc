import requests
from config.configs import NUCLEUS


class Nucleus:

    def get(env, applicationName='', scope='', nucleusHash='', getConfigurationApi=''):

        getConfigurationApi = (NUCLEUS['host'][env] + NUCLEUS['uri']['getConfig']).replace('{applicationName}',applicationName)\
            .replace('{scopeName}',scope)

        headers = {
            "Authorization":nucleusHash
        }

        response = requests.get(url=getConfigurationApi, headers=headers)

        return response.json()


