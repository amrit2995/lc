import {Spinner, Typography} from '@backyard/react'
import React, {useEffect, useState} from 'react'
import {useHistory} from 'react-router-dom'
import logo from '../../../assets/favicon.png'
import {setCurrentPage, waitForAuthCookie} from '../../utils/authUtils'
import useFetch from '../../hooks/useFetch'
import {
    getSessionInfo,
    initiateLogin,
    isActiveSession,
    verifyCallback,
} from '../../utils/kuber/session'
import BaseComponent from '../baseComponent'
import {getBasePath} from '../../utils/commonUtils'
import {SessionStatus} from './interface'
import {Cover, Row, RowWithMargin} from './styles'

const LmnHome = () => {
    const history = useHistory()
    const [sessionStatus, setSessionStatus] = useState<SessionStatus>('loading')

    const triggerNoAccessJourney = () => {
        setSessionStatus('invalid')
    }

    const triggerLoginJourney = async () => {
        try {
            const redirectUrlResponse = await initiateLogin()
            if (redirectUrlResponse.redirectURL)
                window.location.replace(redirectUrlResponse.redirectURL)
        } catch (error) {
            console.error('Error in OAuth', error)
            triggerNoAccessJourney()
        }
    }

    const triggerValidSessionJourney = () => {
        setSessionStatus('valid')
        // const currentPage = getCurrentPage()
        // if (currentPage && currentPage.split('/lormn')?.[1]) {
        //     history.push(`/lormn${currentPage.split('/lormn')?.[1]}`)
        // }
    }

    const triggerSessionVerificationJourney = async () => {
        const sessionInfo = await getSessionInfo()
        if (sessionInfo?.userId) {
            triggerValidSessionJourney()
        } else {
            triggerLoginJourney()
        }
    }

    const triggerPostRedirectJourney = async (code: string, state: string) => {
        const sessionData = await verifyCallback(code, state)
        if (sessionData?.error) {
            // Check for the specific 400 status code
            if (sessionData?.status === 403) {
                // Handle other error cases
                triggerNoAccessJourney()
            } else {
                triggerLoginJourney() // Redirect back to login instead of no access
            }
        } else {
            triggerValidSessionJourney()
        }
    }

    useEffect(() => {
        setCurrentPage()
        const handleAuthFlow = async () => {
            const searchParams = new URLSearchParams(window.location.search)
            const code = searchParams.get('code')
            const state = searchParams.get('state')

            if (code && state) {
                triggerPostRedirectJourney(code, state)
            } else {
                const redisAccessToken = await waitForAuthCookie()
                if (!redisAccessToken) {
                    triggerLoginJourney()
                } else {
                    triggerSessionVerificationJourney()
                }
            }
        }

        handleAuthFlow()
    }, [])

    useEffect(() => {
        document.onvisibilitychange = () => {
            if (!document.hidden) {
                const now = Date.now()
                const oneMinute = 60 * 1000

                const lastCheck = parseInt(
                    window.sessionStorage.getItem('lastSessionCheck') || '0',
                    10,
                )

                if (now - lastCheck >= oneMinute) {
                    window.sessionStorage.setItem(
                        'lastSessionCheck',
                        now.toString(),
                    )
                    ;(async () => {
                        const isValid = await isActiveSession()
                        if (!isValid) {
                            const event = new CustomEvent('idleTimeoutError')
                            window.dispatchEvent(event)
                        }
                    })()
                }
            }
        }

        if (document !== undefined) {
            document.body.style.backgroundColor = '#F5F5F5'
            document.title = "Lowe's Media Network"
            const link = document.createElement('link')
            link.setAttribute('rel', 'icon')
            link.setAttribute('href', logo)
            link.setAttribute('type', 'image/icon type')
            document.head.appendChild(link)
        }
    }, [])

    return (
        <div>
            {sessionStatus === 'valid' && <BaseComponent />}
            {sessionStatus === 'loading' && (
                <Cover>
                    <Row>
                        <RowWithMargin>
                            <Typography variant="body_1" color="white">
                                Loading...
                                <Spinner color="white" show small inline />
                            </Typography>
                        </RowWithMargin>
                    </Row>
                </Cover>
            )}
            {sessionStatus === 'invalid' && (
                <Cover>
                    <Row>
                        <RowWithMargin>
                            <Typography variant="body_1" color="white">
                                403 <Spinner color="white" show small inline />
                            </Typography>
                        </RowWithMargin>
                    </Row>
                </Cover>
            )}
        </div>
    )
}

LmnHome.propTypes = {}

export default React.memo(LmnHome)
