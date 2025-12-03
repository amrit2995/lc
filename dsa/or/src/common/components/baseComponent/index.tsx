import React, {useEffect, useState} from 'react'
import DOMPurify from 'dompurify'
import * as FullStory from '@fullstory/browser'
import {Typography} from '@backyard/react'
import {useHistory} from 'react-router-dom'
import AdvertisersContext from '../../context/AdvertisersContext'
import LogoutContext from '../../context/LogoutContext'
import SideDrawContext from '../../context/SideDrawContext'
import UserAccessContext from '../../context/UserAccessContext'
import {NavigationProvider} from '../../context/NavigationContext'
import {UserAccess} from '../../initialStates/user'
import logoutRoutes from '../../logoutRoutes'
import forbiddenRoutes from '../../forbiddenRoutes'
import routes from '../../routes'
import {getBasePath, getEnv} from '../../utils/commonUtils'
import {getAdvertisers, getBrandsByVbuIds} from '../../utils/kuber/advertisers'
import {getUserAccess, logout} from '../../utils/kuber/session'
import AppBarComponent from '../appBarComponent'
import Modal from '../modal'
import {ModalProps} from '../modal/interface'
import RouteComponent from '../routeComponent'
import SideDrawer from '../sideDrawer'
import BaseComponentWrapper from './styles'
import useFetch from '../../hooks/useFetch'
import {VendorDetails, IntegrationConfig} from './interface'
import {maskName} from './utils'
import TrackifyContainer from '../Trackify'

const BaseComponent = () => {
    const history = useHistory()
    const {value: integrationConfig} = useFetch({
        url: `${getBasePath()}/onering/nucleus?scope=app-integrations-config`,
        noCache: false,
    })

    const [isSideDrawOpen, setIsSideDrawOpen] = useState(false)
    const [isSideDrawHover, setIsSideDrawHover] = useState(false)
    const [advertiserList, setAdvertiserList] = useState([])
    const [userAccess, setUserAccess] = useState<UserAccess>(null)
    const [modal, setModal] = useState<ModalProps>(null)
    const [isLoggedOut, setIsLoggedOut] = useState<boolean>(false)
    const [staticRbacConfig, setStaticRbacConfig] = useState<any>(null)
    const [isUserHaveAccess, setIsUserHaveAccess] = useState<boolean>(true)
    const [vendorDetails, setVendorDetails] = useState<VendorDetails>(null)
    const [tenantRoleKeys, setTenantRoleKeys] = useState<Array<string>>([])
    const fetchAccess = async () => {
        const [, access] = await getUserAccess()
        setUserAccess(access)
        if (access?.roleName) {
            fetchAdvertisers()
        }
        if (
            access?.user_type?.toLowerCase() !== 'employee' &&
            access?.vbuList?.length
        ) {
            const vendorObject = await getBrandsAssociated(access?.vbuList)
            setVendorDetails(vendorObject)
        }
    }

    const fetchAdvertisers = async () => {
        const [, advertisers] = await getAdvertisers()
        if (advertisers?.length) {
            if (advertisers[0] === 'java.util.ArrayList') {
                setAdvertiserList(advertisers[1])
            } else {
                setAdvertiserList(advertisers)
            }
        } else {
            setAdvertiserList([])
        }
    }

    const handleOnReLogin = async () => {
        setIsLoggedOut(true)
        setModal({isOpen: false})
        // Stopping Trackify before logout
        try {
            if (window?.Trackify?.replayHub?.stop) {
                window.Trackify.replayHub.stop()
            }
        } catch (e) {
            console.error('Failed to stop Trackify before logout', e)
        }
        const [err, res] = await logout()
        if (err) {
            history.push(`${getBasePath()}/logout`)
        } else {
            const redirectURL = res.redirectUrl
            if (redirectURL?.includes(`${getBasePath()}/logout`)) {
                history.push(`${getBasePath()}/logout`)
            } else {
                window.location.replace(redirectURL)
            }
        }
    }

    const handleOnInterceptorError = () => {
        setModal({
            isOpen: true,
            acceptBtnLabel: 'Login',
            declineBtnLabel: null,
            hideCloseCrossBtn: true,
            onAccept: handleOnReLogin,
            title: 'Session Expired',
            body: (
                <>
                    <Typography>Please login again</Typography>
                </>
            ),
        })
    }

    const handleOnIdleTimeoutError = () => {
        setModal({
            isOpen: true,
            acceptBtnLabel: 'Login',
            declineBtnLabel: null,
            hideCloseCrossBtn: true,
            onAccept: handleOnReLogin,
            title: 'Idle Session Timeout!',
            body: (
                <>
                    <Typography>
                        Your session has expired due to inactivity. Please log
                        in again to continue
                    </Typography>
                </>
            ),
        })
    }

    const getBrandsAssociated = async (vbuList: any[]) => {
        const vbuIds = vbuList?.map((item) => item.vbu).flat()
        const [, brands] = await getBrandsByVbuIds(vbuIds)
        return {
            brands: Array.from(new Set(brands)).join(', '),
            vbuIds: Array.from(
                new Set(vbuList?.map((item) => item?.vbu?.split('_')[0]) ?? []),
            )?.join(', '),
        }
    }

    const isValidUrl = (url: string) => {
        const allowedDomains = [
            "test"
        ]

        try {
            const urlObj = new URL(url)
            return allowedDomains.includes(urlObj.hostname)
        } catch (err) {
            return false
        }
    }

    const initializeEcko = (config: IntegrationConfig) => {
        const ekoKey = config?.ecko?.key
        const ekoValue = {
            id: config?.ecko?.value,
        }
        window[ekoKey] = ekoValue

        if (isValidUrl(config?.ecko?.src)) {
            const sanitizedSrc = DOMPurify.sanitize(config.ecko.src)
            const script = document.createElement('script')
            script.async = true
            script.src = sanitizedSrc
            document.head.appendChild(script)
        }
    }

    const initializeFullStory = () => {
        FullStory.init({
            orgId: '155KKH',
            recordCrossDomainIFrames: true,
            devMode: getEnv() !== 'prod',
        })
        FullStory.identify(userAccess?.uniqueid, {
            displayName: userAccess?.fullName,
            email: userAccess?.email || '',
            userType: userAccess?.user_type,
        })
    }

    const initializeTrackify = async (config: IntegrationConfig) => {
        const trackifyConfig = {
            sourceId: config?.trackify?.sourceId,
            sourceName: config?.trackify?.sourceName,
            env: config?.trackify?.env,
            replayHub: {
                active: true,
                __DISABLE_SECURE_MODE: true,
                // Default capture mode for input values, 0: capture input values as they are (plain)
                // 1: mask the input values or 2: ignored - do not capture the input values.
                defaultInputMode: 1,
                // Numbers will be converted to chain of 0's, if true.
                obscureTextNumbers: false,
                // Emails will be converted to a random chain of asterisks, if true.
                obscureTextEmails: false,
            },
            context: {
                fullName: userAccess?.fullName,
                userID: userAccess?.uniqueid,
                email: userAccess?.email || '',
                isExternalUser: userAccess?.user_type
                    ? userAccess?.user_type?.toLowerCase() !== 'employee'
                    : false,
                horizonRoleName: userAccess?.horizonRoleName,
                roleName: userAccess?.roleName,
                rrdRoleName: userAccess?.rrdRoleName,
                vertexRoleName: userAccess?.vertexRoleName,
                entSocialRoleName: userAccess?.entSocialRoleName,
                entEmailRoleName: userAccess?.entEmailRoleName,
                tenants: userAccess?.tenants || [],
                brands: vendorDetails?.brands || '',
            },
        }
        const networkConfig = {
            capturePayload: true,
        }
        const script = document.createElement('script')
        let scriptSrc = config?.trackify?.src

        if (trackifyConfig.env === 'prod') {
            try {
                const res = await fetch(
                    "url",
                )
                const version = await res.text()
                scriptSrc = `<url>`
            } catch (err) {
                console.error('Error fetching trackify version:', err)
            }
        }
        if (isValidUrl(scriptSrc)) {
            script.src = DOMPurify.sanitize(scriptSrc)
            document.body.appendChild(script)
            script.addEventListener('load', async () => {
                if (
                    typeof window !== 'undefined' &&
                    typeof window.Trackify !== 'undefined'
                ) {
                    await window.Trackify.init({
                        ...trackifyConfig,
                        network: networkConfig,
                    })
                    setTimeout(() => {
                        window.Trackify.setUser(config?.trackify?.sourceName, {
                            customerId: userAccess?.uniqueid,
                            emailId: userAccess?.email || '',
                        })
                        window.Trackify.replayHub.setUserAnonymousID(
                            maskName(userAccess?.fullName) ||
                                userAccess?.userId,
                        )
                    }, 5000)
                }
            })
        }
    }

    useEffect(() => {
        fetchAccess()

        window.addEventListener('interceptorErr403', handleOnInterceptorError)
        window.addEventListener('idleTimeoutError', handleOnIdleTimeoutError)
        return () => {
            window.removeEventListener(
                'interceptorErr403',
                handleOnInterceptorError,
            )
            window.removeEventListener(
                'idleTimeoutError',
                handleOnInterceptorError,
            )
        }
    }, [])

    useEffect(() => {
        const hasValidData =
            userAccess &&
            integrationConfig &&
            Object.keys(userAccess).length > 0 &&
            Object.keys(integrationConfig).length > 0
        if (hasValidData) {
            console.log('vendorDetails.  ', vendorDetails)
            initializeEcko(integrationConfig)
            initializeTrackify(integrationConfig)
            initializeFullStory()
        }
    }, [integrationConfig, userAccess, vendorDetails])

    const handleOnSideDrawChange = () => {
        setIsSideDrawOpen(!isSideDrawOpen)
        setIsSideDrawHover(false)
    }

    const handleOnSideDrawHoverIn = () => {
        if (!isSideDrawOpen) {
            setIsSideDrawHover(true)
        }
    }

    const handleOnSideDrawHoverOut = () => {
        if (isSideDrawHover) {
            setIsSideDrawHover(false)
        }
    }

    const handleOnLoggedOut = (value: boolean) => {
        setIsLoggedOut(value)
    }

    const handleOnStaticConfigUpdate = (value: any) => {
        setStaticRbacConfig(value)
    }

    return (
        <BaseComponentWrapper>
            <TrackifyContainer>
                {!!userAccess && (
                    <div
                        style={{
                            display: 'flex',
                            flexDirection: 'column',
                            height: '100%',
                        }}
                    >
                        <LogoutContext.Provider
                            value={{
                                isLoggedOut,
                                onLoggedOut: handleOnLoggedOut,
                            }}
                        >
                            <UserAccessContext.Provider value={userAccess}>
                                <AdvertisersContext.Provider
                                    value={{advertiserList, vendorDetails}}
                                >
                                    <NavigationProvider>
                                        {!isLoggedOut && isUserHaveAccess && (
                                            <React.Fragment>
                                                <Modal {...modal} />
                                                <AppBarComponent
                                                    onBurgerClick={
                                                        handleOnSideDrawChange
                                                    }
                                                    staticData={
                                                        staticRbacConfig ?? {}
                                                    }
                                                    setTenantRoleKeys={
                                                        setTenantRoleKeys
                                                    }
                                                />
                                                <div
                                                    style={{
                                                        display: 'flex',
                                                        flexDirection: 'row',
                                                        height: '100%',
                                                    }}
                                                >
                                                    <SideDrawContext.Provider
                                                        value={{
                                                            isOpen: isSideDrawOpen,
                                                            onChange:
                                                                handleOnSideDrawChange,
                                                            isHovered:
                                                                isSideDrawHover,
                                                            onHoverIn:
                                                                handleOnSideDrawHoverIn,
                                                            onHoverOut:
                                                                handleOnSideDrawHoverOut,
                                                        }}
                                                    >
                                                        <SideDrawer
                                                            userAccess={
                                                                userAccess
                                                            }
                                                            staticData={
                                                                staticRbacConfig ||
                                                                null
                                                            }
                                                            setIsUserHaveAccess={
                                                                setIsUserHaveAccess
                                                            }
                                                            tenantRoleKeys={
                                                                tenantRoleKeys
                                                            }
                                                            onStaticConfig={
                                                                handleOnStaticConfigUpdate
                                                            }
                                                        />
                                                    </SideDrawContext.Provider>
                                                    <div
                                                        style={{
                                                            padding: '10px',
                                                            width: isSideDrawOpen
                                                                ? `calc(100% - 260px)`
                                                                : `calc(100% - 64px)`,
                                                            marginLeft:
                                                                isSideDrawOpen
                                                                    ? '260px'
                                                                    : '64px',
                                                            marginTop: '64px',
                                                        }}
                                                    >
                                                        <div
                                                            style={{
                                                                padding: '15px',
                                                            }}
                                                        >
                                                            <RouteComponent
                                                                routes={routes}
                                                            />
                                                        </div>
                                                    </div>
                                                </div>
                                            </React.Fragment>
                                        )}
                                        {isLoggedOut && (
                                            <RouteComponent
                                                routes={logoutRoutes}
                                            />
                                        )}
                                        {!isUserHaveAccess && (
                                            <RouteComponent
                                                routes={forbiddenRoutes}
                                            />
                                        )}
                                    </NavigationProvider>
                                </AdvertisersContext.Provider>
                            </UserAccessContext.Provider>
                        </LogoutContext.Provider>
                    </div>
                )}
            </TrackifyContainer>
        </BaseComponentWrapper>
    )
}

export default React.memo(BaseComponent)
