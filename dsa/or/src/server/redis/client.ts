/* eslint-disable no-await-in-loop */
/* eslint-disable no-plusplus */

import {createClient, RedisClientType} from 'redis'
import logger from '../plugins/logger'
import secrets from '../secrets'

const {redis} = secrets()
const {caCert, clientCert, clientKey, password, host, port} = redis

const redisUrl = `rediss://${host}:${port}`

logger.info('Creating Redis client and initiating connection...')

const client: RedisClientType = createClient({
    url: redisUrl,
    socket: {
        tls: true,
        rejectUnauthorized: false,
        ca: caCert,
        reconnectStrategy: (retries) => {
            if (retries > 10) return new Error('Max reconnect attempts reached')
            return Math.min(retries * 100, 3000) // exponential backoff
        },
    },
    password,
})

client.on('connect', () => logger.info('Redis connected'))
client.on('ready', () => logger.info('Redis client ready'))
client.on('reconnecting', () => logger.warn('Redis reconnecting...'))
client.on('end', () => logger.warn('Redis connection closed'))
client.on('error', (err) => logger.error('Redis Client Error:', err))

// Singleton connection promise
const clientPromise: Promise<RedisClientType> = client
    .connect()
    .then(() => client)
    .catch(() => null)

export default clientPromise
