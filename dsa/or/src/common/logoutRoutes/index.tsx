import logout from '../components/logout'
import {getBasePath} from '../utils/commonUtils'

const basePath = getBasePath()
const routes = [
    {
        path: `${basePath}/logout`,
        exact: true,
        component: logout,
    },
]

export default routes
