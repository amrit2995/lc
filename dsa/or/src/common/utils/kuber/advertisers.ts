import {oneRingInstance} from '../axiosInstance'
import {asyncWrap} from '../commonUtils'

const getAdvertisers = async () => {
    const [error, advertisers]: any = await asyncWrap(
        oneRingInstance.get(`advertisers`),
    )
    return [error, advertisers?.data]
}

const getAdvertiserByVbuId = async (vbuId: string, userId: string) => {
    const [error, advertisers]: any = await asyncWrap(
        oneRingInstance.get(`vendorMapping/${vbuId}/user/${userId}`),
    )
    return [error, advertisers?.data]
}

const getBrandsByVbuIds = async (vbuIds: string[]) => {
    const [error, advertiser]: any = await asyncWrap(
        oneRingInstance.post(`brandsVbu`, {vbuIds}),
    )
    return [error, advertiser?.data]
}

export {getAdvertiserByVbuId, getAdvertisers, getBrandsByVbuIds}
