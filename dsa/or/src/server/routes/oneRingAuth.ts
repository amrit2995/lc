import {
    authCallbackHandler,
    authLoginHandler,
    deleteSessionHandler,
    refreshSessionHandler,
    userInfoHandler,
} from '../handlers/authHandlers'
import {getSessionInfo, userOriginHandler} from '../handlers/sessionHandler'
import {injectSessionInCookieAndRefreshIfNeededHandler} from '../proxyMiddleware/handler'

const basePath = process.env.BASE_PATH

export default [
    {
        method: 'GET',
        path: `${basePath}/onering/isEntForgerock`,
        handler: userOriginHandler,
    },
    {
        method: 'GET',
        path: `${basePath}/onering/journey/request`,
        handler: authLoginHandler,
    },
    {
        method: 'POST',
        path: `${basePath}/onering/journey/handle`,
        handler: authCallbackHandler,
    },
    {
        method: 'GET',
        path: `${basePath}/onering/refresh-session`,
        handler: refreshSessionHandler,
    },
    {
        method: 'POST',
        path: `${basePath}/onering/userInfo`,
        handler: userInfoHandler,
    },
    {
        method: 'GET',
        path: `${basePath}/onering/session`,
        handler: injectSessionInCookieAndRefreshIfNeededHandler(getSessionInfo),
    },
    {
        method: 'GET',
        path: `${basePath}/onering/session/delete`,
        handler: deleteSessionHandler,
    },
]
