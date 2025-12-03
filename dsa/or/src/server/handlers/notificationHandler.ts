import {findAllInWithBooleanFilter, findAllWithBoolean} from '../mongo/client'
import logger from '../plugins/logger'
import {get} from '../redis/utils'
import secrets from '../secrets'
import {getAuthorizationFromRequest} from '../utils/auth'
import {UserSession} from './interfaces/sessionProps'

const {notification} = secrets()
const {
    interval: notificationInterval,
    noLimitAllowedRoles,
    limit,
} = notification

const getNotificationsByAdvertiserId = async (advertiserIds: string[]) => {
    try {
        const notifications = await findAllInWithBooleanFilter(
            'notification',
            'advertiserId',
            advertiserIds,
            'isRead',
            false,
            limit,
        )
        return {
            results: notifications,
            count: notifications.length,
        }
    } catch (error) {
        logger.error('Error in getNotificationsByAdvertiserId ', error)
        return {
            results: [],
            count: 0,
        }
    }
}

const getAllUnreadNotifications = async () => {
    try {
        const notifications = await findAllWithBoolean(
            'notification',
            'isRead',
            false,
            limit,
        )
        return {
            results: notifications,
            count: notifications.length,
        }
    } catch (error) {
        logger.error('Error in getAllUnreadNotifications ', error)
        return {
            results: [],
            count: 0,
        }
    }
}

const getNotifications = async (request: any, response: any) => {
    try {
        const authToken = getAuthorizationFromRequest(request)
        if (authToken) {
            const sessionInfo: UserSession = await get(authToken)
            if (!sessionInfo) {
                return response.status(200).json({results: [], count: 0})
            }
            if (noLimitAllowedRoles.includes(sessionInfo.roleName)) {
                const notificationObj = await getAllUnreadNotifications()
                return response.json(notificationObj)
            }
            const advertiserIds = sessionInfo.advertisers
            const notificationObj = await getNotificationsByAdvertiserId(
                advertiserIds,
            )
            return response.json(notificationObj)
        }
        return response
            .status(401)
            .json({message: 'Missing Authorization token'})
    } catch (error) {
        request.log.error(
            'Error in reading session info for notifications',
            error,
        )
        return response.json({
            results: [],
            count: 0,
        })
    }
}

export default getNotifications
