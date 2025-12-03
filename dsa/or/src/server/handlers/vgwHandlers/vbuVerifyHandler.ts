import axios from 'axios'
import secrets from '../../secrets'

const {vendorattributes} = secrets()
const {apiKey, apiUrl} = vendorattributes

const triggerRequest = (vendorNumber: string, vendorType: string) => {
    const vendorAttributeUrl = `${apiUrl}/apivendorattributes/vendorDetail/vendorNumber/${vendorNumber}/vendorType/${vendorType}`
    return axios.request({
        url: vendorAttributeUrl,
        method: 'GET',
        headers: {
            'Content-type': 'application/json',
            'maintenance-api-secret': apiKey,
            'Cache-Control': 'no-cache',
        },
    })
}

const onVbuVerifyProxy = (request: any, response: any) => {
    const {vbus, vbu: individualVbu} = request?.body
    if (Array.isArray(vbus) && vbus.length) {
        const vbuDetails: Array<any> = []
        vbus.forEach((vbu: any) => {
            const [vendorNumber, vendorType] = vbu.split('_')
            const closureToTrigger = () => {
                triggerRequest(vendorNumber, vendorType)
                    .then((vgwResponse) => {
                        if (vgwResponse.status === 500) {
                            vbuDetails.push({vbu, message: 'Invalid VBU'})
                        } else {
                            vbuDetails.push({vbu, ...vgwResponse.data})
                        }
                        if (vbuDetails?.length === vbus?.length) {
                            response.send(vbuDetails)
                        }
                    })
                    .catch((error) => {
                        vbuDetails.push({vbu, message: 'Invalid VBU'})
                        if (vbuDetails?.length === vbus?.length) {
                            response.send(vbuDetails)
                        }
                    })
            }
            closureToTrigger()
        })
    } else if (typeof individualVbu === 'string' && individualVbu) {
        const [vendorNumber, vendorType] = individualVbu.split('_')
        triggerRequest(vendorNumber, vendorType)
            .then((vgwResponse) => {
                if (vgwResponse.status === 500) {
                    response.send({message: 'Invalid VBU'})
                } else {
                    response.send(vgwResponse.data)
                }
            })
            .catch((error) => {
                if (error?.response?.status === 500) {
                    response.send({message: 'Invalid VBU'})
                } else {
                    response
                        .status(error?.response?.status || 400)
                        .send(error?.message || 'Error in fetching data')
                    request.log.error(
                        'There was an error in onVbuVerifyProxy!',
                        error,
                    )
                }
            })
    } else {
        response.status(400).send({message: 'VBU not present'})
    }
}

export default onVbuVerifyProxy
