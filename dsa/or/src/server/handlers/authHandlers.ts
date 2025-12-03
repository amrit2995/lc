/* eslint-disable camelcase */
import {refreshSession} from '../proxyMiddleware/handler'
import {del, get, set} from '../redis/utils'
import secrets from '../secrets'
import {
    base64URLEncode,
    getAuthorizationFromRequest,
    mutateUserInfo,
    returnNanoId,
    sha256,
} from '../utils/auth'
import {
    REDIS_USER_INFO_TAG,
    REDIS_USER_TAG,
    REDIS_USER_TOKEN_VERSION,
} from '../utils/constants'
import {OIDCUserToken, UserInfo, UserSession} from './interfaces/sessionProps'

import {getForgeRockDetails} from './services/vendorConditions'
import {
    deleteSession,
    getUserInfo,
    initSession,
    isVendorUserFromReferer,
    setUserSession,
} from './sessionHandler'

const {forgerock} = secrets()
const {enterpriseDetails, vendorDetails} = forgerock
const {redirectURL: enterpriseReferrer} = enterpriseDetails
const {redirectURL: vendorReferrer} = vendorDetails

const deleteSessionHandler = async (
    request: any,
    response: any,
): Promise<void> => {
    try {
        const hashToken = getAuthorizationFromRequest(request)
        const isVendor = isVendorUserFromReferer(request)
        const userSession: UserSession = await get(hashToken)
        const redirectUrl = await deleteSession(isVendor, userSession)
        if (redirectUrl) {
            response.status(200).send({
                redirectUrl,
            })
        } else {
            response.status(400).send({
                message: 'Error in performing logout',
            })
        }
        // delete data
        if (hashToken) {
            await del(hashToken)
        }
        if (userSession?.userId) {
            await del(`${REDIS_USER_TOKEN_VERSION}${hashToken}`)
            await del(`${REDIS_USER_TAG}${userSession.userId}`)
            await del(`${REDIS_USER_INFO_TAG}${userSession.userId}`)
        }
    } catch (error) {
        request.log.error('There was an error in deleteSession!', error)
        response.status(403).send({
            message: 'Error in authenticating user',
        })
    }
}

const userInfoHandler = async (request: any, response: any): Promise<void> => {
    try {
        const hashToken = getAuthorizationFromRequest(request)
        const isVendor = isVendorUserFromReferer(request)

        const userSession: UserSession = await get(hashToken)
        const userInfo: UserInfo = await getUserInfo(
            userSession.accessToken,
            isVendor,
        )
        response.status(200).json(mutateUserInfo(userInfo, request))
    } catch (error) {
        request.log.error('There was an error in UserInfo!', error)
        response.status(403).json({
            message: 'Error in fetching userInfo',
        })
    }
}

const refreshSessionHandler = async (
    request: any,
    response: any,
): Promise<void> => {
    try {
        const authToken = getAuthorizationFromRequest(request)
        const sessionInfo: UserSession = await get(authToken)
        if (!sessionInfo) {
            response.status(403).send({message: 'Session not found or expired'})
        }
        const updatedHashToken = await refreshSession(request, authToken)
        response.status(200).send({
            token: updatedHashToken,
        })
    } catch (error) {
        request.log.error('There was an error in refreshSessionHandler!', error)
        response.status(403).send({
            message: 'Error in generating new token',
        })
    }
}

const authLoginHandler = async (request: any, response: any): Promise<void> => {
    const isVendor = isVendorUserFromReferer(request)
    const {authorizeURL, clientId, redirectURL} = getForgeRockDetails(isVendor)

    const codeVerifier = await returnNanoId(64)
    const codeChallenge = base64URLEncode(sha256(codeVerifier))
    const state = await returnNanoId(32)

    // Store verifier & state in a secure session
    await set(`oauth:${state}`, codeVerifier)

    const REDIRECT_URI = new URL(`${authorizeURL}`)
    REDIRECT_URI.searchParams.set('client_id', clientId)
    REDIRECT_URI.searchParams.set('redirect_uri', redirectURL)
    REDIRECT_URI.searchParams.set('response_type', 'code')
    REDIRECT_URI.searchParams.set(
        'scope',
        isVendor
            ? 'openid profile'
            : '',
    )
    REDIRECT_URI.searchParams.set('code_challenge', codeChallenge)
    REDIRECT_URI.searchParams.set('code_challenge_method', 'S256')
    REDIRECT_URI.searchParams.set('state', state)

    // Set state cookie
    response.cookie('x-one-ring-init', state, {
        httpOnly: true,
        secure: true,
        sameSite: 'Lax',
        maxAge: 5 * 60 * 1000,
    })

    response.status(200).json({
        redirectURL: REDIRECT_URI.toString(),
    })
}
const sanitizeInput = (input: string): string => {
    return input.replace(/[^a-zA-Z0-9-_]/g, '') // strip unwanted characters
}

const authCallbackHandler = async (
    request: any,
    response: any,
): Promise<void> => {
    const code = Buffer.from(request.body.reference, 'base64').toString('utf-8')
    const state = request.cookies['x-one-ring-init']

    try {
        if (!state || !code) {
            return response.status(400).send('Missing OAuth data')
        }

        const code_verifier = await get(`oauth:${state}`)
        if (!code_verifier) {
            return response.status(400).send('Invalid or expired session')
        }

        const sanitizedCode = sanitizeInput(code)
        const sanitizedState = sanitizeInput(state)
        const sanitizedVerifier = sanitizeInput(`${code_verifier}`)
        const {referer} = request?.headers ?? ''

        const allowedReferrers = [enterpriseReferrer, vendorReferrer]
        const referrerSplit = referer?.includes('/lormn')
            ? referer.split('/lormn')[0]
            : ''
        if (referrerSplit && !allowedReferrers?.includes(referrerSplit)) {
            request.log.error('Referrer is not allowed:', referrerSplit)
            return response.status(401).send('Unauthorized referrer')
        }

        // Make sure any URL or endpoint constructed uses these sanitized inputs
        const oidcUserToken: OIDCUserToken = await initSession(
            sanitizedVerifier,
            sanitizedState,
            sanitizedCode,
            referrerSplit,
        )
        const isVendor = isVendorUserFromReferer(request)

        if (oidcUserToken) {
            oidcUserToken.hashToken = await setUserSession(
                oidcUserToken,
                null,
                isVendor,
                request,
            )
            oidcUserToken.refresh_token = 'NA'

            response.set({
                'Set-Cookie': `Authorization=${oidcUserToken.hashToken}; Path=/; SameSite=Lax; Secure`,
            })

            return response.json(oidcUserToken)
        }
        return response.status(403).json({
            message: 'Error in authenticating user',
        })
    } catch (error) {
        request.log.error('There was an error in Init-session!', error)
        return response.status(403).json({
            message: 'Error in authenticating user',
        })
    } finally {
        await del(`oauth:${state}`)
    }
}

export {
    authCallbackHandler,
    authLoginHandler,
    deleteSessionHandler,
    refreshSessionHandler,
    userInfoHandler,
}
