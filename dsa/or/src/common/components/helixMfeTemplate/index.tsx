import {Spinner} from '@backyard/react'
import {FabrikLoader} from '@fabrik/component'
import {DynamicRemoteContainer} from '@<url>/helix-core/dist/api/dynamicRemoteContainer'
import React, {useEffect, useState} from 'react'
import {useHistory, useLocation, useParams} from 'react-router-dom'
import AdvertisersContext from '../../context/AdvertisersContext'
import UserAccessContext from '../../context/UserAccessContext'
import useFetch from '../../hooks/useFetch'
import {UserAccess} from '../../initialStates/user'
import {getAccessToken} from '../../utils/authUtils'
import {getBasePath} from '../../utils/commonUtils'
import AccessAuth from '../accessAuth'
import ErrorTemplate from './errorTemplate'
import {AppObjProps, MfeTemplateProps, UrlParamProps} from './interface'
import SpinnerWrapper from './styles'
import {getAppModuleFromAction, getAppNameDetails} from './utils'
import RemedyTicketManagement from '../remedyTicketManagement'
import FAQ from '../faq'

const HelixMfeTemplate = (props: MfeTemplateProps) => {
    const history = useHistory()
    const location = useLocation()
    const userAccess: UserAccess = React.useContext(UserAccessContext)
    const advertiserList: any[] =
        React.useContext(AdvertisersContext)?.advertiserList || []
    // Cache MFE configuration to avoid repeated API calls on route changes
    const {value: appMap} = useFetch({
        url: `${getBasePath()}/onering/nucleus?scope=mfes-config`,
        noCache: false,
    })
    const {entity, action, id}: UrlParamProps = useParams()
    const [appDetails, setAppDetails] = useState<AppObjProps>(null)

    history.listen((locationHistory: any) => {
        if (
            appDetails?.remoteImporter === 'fabrik' &&
            !locationHistory.state?.isInitial &&
            !locationHistory.state?.isSame
        ) {
            setAppDetails({})
        }
    })

    useEffect(() => {
        if (appMap) {
            if (entity === 'settings' && action === 'access-authorization') {
                setAppDetails({remoteImporter: 'vendorAccessAuth'})
            } else if (entity === 'support' && action === 'faq') {
                setAppDetails({remoteImporter: 'vendorFAQ'})
            } else {
                const {app, remoteImporter, url, scope, tab, appAction} =
                    getAppNameDetails(appMap, entity)
                // Use timestamp for cache-busting instead of access token
                const atForCb = Date.now().toString()
                setAppDetails({
                    app,
                    remoteImporter,
                    url: `${url}?cb=${atForCb}`,
                    scope,
                    tab,
                    appAction,
                })
            }
        }
    }, [entity, action, id, appMap])

    const remoteTypeBasedMFE = () => {
        if (!appDetails?.remoteImporter) {
            return (
                <SpinnerWrapper>
                    <Spinner show inline />
                </SpinnerWrapper>
            )
        }
        if (
            appDetails?.remoteImporter === 'vendorAccessAuth' &&
            userAccess?.userId
        ) {
            return <AccessAuth />
        }
        if (
            appDetails?.remoteImporter === 'vendorSupport' &&
            userAccess?.userId
        ) {
            return <RemedyTicketManagement />
        }
        if (appDetails?.remoteImporter === 'vendorFAQ' && userAccess?.userId) {
            return <FAQ />
        }
        if (appDetails?.remoteImporter === 'fabrik') {
            return (
                <FabrikLoader
                    errorFallback={<ErrorTemplate />}
                    appName={appDetails.app}
                    url={`${appDetails.url}`}
                    compProps={{
                        ...userAccess,
                        tab: appDetails.tab,
                        selectedTab: appDetails.tab[action],
                        routeState: location.state,
                    }}
                    scopeModule={appDetails.scope[action]}
                />
            )
        }

        if (appDetails?.remoteImporter === 'helix') {
            return (
                <DynamicRemoteContainer
                    url={appDetails.url}
                    scope={appDetails.app}
                    module={getAppModuleFromAction(
                        appDetails.scope,
                        appDetails.appAction,
                        action,
                    )}
                    lazy
                    compProps={{
                        userAccess,
                        advertiserList,
                        action,
                        id,
                        tab: appDetails.tab[action],
                        routeState: location.state,
                    }}
                />
            )
        }
        return <ErrorTemplate />
    }

    return (
        <>
            {!entity && <div>Page not found</div>}
            {!!userAccess?.userId && remoteTypeBasedMFE()}
        </>
    )
}

export default HelixMfeTemplate
