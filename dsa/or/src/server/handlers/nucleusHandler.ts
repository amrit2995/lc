import axios from 'axios'
import logger from '../plugins/logger'
import secrets from '../secrets'

const {auth, urls} = secrets()
const {nucleus: nucleusAuth} = auth
const {nucleus: nucleusUrl} = urls

const fetchNucleusConfig = async (scope: string) => {
    const config = await axios.get(`${nucleusUrl}${scope}`, {
        headers: {
            Authorization: nucleusAuth,
        },
    })
    if (config?.data?.data) {
        return config.data.data
    }
    logger.error('Error in fetching nucleus config', scope)
    return null
}

const getNucleusConfig = async (request: any, response: any) => {
    try {
        const {scope} = request.query
        const config = await fetchNucleusConfig(scope)
        if (config) {
            return response.json(config)
        }
        return response.status(400).json({error: 'Error in fetching data'})
    } catch (error) {
        request.log.error('Exception at getNucleusConfig', error)
        return response.status(500).json({error: 'Error in fetching data'})
    }
}

export {fetchNucleusConfig, getNucleusConfig}
