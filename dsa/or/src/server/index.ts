import serverStart, {HMR} from '@<url>/helix-core/dist/server/express'

import PrometheusClient from '@<url>/helix-prometheus-express'

import AppComponent from '../common/app'

PrometheusClient.collectDefaultMetrics()

serverStart({
    RootApp: AppComponent,
    // i18n: getI18Next(serverConfig),
})

if (process.env.NODE_ENV !== 'production' && module.hot) {
    module.hot.accept('../common/app', HMR({RootApp: AppComponent}))
}
