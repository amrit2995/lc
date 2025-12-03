import {oneRingInstance} from '../axiosInstance'
import {asyncWrap} from '../commonUtils'

const getNotifications = async () => {
    const [error, notifications]: any = await asyncWrap(
        oneRingInstance.get(`notifications`),
    )
    return [error, notifications?.data]
}

export default getNotifications
