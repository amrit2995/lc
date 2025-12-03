import {addOne, editOne, findOne} from '../mongo/client'
import {UserSession} from './interfaces/sessionProps'
import {UserAdvertiserVendorMappingProps} from './interfaces/vendorProps'
import {findAdvertisersByVbuIds} from './services/loginMapping'

const findUserAndAdvertiserVendorMapping = async (
    request: any,
    response: any,
) => {
    try {
        const userId = request?.params?.userId
        const vbuId = request?.params?.vbuId
        const responseObj: UserAdvertiserVendorMappingProps = {}
        const userDetails: UserSession = await findOne('user', 'userId', userId)
        if (!userDetails) {
            responseObj.userVendorMapping = null
        } else {
            responseObj.userVendorMapping = userDetails.vendorMappings
        }
        const advertiser = await findAdvertisersByVbuIds([vbuId])
        if (!advertiser?.length) {
            responseObj.advertiserVendorMapping = null
        } else {
            responseObj.advertiserVendorMapping = advertiser[0].vendorMappings
        }
        response.send(responseObj)
    } catch (error) {
        request.log.error(error)
        response.status(500).send({message: 'Error in finding user!'})
    }
}

const editUserVendorMapping = async (request: any, response: any) => {
    try {
        const {
            userId,
            advertiserIds: advertisers,
            vendorMappings,
        } = request?.body
        if (typeof userId !== 'string') {
            response.status(400).json({message: 'Invalid userId!'})
        }
        const userDetails = await findOne('user', 'userId', userId)
        if (!userDetails) {
            const addUser = await addOne('user', {
                userId,
                advertisers,
                vendorMappings,
            })
            if (addUser) {
                response.send({message: 'Access updated successfully!'})
            }
        } else {
            const editUser = await editOne('user', 'userId', userId, {
                advertisers,
                vendorMappings,
            })
            if (editUser) {
                response.send({message: 'Access updated successfully!'})
            }
        }
    } catch (error) {
        request.log.error(error)
        response.status(500).send({message: 'Error in updating access!'})
    }
}

export {editUserVendorMapping, findUserAndAdvertiserVendorMapping}
