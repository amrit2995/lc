import React from 'react'
// import {shallow} from 'enzyme'

import {render, screen, fireEvent} from '@testing-library/react'
import {ThemeProvider} from '@backyard/react'
import AppBarComponent from '.'
import LogoutContext from '../../context/LogoutContext'
import UserAccessContext from '../../context/UserAccessContext'
import AdvertisersContext from '../../context/AdvertisersContext'

jest.mock('../notificationDraw', () => () => (
    <div data-testid="notification-draw" />
))
// eslint-disable-next-line react/no-multi-comp
jest.mock('../searchComponent', () => () => (
    <div data-testid="search-component" />
))
// eslint-disable-next-line react/no-multi-comp
jest.mock('../userProfile', () => (props: any) => (
    <div data-testid="user-profile">{JSON.stringify(props)}</div>
))

// Mock image to prevent error in Jest

jest.mock('../../../assets/logo/lmn-logo-v16.png', () => 'mock-logo.png')

// Mock utility function

jest.mock('../../utils/commonUtils', () => ({
    getBasePath: () => '/base-path',
}))
const mockUserAccessValue = {
    advertisers: ['664da69b2877123473b0812e'],
    customAttributes: [],
    defaultAdvertiser: null,
    fullName: 'undefined undefined',
    horizonRoleName: 'HORIZON_ADMIN',
    id: '62bc3db385e868d758fe1546',
    lastUpdatedAt: '2023-12-01T12:34:56Z',
    refreshToken: 'NA',
    roleName: 'ADMINISTRATOR',
    rrdRoleName: 'RRD_ADMIN',
    userId: 'user-123',
    userInfo: {
        authorities: [
            'VG_SOUTHDEEP_TENANT_LMN_MANAGED',
            'VG_SOUTHDEEP_TENANT_LMN_SELF_SERVE',
        ]
    },
    vendorMappings: {
        horizonRoleName: {reporting: ['meta', 'display']},
    },
    vertexRoleName: 'VERTEX_ADMIN',
}

const mockAdvertiserList = {
    name: 'Google',
    id: '64dca791c6e3880ee76553e4',
    advertiserStatus: 'ACTIVE',
    externalId: 'google',
    users: [{userId: '3957300'}],
    wallets: [],
    userTimeZone: 'Asia_Kolkata',
}

// const mockTheme = {
//     shape: {
//         borderRadius: 4,
//     },
// }

describe('AppBarComponent', () => {
    const mockOnBurgerClick = jest.fn()

    const renderComponent = () =>
        render(
            <ThemeProvider theme={'light'} font={'fellix'}>
                <LogoutContext.Provider
                    value={{isLoggedOut: false, onLoggedOut: () => {}}}
                >
                    <UserAccessContext.Provider value={mockUserAccessValue}>
                        <AdvertisersContext.Provider
                            value={{advertiserList: mockAdvertiserList}}
                        >
                            <AppBarComponent
                                onBurgerClick={mockOnBurgerClick}
                                staticData={{
                                    displayNameConfig:,
                                }}
                            />
                        </AdvertisersContext.Provider>
                    </UserAccessContext.Provider>
                </LogoutContext.Provider>
            </ThemeProvider>,
        )

    beforeEach(() => {
        jest.clearAllMocks()
    })

    it('renders logo image correctly with alt text', () => {
        renderComponent()

        const logo = screen.getByAltText('Oneroof logo') as HTMLImageElement

        expect(logo).toBeInTheDocument()

        expect(logo.src).toContain('http://localhost/mock-logo.png')
    })

    it('calls onBurgerClick when burger icon is clicked', () => {
        renderComponent()

        const burgerButton = screen.getByRole('button')

        fireEvent.click(burgerButton)

        expect(mockOnBurgerClick).toHaveBeenCalledTimes(1)
    })

    it('renders SearchComponent', () => {
        renderComponent()

        expect(screen.getByTestId('search-component')).toBeInTheDocument()
    })

    it('renders NotificationDraw', () => {
        renderComponent()

        expect(screen.getByTestId('notification-draw')).toBeInTheDocument()
    })

    it('renders UserProfile with correct props', () => {
        renderComponent()

        const userProfile = screen.getByTestId('user-profile')

        expect(userProfile).toBeInTheDocument()

        expect(userProfile.textContent).toContain(
            '{"displayNameConfig":{"firstName":"<test>"}',
        )
    })

    it('renders Link with correct href', () => {
        renderComponent()

        const link = screen.getByRole('link')

        expect(link).toHaveAttribute('href', '/base-path/')
    })

    it('renders Tenant Dropdown ', () => {
        renderComponent()
        expect(screen.getByTestId('tenant-dropdown')).toBeInTheDocument()

        const dropdown = screen.getByTestId('tenant-dropdown')
        fireEvent.click(dropdown)
        expect(screen.getByText('Manage')).toBeInTheDocument()
        expect(screen.getByText('Self service')).toBeInTheDocument()
    })
})
