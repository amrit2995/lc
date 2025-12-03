import axios from 'axios'
import {get} from '../../redis/utils'
import secrets from '../../secrets'
import {getAuthorizationFromRequest} from '../../utils/auth'
import {
    getContactIdVendorNumberVendorTypeFromUrl,
    isDeleteAsPostUrl,
    isEmailDuplicateUrl,
    isPolledService,
    removeUam,
} from './commonServerUtils'

const {vendorgateway} = secrets()

const {gatewayUrl} = vendorgateway

const getSession = async (req, res, cb) => {
    const authorization = getAuthorizationFromRequest(req)
    const sessionInfo = await get(authorization)
    return cb(sessionInfo)
}

const exceptionHandler = (
    error,
    req,
    res,
    token,
    serviceHost,
    isSecondCallDone,
) => {
    if (isPolledService(req.url) && !isSecondCallDone) {
        axiosTemplateWithBearerTokenHeader(req, res, token, serviceHost, true)
    } else if (
        (error.response.status === '302' || error.response.status === 302) &&
        isEmailDuplicateUrl(req.url)
    ) {
        req.log.error(
            'There was an error in axiosTemplateWithBearerTokenHeader!',
            error,
        )
        return res.status(204).json({message: 'Error in fetching data'})
    } else {
        req.log.error(
            'There was an error in axiosTemplateWithBearerTokenHeader!',
            error,
        )
        return res
            .status(error?.status || 400)
            .send(error?.message || 'Error in fetching data')
    }
}

const axiosTemplateWithBearerTokenHeader = (
    req,
    res,
    token,
    serviceHost,
    isSecondCallDone,
) => {
    const reqUrl = `${serviceHost || gatewayUrl}${removeUam(req.url)}`
    const reqMethod = isDeleteAsPostUrl(req.url) ? 'DELETE' : req.method
    const reqHeaders = {
        'Content-type': 'application/json',
        Authorization: `Bearer ${token}`,
        'Cache-Control': 'no-cache',
    }
    req.log.info(
        'Prepared axiosTemplateWithBearerTokenHeader ',
        reqUrl,
        reqMethod,
    )
    axios
        .request({
            url: reqUrl,
            method: reqMethod,
            headers: reqHeaders,
            data: req.body,
        })
        .then((vgwResponse) => {
            if (
                isEmailDuplicateUrl(req.url) &&
                (!vgwResponse ||
                    vgwResponse?.status === 204 ||
                    vgwResponse?.message?.includes('302'))
            ) {
                return res.status(204).send(vgwResponse?.data)
            }
            if (
                (vgwResponse.status === '204' || vgwResponse.status === 204) &&
                isDeleteAsPostUrl(req.url)
            ) {
                const {contactId, vendorNumber, vendorType} =
                    getContactIdVendorNumberVendorTypeFromUrl(req.url)
                const vendorContactUrl = `/apivendorcontact/contact/${contactId}/vendorNumber/${vendorNumber}/vendorType/${vendorType}`
                axiosTemplateWithBearerTokenHeader(
                    {
                        url: vendorContactUrl,
                        method: 'DELETE',
                    },
                    res,
                    token,
                )
            } else {
                return res.send(vgwResponse.data)
            }
        })
        .catch((err) =>
            exceptionHandler(
                err,
                req,
                res,
                token,
                serviceHost,
                isSecondCallDone,
            ),
        )
}

export {axiosTemplateWithBearerTokenHeader, getSession}
