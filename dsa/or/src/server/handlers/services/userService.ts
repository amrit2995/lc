import {get, set} from '../../redis/utils'
import {
    OIDCUserToken,
    UserDetails,
    UserInfo,
    UserSession,
} from '../interfaces/sessionProps'
import {findOne, insertOne, replaceOne} from '../../mongo/client'
import logger from '../../plugins/logger'
import {
    buildUserRoles,
    findAdvertisersByVbuIdsAndReturnObjectIds,
    findAllAdvertisers,
    generateVendorMappingsForAdvertiserIds,
} from './loginMapping'
import {fetchNucleusConfig} from '../nucleusHandler'
import {saveUserToDb} from '../../utils/auth'
import secrets from '../../secrets'
import {REDIS_USER_TAG} from '../../utils/constants'

const {
    redisTTL: {userExpiry},
} = secrets()

const returnUserFromRedisOrDbAndUpdate = async (
    userId: string,
    oidcUserToken: OIDCUserToken,
): Promise<UserSession | null> => {
    try {
        const redisKey = `${REDIS_USER_TAG}${userId}`
        const user: UserSession = await get(redisKey)

        if (user) {
            // Update OIDC token fields
            user.accessToken = oidcUserToken.access_token
            user.refreshToken = oidcUserToken.refresh_token
            user.idToken = oidcUserToken.id_token
            user.lastUpdatedAt = Date.now()

            await set(redisKey, user, userExpiry)
            return user
        }

        const dbUser: UserSession = await findOne<UserSession>(
            'user',
            'userId',
            userId,
        )
        if (dbUser) {
            const updatedUser: UserSession = {
                ...dbUser,
                accessToken: oidcUserToken.access_token,
                refreshToken: oidcUserToken.refresh_token,
                idToken: oidcUserToken.id_token,
                lastUpdatedAt: Date.now(),
            }

            await replaceOne<UserSession>('user', 'userId', userId, updatedUser)
            return updatedUser
        }

        return null
    } catch (error) {
        logger.error('Error fetching or updating user from Redis or DB:', error)
        return null
    }
}

const findAndUpdateOrCreateUser = async (
    user: UserSession,
): Promise<UserSession | null> => {
    const dbUser: UserSession = await findOne('user', 'userId', user.userId)

    if (!dbUser) {
        const newUser: UserSession = {...user}
        if (
            !user.vendorMappings &&
            user.isExternalUser &&
            user.advertisers?.length
        ) {
            newUser.vendorMappings =
                await generateVendorMappingsForAdvertiserIds(
                    newUser.advertisers,
                )
        }
        await insertOne('user', newUser)
        return newUser
    }

    // only take necessary details from db user
    const updatedUser: UserSession = {
        userId: dbUser.userId,
        vendorMappings: dbUser.vendorMappings || {},
        allowAllAdvertisers: dbUser.allowAllAdvertisers || false,
        ...user,
    }

    if (
        !updatedUser.vendorMappings &&
        updatedUser.isExternalUser &&
        updatedUser.advertisers?.length
    ) {
        updatedUser.vendorMappings =
            await generateVendorMappingsForAdvertiserIds(
                updatedUser.advertisers,
            )
    }

    if (dbUser.allowAllAdvertisers) {
        updatedUser.advertisers = await findAllAdvertisers()
    } else {
        updatedUser.advertisers = Array.from(
            new Set([
                ...(dbUser.advertisers || []),
                ...(user.advertisers || []),
            ]),
        )
    }

    await replaceOne('user', 'userId', user.userId, updatedUser)

    return updatedUser
}

const findOrGenerateUser = async (
    userInfo: UserInfo,
    updateCall: boolean,
    oidcUserToken: OIDCUserToken,
): Promise<UserSession> => {
    if (updateCall) {
        return returnUserFromRedisOrDbAndUpdate(userInfo.sub, oidcUserToken)
    }

    const advertiserIds = userInfo?.vbuList?.length
        ? await findAdvertisersByVbuIdsAndReturnObjectIds(userInfo.vbuList)
        : []

    const isExternalUser = userInfo.user_type
        ? userInfo.user_type.toLowerCase() !== 'employee'
        : false

    const userDetails: UserDetails = {
        name:
            `${userInfo?.given_name || ''} ${
                userInfo?.family_name || ''
            }`.trim() || 'N/A',
        email: userInfo.email,
    }

    const baseUser: UserSession = {
        userId: userInfo.sub,
        userDetails,
        advertisers: advertiserIds,
        lastUpdatedAt: Date.now(),
        accessToken: oidcUserToken.access_token,
        refreshToken: oidcUserToken.refresh_token,
        idToken: oidcUserToken.id_token,
        isExternalUser,
    }

    const nucleusMapping = await fetchNucleusConfig('user-role-config')
    const roles = buildUserRoles(
        nucleusMapping,
        userInfo.authorities,
        isExternalUser,
    )

    const currentUser: UserSession = {
        ...baseUser,
        ...roles,
    }

    const shouldPersist = saveUserToDb(
        nucleusMapping?.persistUserOn ?? [],
        userInfo.authorities,
    )

    if (shouldPersist) {
        return findAndUpdateOrCreateUser(currentUser)
    }

    await set(`${REDIS_USER_TAG}${currentUser.userId}`, currentUser, userExpiry)

    return currentUser
}

export {findOrGenerateUser, returnUserFromRedisOrDbAndUpdate}
