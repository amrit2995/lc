import axios from 'axios'
import https from 'https'
import secrets from '../secrets'
import logger from '../plugins/logger'
import {get, set, del} from '../redis/utils'

// Redis key constants
const REMEDY_TOKEN_KEY = 'remedy:token'
const REMEDY_TOKEN_EXPIRY_KEY = 'remedy:token:expiry'

// Buffer time in seconds before token expiry to refresh (15 minutes)
const TOKEN_EXPIRY_BUFFER = 900

// In-flight promise to prevent multiple simultaneous token requests
let tokenRequestInFlight: Promise<string> | null = null

/**
 * Get a valid access token for Remedy API calls
 * - Returns cached token from Redis if valid
 * - Otherwise fetches a new token and caches it
 * - Uses in-flight promise to prevent multiple simultaneous token requests
 */
export const getRemedyAccessToken = async (): Promise<string> => {
    // If there's already a token request in progress, wait for it
    if (tokenRequestInFlight) {
        logger.debug('Remedy Auth: Using in-flight token request')
        return tokenRequestInFlight
    }

    try {
        // Create a new token request and store the promise
        tokenRequestInFlight = fetchRemedyAccessToken()
        return await tokenRequestInFlight
    } finally {
        // Clear the in-flight promise when done
        tokenRequestInFlight = null
    }
}

/**
 * Fetch a Remedy access token, either from cache or from the auth endpoint
 */
async function fetchRemedyAccessToken(): Promise<string> {
    const {remedyWO} = secrets()

    try {
        // Try to get token from Redis
        const cachedToken = await get<string>(REMEDY_TOKEN_KEY)
        const cachedExpiry = await get<string>(REMEDY_TOKEN_EXPIRY_KEY)

        // Check if we have a valid cached token
        if (cachedToken && cachedExpiry) {
            const expiryTime = parseInt(cachedExpiry, 10)
            const now = Date.now()

            // If token is still valid (with buffer time)
            if (expiryTime > now + TOKEN_EXPIRY_BUFFER * 1000) {
                logger.debug('Remedy Auth: Using cached token')
                return cachedToken
            }

            logger.debug('Remedy Auth: Cached token expired or expiring soon')
        }

        // No valid cached token, fetch a new one
        logger.info('Remedy Auth: Requesting new token')

        // Create https agent to disable certificate validation
        const httpsAgent = new https.Agent({
            rejectUnauthorized: false, // Disable certificate validation
        })

        // eslint-disable-next-line camelcase
        const response = await axios.post(
            remedyWO.authUrl,
            {
                // eslint-disable-next-line camelcase
                grant_type: 'client_credentials',
                // eslint-disable-next-line camelcase
                client_id: remedyWO.clientID,
                // eslint-disable-next-line camelcase
                client_secret: remedyWO.clientSecret,
            },
            {
                headers: {
                    'Content-Type': 'application/json',
                    Accept: 'application/json',
                },
                timeout: 10000, // 10 second timeout
                httpsAgent, // Use the custom agent to bypass certificate validation
            },
        )

        // Extract token and expiry from response
        // eslint-disable-next-line camelcase
        const accessToken =
            response.data.access_token || response.data.accessToken
        // eslint-disable-next-line camelcase
        const expiresIn =
            response.data.expires_in || response.data.expiresIn || 3600

        if (!accessToken) {
            throw new Error(
                'No access token received from Remedy auth endpoint',
            )
        }

        // Calculate expiry time (current time + expiresIn seconds)
        const expiryTime = Date.now() + expiresIn * 1000

        // Cache the token and its expiry in Redis with TTL
        await set(REMEDY_TOKEN_KEY, accessToken, expiresIn)
        await set(REMEDY_TOKEN_EXPIRY_KEY, expiryTime.toString(), expiresIn)

        logger.info('Remedy Auth: New token cached')

        return accessToken
    } catch (error: any) {
        logger.error('Remedy Auth: Failed to get access token', error.message)
        throw new Error('Failed to get Remedy access token')
    }
}

/**
 * Force refresh the Remedy access token
 * Useful when receiving a 401 Unauthorized response
 */
export const refreshRemedyAccessToken = async (): Promise<string> => {
    // Delete existing cached token
    await del(REMEDY_TOKEN_KEY)
    await del(REMEDY_TOKEN_EXPIRY_KEY)

    // Get a fresh token
    return getRemedyAccessToken()
}
