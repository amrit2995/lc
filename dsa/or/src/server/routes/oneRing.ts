import {
    getAllAdvertisers,
    getBrandsByVbuIds,
} from '../handlers/advertiserHandler'
import getNotifications from '../handlers/notificationHandler'
import {getNucleusConfig} from '../handlers/nucleusHandler'
import {findUser, getMFEUserInfo} from '../handlers/userHandler'
import {
    editUserVendorMapping,
    findUserAndAdvertiserVendorMapping,
} from '../handlers/vendorMappingHandler'
import {injectSessionInCookieAndRefreshIfNeededHandler} from '../proxyMiddleware/handler'
import {
    postRemedyTicketHandler,
    getRemedyTicketsHandler,
} from '../handlers/remedyTicketHandler'

const basePath = process.env.BASE_PATH

export default [
    {
        method: 'GET',
        path: `${basePath}/onering/notifications`,
        handler: getNotifications,
    },
    {
        method: 'GET',
        path: `${basePath}/onering/nucleus`,
        handler: getNucleusConfig,
    },
    {
        method: 'GET',
        path: `${basePath}/onering/advertisers`,
        handler:
            injectSessionInCookieAndRefreshIfNeededHandler(getAllAdvertisers),
    },
    {
        method: 'GET',
        path: `${basePath}/onering/vendorMapping/:vbuId/user/:userId`,
        handler: injectSessionInCookieAndRefreshIfNeededHandler(
            findUserAndAdvertiserVendorMapping,
        ),
    },
    {
        method: 'POST',
        path: `${basePath}/onering/brandsVbu`,
        handler:
            injectSessionInCookieAndRefreshIfNeededHandler(getBrandsByVbuIds),
    },
    {
        method: 'GET',
        path: `${basePath}/onering/findUser/:userId`,
        handler: injectSessionInCookieAndRefreshIfNeededHandler(findUser),
    },
    {
        method: 'POST',
        path: `${basePath}/onering/user/update-vendor-mapping`,
        handler: injectSessionInCookieAndRefreshIfNeededHandler(
            editUserVendorMapping,
        ),
    },
    {
        method: 'GET',
        path: `${basePath}/onering/:sessionToken/userinfo`,
        handler: getMFEUserInfo,
    },
    {
        method: 'POST',
        path: `${basePath}/onering/remedy`,
        handler: postRemedyTicketHandler,
    },
    {
        method: 'GET',
        path: `${basePath}/onering/remedy`,
        handler: getRemedyTicketsHandler,
    },
]
