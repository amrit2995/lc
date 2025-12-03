import {AxiosResponse} from 'axios'
import {southDeepSvcInstance} from '../axiosInstance'

const nameSearch = async (params: any) => {
    try {
        /* eslint-disable camelcase */
        const searchResult: AxiosResponse = await southDeepSvcInstance.post(
            `/search/full-text-search`,
            {name: params},
        )
        if (!searchResult?.data) {
            return [{error: 'Error in fetching session info'}, null]
        }
        return [null, searchResult.data]
    } catch (e) {
        console.error(e)
        return [{error: 'Error in fetching session info'}, null]
    }
}

export default nameSearch
