import secrets from '../../secrets'
import {axiosTemplateWithBearerTokenHeader, getSession} from './commonHandler'

const {vendorgateway} = secrets()

const {aggregatorUrl} = vendorgateway

const onAggregatorVendorServicesProxy = (request: any, response: any) => {
    /* eslint-disable camelcase */
    const onUpdateProxy = (tokenResponse: any) => {
        axiosTemplateWithBearerTokenHeader(
            request,
            response,
            tokenResponse?.accessToken,
            aggregatorUrl,
        )
    }
    request.log.info('Received onAggregatorVendorServicesProxy request')
    getSession(request, response, onUpdateProxy)
}

export default onAggregatorVendorServicesProxy
