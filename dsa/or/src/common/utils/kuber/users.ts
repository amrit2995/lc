import {oneRingInstance} from '../axiosInstance'
import {asyncWrap} from '../commonUtils'
import {UpdateUserProps} from './interface'

const updateUser = async ({
    userId,
    advertiserIds = [],
    vendorMappings,
}: UpdateUserProps) => {
    const [err, response] = await asyncWrap(
        oneRingInstance.post('user/update-vendor-mapping', {
            userId,
            advertiserIds,
            vendorMappings,
        }),
    )
    return [err, response?.data]
}

export default updateUser
