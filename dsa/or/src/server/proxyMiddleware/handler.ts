/* eslint-disable no-restricted-syntax */
import FormData from 'form-data'
import {
    AdvertiserDetails,
    ExternalMappings,
    Handler,
    MFEUserDetails,
    OIDCUserToken,
    UserDetails,
    UserInfo,
    UserSession,
} from '../handlers/interfaces/sessionProps'
import {mapUserAdvertiserVendorAccess} from '../handlers/services/loginMapping'
import {onUpdateToken} from '../handlers/sessionHandler'
import {findAll, findAllInObjectId} from '../mongo/client'
import logger from '../plugins/logger'
import {get, set} from '../redis/utils'
import secrets from '../secrets'
import {getAuthorizationFromRequest, isUserAdmin} from '../utils/auth'
import {
    ALLOWED_URLS,
    REDIS_USER_INFO_TAG,
    REDIS_USER_TOKEN_VERSION,
} from '../utils/constants'

const {
    redisTTL: {checkSessionTokenThreshold, userExpiry},
    forgerock,
} = secrets()
const {enterpriseDetails, vendorDetails} = forgerock
const {redirectURL: enterpriseReferrer} = enterpriseDetails
const {redirectURL: vendorReferrer} = vendorDetails

const refreshSession = async (
    request: any,
    hashToken: string,
): Promise<string | null> => {
    try {
        const tokenVersion: number = await get(
            `${REDIS_USER_TOKEN_VERSION}${hashToken}`,
        )
        const userSession: UserSession = await get(hashToken)
        if (tokenVersion && tokenVersion !== userSession.lastUpdatedAt) {
            return hashToken
        }

        const allowedReferrers = [enterpriseReferrer, vendorReferrer]
        const referrer = request?.headers?.referer ?? ''
        const referrerSplit = referrer?.includes('/lormn')
            ? referrer.split('/lormn')[0]
            : ''
        if (!allowedReferrers?.includes(referrerSplit)) {
            request.log.error('Referrer is not allowed:', referrerSplit)
            throw new Error('Unauthorized referrer')
        }

        const oidcUserToken: OIDCUserToken = await onUpdateToken(
            referrerSplit,
            userSession.userId,
            userSession.refreshToken,
            request,
        )
        return oidcUserToken.hashToken
    } catch (error) {
        request.log.error(
            'Error refreshing session token, might have already refreshed',
            error,
        )
        return hashToken
    }
}

const isSessionExpiring = (sessionTimestamp: number): boolean => {
    const now = new Date().getTime()
    const sessionTime = new Date(sessionTimestamp).getTime()
    const diffInSeconds = (now - sessionTime) / 1000
    return diffInSeconds >= checkSessionTokenThreshold
}

const processMFEUserDetails = async (
    userSession: UserSession,
): Promise<MFEUserDetails> => {
    let mfeUserDetails: MFEUserDetails | null = await get(
        `${REDIS_USER_INFO_TAG}${userSession.userId}`,
    )

    if (mfeUserDetails) {
        return mfeUserDetails
    }

    let advertiserList: any[] = []

    const isAdmin = isUserAdmin(userSession)

    if (userSession.isExternalUser) {
        advertiserList = isAdmin
            ? await findAll('advertiser')
            : await findAllInObjectId(
                  'advertiser',
                  '_id',
                  userSession.advertisers,
              )

        if (!advertiserList) {
            advertiserList = []
        }
    }

    const advertiserDetails: AdvertiserDetails[] = advertiserList.map(
        (advertiser) =>
            ({
                id: advertiser.id,
                advertiserName: advertiser.name,
                externalMappings: advertiser.externalMappings
                    ? Object.entries(advertiser.externalMappings).map(
                          ([key, value]) =>
                              ({
                                  source: key,
                                  id: value,
                              } as ExternalMappings),
                      )
                    : [],
                vbuIds: [
                    ...new Set(
                        (advertiser.vbuIds || [])
                            .map((id: string) => (id ? id.split('_')[0] : ''))
                            .filter(Boolean),
                    ),
                ],
                brands: advertiser.brands,
                ...mapUserAdvertiserVendorAccess(userSession, advertiser),
            } as AdvertiserDetails),
    )

    mfeUserDetails = {
        userId: userSession.userId,
        isExternalUser: userSession.isExternalUser,
        horizonRoleName: userSession.horizonRoleName,
        vertexRoleName: userSession.vertexRoleName,
        entSocialRoleName: userSession.entSocialRoleName,
        entEmailRoleName: userSession.entEmailRoleName,
        roleName: userSession.roleName,
        rrdRoleName: userSession.rrdRoleName,
        tenants: userSession.tenants || [],
        advertiserDetails,
        userDetails: userSession.userDetails,
    }

    set(
        `${REDIS_USER_INFO_TAG}${userSession.userId}`,
        mfeUserDetails,
        userExpiry,
    )

    return mfeUserDetails
}

const handlerWithAuth = async (
    req: {
        cookies: {Authorization: any}
        method: string
        body: any
        url: string
        headers: any
        log: any
    },
    res: any,
    next: any,
    handler: Handler,
) => {
    if (!handler.roleKey || !handler.users?.length) {
        return res
            .status(403)
            .send({message: 'Handler configuration missing roles or roleKey'})
    }

    if (ALLOWED_URLS.some((url) => req.url.includes(url))) {
        return next()
    }

    const authToken = getAuthorizationFromRequest(req)
    if (!authToken) {
        return res.status(401).send({message: 'Missing Authorization token'})
    }
    let tokenToSetInCookie = authToken
    try {
        const sessionInfo: UserSession = await get(authToken)
        if (!sessionInfo) {
            return res
                .status(403)
                .send({message: 'Session not found or expired'})
        }
        const roleName = sessionInfo[handler.roleKey]

        if (!handler.users.includes(roleName)) {
            return res
                .status(403)
                .send({message: 'User lacks permission for this resource'})
        }

        if (isSessionExpiring(sessionInfo.lastUpdatedAt)) {
            const newSessionToken = await refreshSession(req, authToken)
            if (!newSessionToken) {
                return res.status(403).send({message: 'Session refresh failed'})
            }
            tokenToSetInCookie = newSessionToken
        }
        res.set({
            'Set-Cookie': `Authorization=${tokenToSetInCookie}; Path=/; SameSite=Lax; Secure`,
        })

        // If a static token is provided, inject it and forward directly
        if (handler.token) {
            req.headers.authorization = handler.token
        }

        if (handler.userInfoInjectionNeeded) {
            const mfeUserDetails: MFEUserDetails = await processMFEUserDetails(
                sessionInfo,
            )
            return requestHandler(req, res, next, mfeUserDetails)
        }
        return requestHandler(req, res, next)
    } catch (error) {
        req.log.error('Error in session validation:', error)
        return res.status(403).send({message: 'Error validating session'})
    }
}

const requestHandler = async (
    req: any,
    res: any,
    next: any,
    mfeUserDetails?: MFEUserDetails,
): Promise<void> => {
    if (req.method !== 'POST' && req.method !== 'PUT') return next()

    const contentType = req.headers['content-type']

    try {
        if (contentType?.includes('application/json')) {
            // JSON body handling
            let bodyData = req.body

            if (typeof bodyData === 'string') {
                try {
                    bodyData = JSON.parse(bodyData)
                } catch (e) {
                    req.log.error('Invalid JSON body:', e)
                    return res.status(400).send('Invalid request body')
                }
            }

            req.modifiedBody = JSON.stringify({
                ...bodyData,
                userInfo: mfeUserDetails || {},
            })
        } else if (contentType?.includes('multipart/form-data')) {
            const form = new FormData()

            form.append('userInfo', JSON.stringify(mfeUserDetails || {}))

            // use multer or any middleware to parse `req.body` and `req.files` before this
            if (req.body) {
                for (const [key, value] of Object.entries(req.body)) {
                    form.append(key, value)
                }
            }

            if (req.files) {
                const files = Array.isArray(req.files)
                    ? req.files
                    : Object.values(req.files).flat()
                for (const file of files) {
                    form.append(file.fieldname, file.buffer, {
                        filename: file.originalname,
                        contentType: file.mimetype,
                    })
                }
            }

            req.modifiedForm = form
        }
        return next()
    } catch (err) {
        req.log.error('Error preparing proxy body:', err)
        return res.status(400).send('Invalid request body')
    }
}

const fixRequestBody = (proxyReq: any, req: any) => {
    if (req.modifiedBody) {
        proxyReq.setHeader('Content-Type', 'application/json; charset=utf-8')
        proxyReq.setHeader(
            'Content-Length',
            Buffer.byteLength(req.modifiedBody),
        )
        proxyReq.write(req.modifiedBody)
        proxyReq.end()
    } else if (req.modifiedForm) {
        const buffer = req.modifiedForm.getBuffer()
        const headers = req.modifiedForm.getHeaders()

        proxyReq.setHeader('Content-Type', headers['content-type'])
        proxyReq.setHeader('Content-Length', buffer.length)
        proxyReq.write(buffer)
        proxyReq.end()
    }
}

const createPrepareProxyRequestBody = (handler: Handler) => {
    return async (req: any, res: any, next: any) => {
        handlerWithAuth(req, res, next, handler)
    }
}

const injectSessionInCookieAndRefreshIfNeeded = async (
    req: any,
    res: any,
    handler: any,
) => {
    const authToken = getAuthorizationFromRequest(req)
    if (!authToken) {
        return res.status(401).send({message: 'Missing Authorization token'})
    }
    let tokenToSetInCookie = authToken
    try {
        const sessionInfo: UserSession = await get(authToken)
        if (!sessionInfo) {
            return res
                .status(403)
                .send({message: 'Session not found or expired'})
        }

        if (isSessionExpiring(sessionInfo.lastUpdatedAt)) {
            const newSessionToken = await refreshSession(req, authToken)
            if (!newSessionToken) {
                return res.status(403).send({message: 'Session refresh failed'})
            }
            tokenToSetInCookie = newSessionToken
        }
        res.set({
            'Set-Cookie': `Authorization=${tokenToSetInCookie}; Path=/; SameSite=Lax; Secure`,
        })

        return handler(req, res)
    } catch (error) {
        req.log.error('Error in session validation:', error)
        return res.status(403).send({message: 'Error validating session'})
    }
}

const injectSessionInCookieAndRefreshIfNeededHandler =
    (handler: any) => (req: any, res: any) => {
        return injectSessionInCookieAndRefreshIfNeeded(req, res, handler)
    }

export {
    createPrepareProxyRequestBody,
    fixRequestBody,
    handlerWithAuth,
    injectSessionInCookieAndRefreshIfNeededHandler,
    processMFEUserDetails,
    refreshSession,
}
