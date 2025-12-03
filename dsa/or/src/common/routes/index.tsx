import HelixMfeTemplate from '../components/helixMfeTemplate'
import {getBasePath} from '../utils/commonUtils'
import RedirectComponent from './RedirectComponent'

const basePath = getBasePath()

const routes = [
    {
        path: `${basePath}/`,
        exact: true,
        component: RedirectComponent,
    },
    {
        path: `${basePath}/dashboard`,
        exact: true,
        component: RedirectComponent,
    },
    {
        path: `${basePath}/dashboard/:entity`,
        exact: true,
        component: HelixMfeTemplate,
        scope: 'campaignManager',
    },
    {
        path: `${basePath}/dashboard/:entity/:action`,
        exact: true,
        component: HelixMfeTemplate,
        scope: 'campaignManager',
    },
    {
        path: `${basePath}/dashboard/:entity/:action/:id`,
        exact: true,
        component: HelixMfeTemplate,
        scope: 'campaignManager',
    },
    {
        path: `${basePath}/:entity/:action`,
        exact: true,
        component: HelixMfeTemplate,
        scope: 'campaignManager',
    },
    {
        path: `${basePath}/:entity/:action/:actionTwo`,
        exact: true,
        component: HelixMfeTemplate,
        scope: 'campaignManager',
    },
]

export default routes
