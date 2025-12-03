import axios from 'axios'
import secrets from '../secrets'
import {getAuthorizationFromRequest} from '../utils/auth'
import {findAdvertisersByVbuIds} from './services/loginMapping'

const {urls} = secrets()
const {southdeep} = urls

const getAllAdvertisers = async (request: any, response: any) => {
    // TODO: Can be called directly from db
    const authorization: string = getAuthorizationFromRequest(request)
    try {
        const advertisers = await axios.get(
            `${southdeep}/southdeep-svc/presentation/advertiser`,
            {
                headers: {
                    Authorization: authorization,
                },
            },
        )
        if (advertisers) {
            return response.json(advertisers.data)
        }
        return response
            .status(500)
            .json({message: 'Error in fetching advertisers', data: []})
    } catch (error) {
        request.log.error('Exception at getAllAdvertisers', error)
        return response
            .status(500)
            .json({message: 'Error in fetching advertisers', data: []})
    }
}

const getAdvertiserByVbuId = async (request: any, response: any) => {
    const {vbuId} = request.params
    if (!vbuId) {
        request.log.error('VbuId is not present!')
        return response
            .status(400)
            .json({message: 'VbuId is not present!', data: []})
    }
    try {
        const advertiser = await findAdvertisersByVbuIds([vbuId])
        if (advertiser?.length) {
            return response.json(advertiser[0])
        }
        return response.json({})
    } catch (error) {
        request.log.error('Exception at getAdvertiserByVbuId', error)
        return response
            .status(500)
            .json({message: 'Error in fetching advertisers', data: []})
    }
}

const getBrandsByVbuIds = async (request: any, response: any) => {
    const {vbuIds} = request.body
    if (!vbuIds) {
        request.log.error('VbuIds is not present!')
        return response
            .status(400)
            .json({message: 'VbuIds is not present!', data: []})
    }
    try {
        const advertiser = await findAdvertisersByVbuIds(vbuIds)
        if (advertiser?.length) {
            return response.json(advertiser?.map((item) => item.brands).flat())
        }
        return response.json({})
    } catch (error) {
        request.log.error('Exception at getBrandsByVbuIds', error)
        return response
            .status(500)
            .json({message: 'Error in fetching brandsByVbuIds', data: []})
    }
}

export {getAdvertiserByVbuId, getAllAdvertisers, getBrandsByVbuIds}
