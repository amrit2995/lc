import {remedyNotificationHandler} from '../handlers/remedyTicketHandler'

const basePath = process.env.BASE_PATH

/**
 * Remedy API Routes for notification handling
 */
export default [
    {
        method: 'POST',
        path: `${basePath}/remedy/notification`,
        handler: remedyNotificationHandler,
        description:
            'Handle remedy notifications for orders with different notification types',
    },
]
