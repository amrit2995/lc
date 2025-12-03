/* eslint-disable camelcase */
import axios from 'axios'
import logger from '../plugins/logger'
import {get, set} from '../redis/utils'
import secrets from '../secrets'
import {
    generateSessionToken,
    getAuthorizationFromRequest,
    mutateUserInfo,
} from '../utils/auth'
import {REDIS_USER_TOKEN_VERSION} from '../utils/constants'

import {OIDCUserToken, UserInfo, UserSession} from './interfaces/sessionProps'
import {findOrGenerateUser} from './services/userService'
import {
    getForgeRockDetails,
    isVendorUser,
    isVendorUserFromReferer,
} from './services/vendorConditions'

const {
    redisTTL: {sessionExpiry},
} = secrets()

const userOriginHandler = async (request: any, response: any) => {
    const isVendor = isVendorUserFromReferer(request)
    request.log.info('User isEntForgerock', !isVendor)
    response.send({isEntForgerock: !isVendor})
}

const getSessionInfo = async (request: any, response: any) => {
    const authorization = getAuthorizationFromRequest(request)

    if (!authorization) {
        return response
            .status(401)
            .send({message: 'Authorization token missing'})
    }

    try {
        const sessionInfo: UserSession = await get(authorization)
        if (!sessionInfo) {
            return response
                .status(403)
                .send({message: 'User session not found'})
        }
        return response.json({...sessionInfo, refreshToken: 'NA'})
    } catch (error) {
        request.log.error('Error in reading from redis ', error)
        return response.status(403).json({
            message: 'Error in getting user info',
        })
    }
}

const deleteSession = async (
    isVendor: boolean,
    userSession: UserSession,
): Promise<string> => {
    try {
        const {OPServer, logoutUrl, clientId} = getForgeRockDetails(isVendor)
        const enterpriseDetails = getForgeRockDetails(false)
        const url = OPServer.split('/realms/')[0]

        if (!isVendor) {
            return logoutUrl
        }

        await axios.request({
            url: `${url}/connect/endSession`,
            method: 'GET',
            params: {
                id_token_hint: userSession?.idToken ?? '',
                client_id: clientId,
            },
            headers: {
                Authorization: `Bearer ${userSession?.accessToken ?? ''}`,
            },
        })

        if (userSession.isExternalUser) return '/lormn/logout'
        return enterpriseDetails?.logoutUrl
    } catch (error) {
        logger.error('Error in delete session ', error)
        return null
    }
}

const initSession = async (
    codeVerifier: string,
    state: string,
    code: string,
    referrer: string,
): Promise<OIDCUserToken> => {
    const isVendor = isVendorUser(referrer)
    const {OPServer, clientId, redirectURL} = getForgeRockDetails(isVendor)

    /* eslint-disable camelcase */
    const requestBody = {
        client_id: clientId,
        redirect_uri: redirectURL,
        grant_type: 'authorization_code',
        code_verifier: codeVerifier,
        state,
        code,
    }
    logger.info('Received getToken request with params', requestBody)

    try {
        const oidcUserToken = await axios.request({
            url: `${OPServer}/access_token`,
            method: 'POST',
            data: requestBody,
            headers: {
                'Content-type': 'application/x-www-form-urlencoded',
            },
        })
        logger.info('got response', oidcUserToken.status)
        if (oidcUserToken?.data) {
            logger.info('got response data', oidcUserToken.data)

            const parsedData = oidcUserToken.data
            return {
                ...parsedData,
                useEntForgerock: !isVendor,
            } as OIDCUserToken
        }
        logger.error('There was an error in getToken! - response')
        throw new Error('There was an error in getToken!')
    } catch (error) {
        logger.error('There was an error in getToken! - exception', error)
        throw new Error('There was an error in getToken!')
    }
}

const onUpdateToken = async (
    referrer: string,
    userId: string,
    refreshToken: string,
    request: any,
): Promise<OIDCUserToken> => {
    const isVendor = isVendorUser(referrer)
    const {OPServer, clientId} = getForgeRockDetails(isVendor)

    /* eslint-disable camelcase */
    const requestBody = {
        client_id: clientId,
        grant_type: 'refresh_token',
        refresh_token: refreshToken,
    }
    logger.info('Received updateToken request with params', requestBody)

    try {
        const oidcUserTokenRaw = await axios.post(
            `${OPServer}/access_token`,
            requestBody,
            {
                headers: {
                    'Content-type': 'application/x-www-form-urlencoded',
                },
            },
        )
        logger.info('Fetched refresh token', oidcUserTokenRaw.data)
        const oidcUserToken: OIDCUserToken = oidcUserTokenRaw.data
        oidcUserToken.hashToken = await setUserSession(
            oidcUserToken,
            userId,
            isVendor,
            request,
        )
        oidcUserToken.refresh_token = 'NA'
        return oidcUserToken
    } catch (error) {
        logger.error('There was an error in refreshToken!', error)
        return null
    }
}

// local only
// const getUserInfo = async (request: any, response: any) => {
//     response.send(userInfoData)
// }

const getUserInfo = async (
    authorization: string,
    isVendor: boolean,
): Promise<UserInfo> => {
    const {OPServer} = getForgeRockDetails(isVendor)
    try {
        const userInfo = await axios.get(`${OPServer}/userinfo`, {
            headers: {
                'Content-type': 'application/json',
                Authorization: `Bearer ${authorization}`,
            },
        })
        if (userInfo?.data) {
            return userInfo.data as UserInfo
        }
        logger.error('Error in fetching userInfo - response')
        throw new Error('Error in fetching userInfo')
    } catch (error) {
        logger.error('Error in fetching userInfo - exception', error)
        throw new Error('Error in fetching userInfo')
    }
}

const setUserSession = async (
    oidcUserToken: OIDCUserToken,
    salesId: string,
    isVendor: boolean,
    request: any,
): Promise<string> => {
    // Persisting the same token for update, and generating new token for init session
    const hashTokenFromCookie = getAuthorizationFromRequest(request)
    const hashToken =
        hashTokenFromCookie || generateSessionToken(oidcUserToken.access_token)

    let userInfo: UserInfo

    if (salesId) {
        userInfo = {
            sub: salesId,
        }
    } else {
        userInfo = await getUserInfo(oidcUserToken.access_token, isVendor)
    }
    logger.info('User Id for setUserSession', userInfo.sub)
    userInfo = mutateUserInfo(userInfo, request)
    const currentUser: UserSession = await findOrGenerateUser(
        userInfo,
        !!salesId,
        oidcUserToken,
    )
    // hashToken - userSession
    await set(hashToken, currentUser, sessionExpiry)
    // userId - hashToken -> used in updateToken
    await set(
        `${REDIS_USER_TOKEN_VERSION}${hashToken}`,
        currentUser.lastUpdatedAt,
        sessionExpiry,
    )
    return hashToken
}

export {
    deleteSession,
    getSessionInfo,
    getUserInfo,
    initSession,
    isVendorUserFromReferer,
    onUpdateToken,
    setUserSession,
    userOriginHandler,
}
