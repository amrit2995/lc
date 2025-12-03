import {Theme} from '@backyard/design-tokens'
import {Dropdown, DropdownChangeInfo, Link} from '@backyard/react'
import React, {useContext, useEffect, useState} from 'react'
import lormnLogo from '../../../assets/logo/lmn-hub-logo-horizontal-white.png'
import {getBasePath} from '../../utils/commonUtils'
import NotificationDraw from '../notificationDraw'
import SearchComponent from '../searchComponent'
import UserProfile from '../userProfile'
import {
    BtnRow,
    FlexItem,
    Overwrite,
    StyledIconButton,
    StyledMenuIcon,
    DropdownWrapper,
} from './styles'
import UserAccessContext from '../../context/UserAccessContext'
import {useNavigation} from '../../context/NavigationContext'
import {UserAccess} from '../../initialStates/user'

const AppBarComponent = (props: {
    onBurgerClick: () => void
    staticData: {displayNameConfig: any}
    setTenantRoleKeys: any
}) => {
    const userAccess: UserAccess = useContext(UserAccessContext)
    const {setAutoNavigate} = useNavigation()
    // Use string values to avoid 0 being treated as falsy
    const [selectedTenant, setSelectedTenant] = useState<string>('0')
    const [tenantOptions, setTenantOptions] = useState<Array<any>>([])

    // Simple onChange handler without memoization
    const onTenantSwitcherChange = (_: any, tenant: DropdownChangeInfo) => {
        const tenantValue = tenant.value as string
        sessionStorage.setItem('tenantValue', String(tenant.value))
        setSelectedTenant(tenantValue)

        // Convert string value back to number for array index
        const index = Number(tenantValue)

        // Access the roleGroups directly from userAccess using the index
        const roleNameKeys = userAccess.tenants[index]?.roleGroups || []
        setAutoNavigate(true)
        props.setTenantRoleKeys(roleNameKeys)
    }

    // Function to find tenant index based on URL path
    const findTenantIndexByPath = (path: string): string | null => {
        if (!userAccess?.tenants?.length) return null

        // Extract path segments
        const pathSegments = path.split('/').filter((segment) => segment)

        // Check if we have a path segment that matches a tenant label
        let matchedIndex = null
        userAccess.tenants.forEach((tenant, index) => {
            const tenantLabel = tenant.label.toLowerCase().replace(/\s+/g, '-')

            // Check if any path segment matches the tenant label
            if (pathSegments.some((segment) => segment === tenantLabel)) {
                matchedIndex = String(index)
            }
        })

        return matchedIndex
    }

    useEffect(() => {
        // Only set the initial selection and role keys if we have tenants
        if (userAccess?.tenants?.length) {
            // Format tenant options with string values
            const formattedTenants = userAccess.tenants.map(
                (option: any, index: number) => ({
                    ...option,
                    value: String(index), // Use string values to avoid 0 being falsy
                }),
            )
            setTenantOptions(formattedTenants)

            // Check if URL path contains a tenant identifier
            const currentPath = window.location.pathname
            const pathTenantIndex = findTenantIndexByPath(currentPath)

            // Priority for tenant selection:
            // 1. URL path-based tenant
            // 2. Saved tenant from session storage
            // 3. Default to first tenant (0)
            const tenantValue = pathTenantIndex || '0'

            // Save the selected tenant to session storage
            sessionStorage.setItem('tenantValue', tenantValue)
            setSelectedTenant(tenantValue)

            // Set the initial role keys
            const roleNameKeys =
                userAccess.tenants[Number(tenantValue)]?.roleGroups || []
            props.setTenantRoleKeys(roleNameKeys)

            // Don't auto-navigate if we're already on a specific path
            setAutoNavigate(false)
        }
    }, [userAccess.tenants])

    return (
        <Overwrite>
            <StyledIconButton
                shape="squared"
                size="full-width"
                variant="ghost"
                onClick={props.onBurgerClick}
            >
                <StyledMenuIcon color={Theme.color.white} />
            </StyledIconButton>
            <FlexItem>
                <Link to={`${getBasePath()}/`}>
                    <img
                        alt="Oneroof logo"
                        style={{
                            height: '48px',
                            objectFit: 'contain',
                            marginTop: '20%',
                            marginBottom: '15%',
                            zIndex: 99,
                        }}
                        src={lormnLogo}
                    />
                </Link>
            </FlexItem>
            <BtnRow>
                {tenantOptions.length ? (
                    <DropdownWrapper>
                        {/* Wrap in a div to prevent event bubbling */}
                        <div style={{pointerEvents: 'auto'}}>
                            <Dropdown
                                key="tenant-dropdown"
                                style={{
                                    width: '200px',
                                    WebkitTextFillColor:
                                        'rgba(255, 255, 255, 1)',
                                }}
                                onChange={onTenantSwitcherChange}
                                size="small"
                                options={tenantOptions}
                                label="Business Line"
                                value={selectedTenant}
                                disabled={tenantOptions.length === 1}
                                data-testid="tenant-dropdown"
                            />
                        </div>
                    </DropdownWrapper>
                ) : null}
                <NotificationDraw />
                <UserProfile
                    displayNameConfig={
                        props?.staticData?.displayNameConfig ?? {}
                    }
                />
            </BtnRow>
        </Overwrite>
    )
}

export default React.memo(AppBarComponent)
