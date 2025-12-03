import logger from '../plugins/logger'
import clientPromise from './client'

const get = async <T>(key: string): Promise<T | null> => {
    try {
        const client = await clientPromise
        const rawData = await client.get(key)
        return rawData ? (JSON.parse(rawData) as T) : null
    } catch (error) {
        logger.error('Error fetching from Redis (get):', error)
        return null
    }
}

const set = async (
    key: string,
    value: any,
    ttlSeconds?: number | null,
): Promise<string | null> => {
    try {
        const client = await clientPromise
        const serializedValue = JSON.stringify(value)

        if (typeof ttlSeconds === 'number' && ttlSeconds > 0) {
            return await client.set(key, serializedValue, {EX: ttlSeconds})
        }

        return await client.set(key, serializedValue)
    } catch (error) {
        logger.error('Error saving to Redis (set):', error)
        return null
    }
}

const del = async (key: string): Promise<boolean> => {
    try {
        const client = await clientPromise
        const result = await client.del(key)
        return result > 0
    } catch (error) {
        logger.error('Error deleting from Redis (del):', error)
        return false
    }
}

export {get, set, del}
