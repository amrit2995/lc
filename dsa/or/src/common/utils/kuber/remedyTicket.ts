import {oneRingInstance} from '../axiosInstance'
import {asyncWrap} from '../commonUtils'

const createRemedyTicket = async (data: any) => {
    const [error, advertisers]: any = await asyncWrap(
        oneRingInstance.post(`remedy`, data, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        }),
    )
    return [error, advertisers?.data]
}

const getRemedyTickets = async (data: any) => {
    const [error, advertisers]: any = await asyncWrap(
        oneRingInstance.get(`remedy`, {params: data}),
    )
    return [error, advertisers?.data]
}

export {createRemedyTicket, getRemedyTickets}
