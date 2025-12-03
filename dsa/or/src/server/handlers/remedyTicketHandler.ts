import axios from 'axios'
import secrets from '../secrets'
import PostieEmailService from '../services/postieEmailService'
import {
    getRemedyAccessToken,
    refreshRemedyAccessToken,
} from '../services/remedyAuthService'

/**
 * Normalize email domain from @<url>clqa.com to @<url>.com
 */
const normalizeEmailDomain = (email: string): string => {
    return email.replace('@<url>clqa.com', '@<url>.com')
}

const {remedyWO} = secrets()

/**
 * Handler for /remedy/notification endpoint
 * Processes order notifications with different types (StatusChange, WorkOrderUpdate, etc.)
 */
interface RemedyNotificationRequest {
    orderId: string
    emailId: string
    notificationType: 'StatusChange' | 'WorkOrderUpdate' | string
    message?: string
    timestamp?: string
}
const postRemedyTicketHandler = async (request: any, response: any) => {
    try {
        const {subject, description, email, isVendor, lowVBU} = request.body

        request.log.info('API - postRemedyTicketHandler - received request', {
            subject,
            description,
            email,
            isVendor: typeof isVendor,
            lowVBU,
        })

        // Get access token from cache or request a new one
        let accessToken: string
        try {
            accessToken = await getRemedyAccessToken()
        } catch (error) {
            request.log.error(
                'API - postRemedyTicketHandler - Failed to get access token',
                error,
            )
            return response.status(401).json({
                error: 'Authentication failed - unable to obtain access token',
                details: error.message,
            })
        }
        const normalizedEmail = normalizeEmailDomain(email)
        const isVendorBool = isVendor === 'true' || isVendor === true

        const customerEmail = isVendorBool
            ? 'OneRingIntegrationUser@<url>.com'
            : normalizedEmail

        const baseValues = {
            // eslint-disable-next-line camelcase
            z1D_Action: 'CREATE',
            'Customer Internet E-mail': customerEmail,
            VendorEmail: normalizedEmail,
            Status: 'Assigned',
            Company: "Lowe's Companies, Inc.",
            'Customer Company': "Lowe's Companies, Inc.",
            'Location Company': "Lowe's Companies, Inc.",
            TemplateID: remedyWO.templateID,
            'LOW_VBU#': lowVBU,
            Summary: subject,
            'Detailed Description': description,
        }

        const values: any = baseValues
        // eslint-disable-next-line no-undef
        const formData = new FormData()
        if (request.files.length) {
            const fileAttachments = request.files.reduce(
                (init: string, file: any, index: number) => {
                    if (!init) {
                        return `"z2AF_Act_Attachment_${index + 1}":"${
                            file.originalname
                        }"`
                    }
                    return `${init},"z2AF_Act_Attachment_${index + 1}":"${
                        file.originalname
                    }"`
                },
                '',
            )

            const formDataValues = {
                ...baseValues,
                'View Access': 'Public',
                'Secure Work Log2': 'Yes',
                // eslint-disable-next-line camelcase
                z1D_WorklogDetails: 'Test',
                // eslint-disable-next-line camelcase
                z1D_View_Access: 'Public',
                // eslint-disable-next-line camelcase
                z1D_Details: 'Test',
            }

            formData.append(
                'entry',
                `{
                    "values":{
                    ${Object.entries(formDataValues)
                        .map(([key, value]) => `"${key}":"${value}"`)
                        .join(',\n                    ')}${
                    fileAttachments
                        ? `,\n                    ${fileAttachments}`
                        : ''
                }
                    }
                }`,
            )
            for (let i = 0; i < request.files.length; i += 1) {
                formData.append(
                    `attach-z2AF_Act_Attachment_${i + 1}`,
                    request.files[i].buffer,
                )
            }
        }

        request.log.info(
            'API - postRemedyTicketHandler - success getting token, sending remedy request',
            {
                attachments:
                    request.files.length > 0
                        ? 'With file attachments'
                        : 'No attachments',
                payload: request.files.length > 0 ? 'FormData' : values,
            },
        )
        const createRemedyResponse = await axios.post(
            remedyWO.createRemedyTicketUrl,
            request.files.length ? formData : {values},
            {
                headers: {
                    Authorization: `Bearer ${accessToken}`,
                    'Content-Type': request.files.length
                        ? 'multipart/form-data'
                        : 'application/json',
                },
            },
        )
        request.log.info(
            'API - postRemedyTicketHandler - successfully created ticket, sending 200 response',
            {
                status: 200,
                ticketId:
                    createRemedyResponse.data?.values?.['Work Order ID'] ||
                    'N/A',
            },
        )
        return response.status(200).json({
            message: 'Successfully created ticket',
            data: createRemedyResponse.data,
        })
    } catch (error: any) {
        request.log.error('API - postRemedyTicketHandler - Exception', {
            message: error.message,
            status: error.response?.status,
            statusText: error.response?.statusText,
            data: error.response?.data,
            url: error.config?.url,
        })

        // Handle authentication errors
        if (error.response?.status === 401 || error.response?.status === 403) {
            // If it's a 401, try to refresh the token once
            if (error.response?.status === 401) {
                try {
                    request.log.info(
                        'API - postRemedyTicketHandler - Refreshing token after 401',
                    )
                    // Force refresh the token
                    const newAccessToken = await refreshRemedyAccessToken()

                    // Prepare the request data again
                    const requestData = request.files.length
                        ? request.body // Use the original form data
                        : {values: request.body} // Use the original values

                    // Retry the request with the new token
                    const createRemedyResponse = await axios.post(
                        remedyWO.createRemedyTicketUrl,
                        requestData,
                        {
                            headers: {
                                Authorization: `Bearer ${newAccessToken}`,
                                'Content-Type': request.files.length
                                    ? 'multipart/form-data'
                                    : 'application/json',
                            },
                        },
                    )

                    request.log.info(
                        'API - postRemedyTicketHandler - successfully created ticket after token refresh',
                    )
                    return response.status(200).json({
                        message:
                            'Successfully created remedy ticket after token refresh',
                        data: createRemedyResponse.data,
                    })
                } catch (retryError) {
                    request.log.error(
                        'API - postRemedyTicketHandler - Failed retry after token refresh',
                        retryError,
                    )
                }
            }

            return response.status(error.response?.status || 403).json({
                error: 'Authentication failed - check remedy credentials',
                details: error.response?.data,
            })
        }

        return response.status(500).json({
            error: 'Failed to create remedy ticket',
            details: error.message,
        })
    }
}

const getRemedyTicketsHandler = async (request: any, response: any) => {
    try {
        request.log.info(
            'API - getRemedyTicketsHandler - try block start',
            request.query,
        )

        // Get access token from cache or request a new one
        let accessToken: string
        try {
            accessToken = await getRemedyAccessToken()
        } catch (error) {
            request.log.error(
                'API - getRemedyTicketsHandler - Failed to get access token',
                error,
            )
            return response.status(401).json({
                error: 'Authentication failed - unable to obtain access token',
                details: error.message,
            })
        }

        request.log.info(
            'API - getRemedyTicketsHandler - success getting token, fetching tickets',
        )
        const remedyResponse = await axios.get(remedyWO.getRemedyTicketsUrl, {
            headers: {
                Authorization: `Bearer ${accessToken}`,
            },
            params: {
                fields: 'values(Work Order ID,ASGRP,Description,Detailed Description,Status,Submit Date,First Name,Last Name,Customer Internet E-mail,VendorEmail)',
                q:
                    request.query.isAdmin === 'true'
                        ? `'TemplateID'="${remedyWO.templateID}"`
                        : `'LOW_VBU#'="${request.query.lowVBU}"`,
            },
        })
        request.log.info(
            'API - getRemedyTicketsHandler - successfully retrieved remedy tickets',
            {
                count: remedyResponse.data?.values?.length || 0,
                isAdmin: request.query.isAdmin === 'true',
                filter:
                    request.query.isAdmin === 'true' ? 'templateID' : 'lowVBU',
            },
        )
        return response.status(200).json({
            message: 'Successfully fetched remedy tickets',
            data: remedyResponse.data,
        })
    } catch (error) {
        request.log.error('API - getRemedyTicketsHandler - Exception', error)

        // Handle authentication errors
        if (error.response?.status === 401 || error.response?.status === 403) {
            // If it's a 401, try to refresh the token once
            if (error.response?.status === 401) {
                try {
                    request.log.info(
                        'API - getRemedyTicketsHandler - Refreshing token after 401',
                    )
                    // Force refresh the token
                    const newAccessToken = await refreshRemedyAccessToken()

                    // Retry the request with the new token
                    const remedyResponse = await axios.get(
                        remedyWO.getRemedyTicketsUrl,
                        {
                            headers: {
                                Authorization: `Bearer ${newAccessToken}`,
                            },
                            params: {
                                fields: 'values(Work Order ID,ASGRP,Description,Detailed Description,Status,Submit Date,First Name,Last Name,Customer Internet E-mail,VendorEmail)',
                                q:
                                    request.query.isAdmin === 'true'
                                        ? `'TemplateID'="${remedyWO.templateID}"`
                                        : `'LOW_VBU#'="${request.query.lowVBU}"`,
                            },
                        },
                    )

                    request.log.info(
                        'API - getRemedyTicketsHandler - successfully retrieved tickets after token refresh',
                    )
                    return response.status(200).json({
                        message:
                            'Successfully fetched remedy tickets after token refresh',
                        data: remedyResponse.data,
                    })
                } catch (retryError) {
                    request.log.error(
                        'API - getRemedyTicketsHandler - Failed retry after token refresh',
                        retryError,
                    )
                }
            }

            return response.status(error.response?.status || 403).json({
                error: 'Authentication failed - check remedy credentials',
                details: error.response?.data,
            })
        }

        return response.status(500).json({
            error: 'Failed to fetch remedy tickets',
            details: error.message,
        })
    }
}

const remedyNotificationHandler = async (request: any, response: any) => {
    try {
        const {orderId, emailId, notificationType, message} =
            request.body as RemedyNotificationRequest

        // Normalize email domain
        const normalizedEmailId = normalizeEmailDomain(emailId)

        // logger
        request.log.info('Raw request body received:', request.body)

        // Validate required fields
        if (!orderId || !normalizedEmailId || !notificationType) {
            request.log.info('Missing required fields in remedy notification', {
                orderId,
                emailId: normalizedEmailId,
                notificationType,
                message,
                rawRequestBody: request.body,
            })
            return response.status(400).json({
                success: false,
                message:
                    'Missing required fields: orderId, emailId, notificationType',
                timestamp: new Date().toISOString(),
            })
        }

        // Log to application logger as well
        request.log.info('Remedy notification received', {
            orderId,
            emailId: normalizedEmailId,
            notificationType,
            message,
            timestamp: new Date().toISOString(),
            ip: request.ip,
            userAgent: request.get('User-Agent'),
        })

        // Send email notification automatically based on notification type
        let emailStatus = 'skipped'
        let emailMessageId: string | undefined
        let emailError: string | undefined

        try {
            request.log.info('Sending remedy notification email', {
                orderId,
                emailId: normalizedEmailId,
                notificationType,
            })

            const emailResult = await PostieEmailService.sendRemedyNotification(
                normalizedEmailId,
                orderId,
                notificationType,
                message,
            )

            if (emailResult.success) {
                emailStatus = 'sent'
                emailMessageId = emailResult.messageId
                request.log.info('Email sent successfully', {
                    orderId,
                    emailId: normalizedEmailId,
                    messageId: emailMessageId,
                })
            } else {
                emailStatus = 'failed'
                emailError = emailResult.error
                request.log.error('Failed to send email', {
                    orderId,
                    emailId: normalizedEmailId,
                    error: emailError,
                })
            }
        } catch (error: any) {
            emailStatus = 'error'
            emailError = error.message
            request.log.error('Error sending email', {
                orderId,
                emailId: normalizedEmailId,
                error: error.message,
            })
        }

        // Return success response
        return response.status(200).json({
            success: true,
            message: 'Remedy notification processed successfully',
            data: {
                orderId,
                emailId: normalizedEmailId,
                notificationType,
                processedAt: new Date().toISOString(),
                email: {
                    status: emailStatus,
                    messageId: emailMessageId,
                    error: emailError,
                },
            },
        })
    } catch (error) {
        request.log.error('Error processing remedy notification:', error)

        return response.status(500).json({
            success: false,
            message: 'Internal server error processing remedy notification',
            timestamp: new Date().toISOString(),
        })
    }
}

export {
    postRemedyTicketHandler,
    getRemedyTicketsHandler,
    remedyNotificationHandler,
}
