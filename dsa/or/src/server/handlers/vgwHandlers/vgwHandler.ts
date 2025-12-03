import onAggregatorVendorServicesProxy from './aggVendorHandler'
import {axiosTemplateWithBearerTokenHeader, getSession} from './commonHandler'
import {
    isAggregatorVendorService,
    isVBUVerifyUrl,
    isVppService,
} from './commonServerUtils'
import onGetVppSessionAndProxy from './vppHandler'

import onVbuVerifyProxy from './vbuVerifyHandler'

const onGetSessionAndAddHeader = (request: any, response: any) => {
    /* eslint-disable camelcase */
    const vgwProxyHandler = (tokenResponse: any) => {
        axiosTemplateWithBearerTokenHeader(
            request,
            response,
            tokenResponse?.accessToken,
        )
    }
    request.log.info(
        'Received onGetSessionAndAddHeader request',
        request.cookies?.Authorization,
    )
    if (isVppService(request.url)) {
        onGetVppSessionAndProxy(request, response)
    } else if (isAggregatorVendorService(request.url)) {
        onAggregatorVendorServicesProxy(request, response)
    } else if (isVBUVerifyUrl(request.url)) {
        onVbuVerifyProxy(request, response)
    } else {
        getSession(request, response, vgwProxyHandler)
    }
}

export default onGetSessionAndAddHeader
