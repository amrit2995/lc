import axios, {AxiosResponse} from 'axios'
import {v4 as uuid} from 'uuid'
import {getAccessToken} from '../authUtils'
import {gatewayInstance, oneRingInstance} from '../axiosInstance'
import {asyncWrap, encodeBase64, getBasePath} from '../commonUtils'
import {InitSessionProps} from './interface'

const initSession = async (params: InitSessionProps) => {
    try {
        /* eslint-disable camelcase */
        const sessionInfo: AxiosResponse = await oneRingInstance.post(
            `init-session`,
            params,
        )
        if (!sessionInfo?.data) {
            return {error: 'Error in fetching session info'}
        }
        return sessionInfo.data
    } catch (e) {
        console.error(e)
        return {error: 'Error in fetching session info'}
    }
}

const getIsEnterpriseUser = async () => {
    try {
        const sessionInfo: AxiosResponse = await oneRingInstance.get(
            `isEntForgerock`,
        )
        return {isEntForgerock: !!sessionInfo?.data?.isEntForgerock}
    } catch (e) {
        console.error(e)
        return {isEntForgerock: false}
    }
}

const initiateLogin = async () => {
    try {
        const ssoRedirectInfo: AxiosResponse = await oneRingInstance.get(
            `journey/request`,
        )
        return {redirectURL: ssoRedirectInfo?.data?.redirectURL}
    } catch (e) {
        console.error(e)
        return {redirectURL: false}
    }
}

const verifyCallback = async (code: string) => {
    try {
        /* eslint-disable camelcase */
        const sessionInfo: AxiosResponse = await oneRingInstance.post(
            `journey/handle`,
            {
                reference: encodeBase64(code),
            },
            {withCredentials: true},
        )
        if (!sessionInfo?.data) {
            return {error: 'Error in verifyCallback'}
        }
        return sessionInfo.data
    } catch (e) {
        console.error(e)
        return {error: 'Error in verifyCallback'}
    }
}

const getSessionInfo = async () => {
    try {
        const sessionInfo: AxiosResponse = await oneRingInstance.get(`session`)
        if (!sessionInfo?.data) {
            return {message: 'Error in fetching session info'}
        }
        return sessionInfo.data
    } catch (e) {
        return {message: 'Error in fetching session info', error: e}
    }
}

// Not using oneRingInstance to keep it away from 403 interceptor
// need to check for idleSession timeouts
const isActiveSession = async (): Promise<boolean> => {
    try {
        const sessionInfo: AxiosResponse = await axios.get(
            `${getBasePath()}/onering/session?getId=${uuid()}`,
            {
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: getAccessToken(),
                },
            },
        )
        if (sessionInfo?.data?.userId) {
            return true
        }
        return false
    } catch (e) {
        console.log('Error in fetching isActiveSession', e)
        return false
    }
}

const isVendorAdmin = (authorities: Array<string>) =>
    authorities?.indexOf('VG_VNDACS_USER-ACCESS-WRITE') >= 0

// userInfo?.user_type === 'vendor'
const getUserAccess = async () => {
    const [sessionInfoErr, sessionInfo] = await asyncWrap(
        oneRingInstance.get('session'),
    )
    const [, userInfo] = await asyncWrap(
        oneRingInstance.post('userInfo', {
            accessToken: getAccessToken(),
        }),
    )
    let vendorUser = {}
    // let vendorUser = {
    //     isVendorUser: true,
    //     isVendorAdmin: true,
    // }
    if (userInfo?.user_type === 'vendor') {
        vendorUser = {
            isVendorUser: true,
            isVendorAdmin: isVendorAdmin(userInfo?.authorities),
        }
    }
    const sessionData = {
        ...sessionInfo?.data,
        ...userInfo?.data,
        ...vendorUser,
        fullName: `${userInfo?.data?.given_name} ${userInfo?.data?.family_name}`,
        given_name: userInfo?.data?.given_name,
        family_name: userInfo?.data?.family_name,
        activeVbu: userInfo?.data?.activeVbu,
        // vbuList: ['501242_2'],
    }

    /* eslint-disable camelcase */
    if (undefined !== window) {
        window.sessionStorage.setItem(
            'eckoData',
            JSON.stringify({
                sales_id: userInfo?.data?.uniqueid || userInfo?.data?.sales_id,
                first_name: userInfo?.data?.given_name,
                last_name: userInfo?.data?.family_name,
                user_email: userInfo?.data?.email,
            }),
        )
    }

    if (sessionData?.vbuList?.length) {
        const [_, vbuDetails] = await verifyVBU(sessionData?.vbuList)
        return [
            sessionInfoErr,
            sessionData ? {...sessionData, vbuList: vbuDetails} : null,
        ]
    }
    return [sessionInfoErr, {...sessionData}]
}

const verifyVBU = async (props: any) => {
    const [err, response] = await asyncWrap(
        gatewayInstance.post('/vbuVerify', {vbus: props}),
    )
    return [err, response?.data]
}

const flushSession = () => {}

const clearSession = () => {
    window.localStorage.clear()
    window.sessionStorage.clear()
    window.document.cookie =
        'Authorization=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT; Secure;'
}

const logout = async () => {
    const [err, response] = await asyncWrap(
        oneRingInstance.get('session/delete'),
    )
    window.document.cookie =
        'Authorization=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT; Secure'
    flushSession()
    clearSession()
    return [err, response?.data]
}

export {
    getIsEnterpriseUser,
    getSessionInfo,
    getUserAccess,
    initSession,
    isActiveSession,
    logout,
    verifyVBU,
    initiateLogin,
    verifyCallback,
}
