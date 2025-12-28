ADAPTABLE_APPNAME_SCOPE_PAIR = {
    ('delta', 'dataproc'),
    ('spa-etl-dev', 'mongo-delta-connector')
}

class Adapter:
    @staticmethod
    def env(env, applicationName, scope):
        if env == 'dev':
            pair_to_check = (applicationName, scope)
            return 'dev' if pair_to_check in ADAPTABLE_APPNAME_SCOPE_PAIR else 'stage'
        return env