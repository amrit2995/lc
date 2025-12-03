import axios, {AxiosResponse} from 'axios'
import {v4 as uuid} from 'uuid'
import {getAccessToken} from './authUtils'
import {getBasePath, triggerOnInterceptorAccessDenied} from './commonUtils'

const requestInterceptorCommon = (request: any) => {
    request.headers.Authorization = getAccessToken()
    request.headers['x-b3-traceId'] = uuid()
    if (request.method === 'GET' || request.method === 'get') {
        request.params = {
            ...request.params,
            getId: uuid(),
        }
    }
    return request
}

const responseInterceptorSuccessCommon = (success: {
    response: AxiosResponse
}) => {
    return Promise.resolve(success)
}

const responseInterceptorErrorCommon = (error: {response: AxiosResponse}) => {
    if (error?.response?.status === 403) {
        triggerOnInterceptorAccessDenied()
    }
    return Promise.reject(error)
}

const oneRingInstance: any = axios.create({
    baseURL: `${getBasePath()}/onering/`,
    headers: {
        'Content-Type': 'application/json',
    },
})

oneRingInstance.interceptors.request.use(requestInterceptorCommon)
oneRingInstance.interceptors.response.use(
    responseInterceptorSuccessCommon,
    responseInterceptorErrorCommon,
)

const southDeepSvcInstance: any = axios.create({
    baseURL: `/lormn/api/`,
    headers: {
        'Content-Type': 'application/json',
    },
})

southDeepSvcInstance.interceptors.request.use(requestInterceptorCommon)
southDeepSvcInstance.interceptors.response.use(
    responseInterceptorSuccessCommon,
    responseInterceptorErrorCommon,
)

const gatewayInstance: any = axios.create({
    baseURL: '/lormn/gateway/api',
    headers: {
        'Content-Type': 'application/json',
    },
})

gatewayInstance.interceptors.request.use(requestInterceptorCommon)
gatewayInstance.interceptors.response.use(
    responseInterceptorSuccessCommon,
    responseInterceptorErrorCommon,
)

export {gatewayInstance, oneRingInstance, southDeepSvcInstance}
