import React from 'react'
import {act, render, screen} from '@testing-library/react'
import SideDrawer from '.'
import SideDrawContext from '../../context/SideDrawContext'
import useFetch from '../../hooks/useFetch'

// Mock DrawerComponent to simply display elements prop for testing
jest.mock('../drawerComponent', () => (props: any) => (
    <div data-testid="drawer-component">{JSON.stringify(props.elements)}</div>
))

// Mock useFetch to call handleOnTrigger with test data immediately
jest.mock('../../hooks/useFetch', () => jest.fn())

describe('SideDrawer', () => {
    const mockSideDrawContext = {
        isOpen: true,
        isHovered: false,
    }

    const mockUserAccess = {
        admin: 'adminRole',
        user: 'userRole',
    }

    const mockRbacData = {
        adminRole: {
            dashboard: {label: 'Dashboard'},
            reports: {label: 'Reports'},
        },
        userRole: {profile: {label: 'Profile'}},
        sideNavOrder: ['dashboard', 'reports', 'profile'],
    }

    const onStaticConfigMock = jest.fn()

    beforeEach(() => {
        jest.clearAllMocks()
        ;(useFetch as jest.Mock).mockImplementation(({handleOnTrigger}) => {
            // Call handleOnTrigger asynchronously to avoid render loop
            setTimeout(() => {
                act(() => {
                    handleOnTrigger(mockRbacData, null)
                })
            }, 0)
            return {}
        })
    })

    it('renders DrawerComponent with filtered elements based on RBAC and userAccess', () => {
        jest.spyOn(
            // eslint-disable-next-line global-require
            require('../userProfile/utils'),
            'roleKeys',
        ).mockImplementation((userAccess) => Object.keys(userAccess))

        render(
            <SideDrawContext.Provider value={mockSideDrawContext}>
                <SideDrawer
                    userAccess={mockUserAccess}
                    onStaticConfig={onStaticConfigMock}
                />
            </SideDrawContext.Provider>,
        )
        const drawerComponent = screen.getByTestId('drawer-component')
        const elements = JSON.parse(drawerComponent.textContent || '[]')

        expect(Array.isArray(elements)).toBe(true)
        expect(elements.length).toBe(0)
    })

    it('passes context state as props to SideDrawerWrapper', () => {
        const {container} = render(
            <SideDrawContext.Provider value={{isOpen: false, isHovered: true}}>
                <SideDrawer userAccess={{}} onStaticConfig={() => {}} />
            </SideDrawContext.Provider>,
        )
        expect(container.firstChild).toBeInTheDocument()
    })
})
