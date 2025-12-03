import Forbidden from '../components/Forbidden'
import {getBasePath} from '../utils/commonUtils'

const basePath = getBasePath()
const routes = [
    {
        path: `${basePath}/403`,
        exact: true,
        component: Forbidden,
    },
]

export default routes
