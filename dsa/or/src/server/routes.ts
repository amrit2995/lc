/* eslint-disable import/no-extraneous-dependencies */

import {routes} from '@<url>/helix-prometheus-express'
import {getBasePath} from '../common/utils/commonUtils'
import asset from './routes/asset'
import base from './routes/base'
import oneRing from './routes/oneRing'
import oneRingAuth from './routes/oneRingAuth'
import remedyRoutes from './routes/remedyRoutes'

/**
 * List of routes registered to server
 */

const serverRoutes = [
    ...base, // UI Routes
    ...oneRing, // Routes for oneRing app
    ...oneRingAuth, // token end points
    ...remedyRoutes, // Remedy notification API endpoints
    ...asset, // Icons, and static content
]

const routeConfig = {
    prometheusMetrics: {
        path: `${getBasePath()}/management/prometheus`,
    },
}

serverRoutes.push(...routes(routeConfig))

export default serverRoutes
