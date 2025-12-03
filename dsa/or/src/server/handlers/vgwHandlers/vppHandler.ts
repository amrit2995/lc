import axios from 'axios'
import secrets from '../../secrets'
import {axiosTemplateWithBearerTokenHeader} from './commonHandler'

const {vpp} = secrets()

/* eslint-disable camelcase */
const {endpoint, oauth, client_id, client_secret, grant_type, vpp_service} = vpp

const onGetVppSessionAndProxy = (request: any, response: any) => {
    const vppProxyHandler = (tokenResponse: any) => {
        request.log.info(
            'Received tokenResponse in vppProxyHandler',
            tokenResponse?.accessToken,
        )
        axiosTemplateWithBearerTokenHeader(
            request,
            response,
            tokenResponse?.accessToken,
            vpp_service,
        )
    }
    const reqUrl = `${endpoint}${oauth}?client_id=${client_id}&client_secret=${client_secret}&grant_type=${grant_type}`
    request.log.info('Received onGetSessionAndAddHeader request')
    request.log.info('Requesting url from onGetSessionAndAddHeader', reqUrl)
    response.writeHead(200, {'Content-Type': 'application/json'})
    axios
        .request({
            url: reqUrl,
            method: 'POST',
            data: {},
        })
        .then(vppProxyHandler)
        .catch((error) => {
            request.log.error(
                'There was an error in onGetVppSessionAndProxy!',
                error ? error?.message : null,
            )
            return response
                .status(error?.status || 400)
                .send(error?.message || 'Error in getting vpp session')
        })
}

export default onGetVppSessionAndProxy
