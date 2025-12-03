import axios from 'axios'
import logger from '../plugins/logger'
import secrets from '../secrets'

const {postie} = secrets()
const {baseUrl, timeout, retryAttempts, loginUrl} = postie

// Create postie client instance
const postieClient = axios.create({
    baseURL: baseUrl,
    timeout: timeout || 10000,
    headers: {
        'Content-Type': 'application/json',
        'User-Agent': 'one-ring/1.0.0',
        Accept: 'application/json',
    },
})

/**
 * Async wrapper utility for handling promises
 */
const asyncWrap = async (promise: Promise<any>): Promise<[any, any]> => {
    try {
        const data = await promise
        return [null, data]
    } catch (error) {
        return [error, null]
    }
}

/**
 * Retry utility with exponential backoff
 */
const retryWithBackoff = async <T>(
    fn: () => Promise<T>,
    maxRetries: number = 3,
    baseDelay: number = 1000,
): Promise<T> => {
    let lastError: any

    for (let attempt = 0; attempt <= maxRetries; attempt += 1) {
        try {
            // eslint-disable-next-line no-await-in-loop
            return await fn()
        } catch (error: any) {
            lastError = error

            // Don't retry on authentication errors (401, 403) or client errors (4xx)
            if (error.response?.status >= 400 && error.response?.status < 500) {
                throw error
            }

            if (attempt === maxRetries) {
                break
            }

            const delay = baseDelay * 2 ** attempt
            logger.warn(
                `Postie request failed (attempt ${attempt + 1}/${
                    maxRetries + 1
                }), retrying in ${delay}ms:`,
                {
                    error: error.message,
                    status: error.response?.status,
                    attempt: attempt + 1,
                },
            )

            // eslint-disable-next-line no-await-in-loop
            await new Promise((resolve) => setTimeout(resolve, delay))
        }
    }

    throw lastError
}

/**
 * Form Postie email body for sending emails
 */
const formPostieBody = (
    emailObject: PostieEmailRequest,
): PostieEmailRequest => {
    return {
        appName: emailObject.appName || 'one-ring',
        emailName: emailObject.emailName,
        to: emailObject.to,
        cc: emailObject.cc,
        bcc: emailObject.bcc,
        subject: emailObject.subject,
        templateData: emailObject.templateData,
        priority: emailObject.priority || 'normal',
    }
}

interface PostieEmailRequest {
    appName: string
    emailName: string
    to: string | string[]
    cc?: string[]
    bcc?: string[]
    subject?: string
    templateData: Record<string, any>
    priority?: 'high' | 'normal' | 'low'
}

interface PostieResponse {
    success: boolean
    messageId?: string
    error?: string
    details?: any
}

interface PostieConfig {
    appName: string
    templateName: string
    to?: string
    subject?: string
}

/**
 * Postie Email Service for sending emails through Lowe's Postie service
 * Uses predefined templates from Postie instead of generating HTML locally
 */
class PostieEmailService {
    private readonly baseUrl: string

    private readonly timeout: number

    private readonly retryAttempts: number

    constructor() {
        this.baseUrl = baseUrl
        this.timeout = timeout || 10000
        this.retryAttempts = retryAttempts || 3
    }

    /**
     * Send email through Postie service using simple pattern
     */
    static async sendMail(
        emailObject: PostieEmailRequest,
    ): Promise<PostieResponse> {
        const emailBody = formPostieBody(emailObject)
        logger.info('emailBody for sendMail', emailBody)

        // Enhanced logging for debugging 403 errors
        logger.info('Postie request details:', {
            url: `${baseUrl}/send/email`,
            headers: postieClient.defaults.headers,
            body: emailBody,
            baseUrl,
            fullUrl: `${baseUrl}/send/email`,
        })

        const [err, data] = await asyncWrap(
            retryWithBackoff(
                () => postieClient.post('/send/email', emailBody),
                retryAttempts || 3,
                1000,
            ),
        )

        if (err) {
            logger.error('Postie send error:', {
                message: err.message,
                status: err.response?.status,
                statusText: err.response?.statusText,
                data: err.response?.data,
                headers: err.response?.headers,
                config: {
                    url: err.config?.url,
                    method: err.config?.method,
                    headers: err.config?.headers,
                    data: err.config?.data,
                },
            })
            return {
                success: false,
                error: err.message || 'Failed to send email',
                details: err,
            }
        }

        if (data?.data) {
            logger.info('Postie response received:', data.data)

            // Check if Postie response indicates success
            if (data.data.success === false) {
                logger.error('Postie returned failure:', data.data)
                return {
                    success: false,
                    error:
                        data.data.message ||
                        'Postie service failed to send email',
                    details: data.data,
                }
            }

            logger.info('Email sent successfully:', data.data)
            return {
                success: true,
                messageId:
                    data.data?.messageId ||
                    PostieEmailService.generateMessageId(),
                details: data.data,
            }
        }

        logger.error('No response data received from Postie:', data)
        return {
            success: false,
            error: 'No response data received',
            details: data,
        }
    }

    /**
     * Send remedy notification email using Postie templates
     */
    static async sendRemedyNotification(
        emailId: string,
        orderId: string,
        notificationType: string,
        message?: string,
        fullName?: string,
    ): Promise<PostieResponse> {
        const emailRequest: PostieEmailRequest = {
            appName: 'oneRing',
            emailName:
                PostieEmailService.getTemplateNameForNotificationType(
                    notificationType,
                ),
            to: [emailId],
            subject: `Remedy Ticket ${orderId} - ${notificationType} | Status Update`,
            templateData: {
                ticketNumber: orderId,
                fullName: fullName || 'User',
                loginUrl,
                message: message || 'Status change',
            },
        }

        return PostieEmailService.sendMail(emailRequest)
    }

    /**
     * Send campaign notification email using Postie templates
     */
    static async sendCampaignNotification(
        to: string,
        name: string,
        campaignName: string,
        campaignLink: string,
        subject?: string,
        postieConfig?: PostieConfig,
    ): Promise<PostieResponse> {
        const defaultConfig: PostieConfig = {
            appName: 'oneRing',
            templateName: 'ticket-closure-notification',
            subject: `Campaign Update: ${campaignName}`,
        }

        const config = {...defaultConfig, ...postieConfig}

        const emailRequest: PostieEmailRequest = {
            appName: config.appName,
            emailName: config.templateName,
            to: to || config.to || '',
            subject: subject || config.subject || '',
            templateData: {
                name,
                campaignName,
                campaignLink: 'Campaign details',
                campaignDownloadLink: campaignLink,
            },
        }

        return PostieEmailService.sendMail(emailRequest)
    }

    /**
     * Get appropriate template name based on notification type
     */
    private static getTemplateNameForNotificationType(
        notificationType: string,
    ): string {
        switch (notificationType.toLowerCase()) {
            case 'statuschange':
                return 'ticket-status-change-notification'
            case 'workorderupdate':
                return 'ticket-response-notification'
            default:
                return 'ticket-response-notification'
        }
    }

    /**
     * Generate unique message ID for tracking
     */
    private static generateMessageId(): string {
        return `one-ring-${Date.now()}-${Math.random()
            .toString(36)
            .substr(2, 9)}`
    }
}

// Export class with static methods
export default PostieEmailService
