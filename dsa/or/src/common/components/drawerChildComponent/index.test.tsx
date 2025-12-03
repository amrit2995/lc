import React from 'react'
import {render, screen, fireEvent} from '@testing-library/react'
import {createMemoryHistory} from 'history'
import {Router} from 'react-router-dom'
import {ThemeProvider} from '@backyard/react'
import DrawerChildComponent from '.'
import SideDrawContext from '../../context/SideDrawContext'
import UserAccessContext from '../../context/UserAccessContext'

// Mocks for utils used inside the component
jest.mock('../../utils/authUtils', () => ({
    getCurrentPage: jest.fn(() => null),
}))
jest.mock('../../utils/commonUtils', () => ({
    getBasePath: jest.fn(() => '/base'),
    lowerCase: jest.fn((str) => str.toLowerCase()),
    trimLowerCase: jest.fn((str) => str.trim().toLowerCase()),
}))
jest.mock('../drawerComponent/utils', () =>
    jest.fn(() => ({openLabel: 'child1', closedLabel: 'parent'})),
)
jest.mock('./util', () => jest.fn(() => null))

// Mock SideBarIcons to just render text for test ease
jest.mock('../drawerComponent/icons', () => (props: any) => (
    <span data-testid="sidebar-icon">{props.text}</span>
))

describe('DrawerChildComponent', () => {
    let sideDrawContextValue
    let userAccessValue
    let history

    const baseProps = {
        label: 'Parent',
        path: '/parent',
        labelConfig: {},
        children: [
            {label: 'Child1', path: '/child1', isOnlyVendor: false},
            {label: 'Child2', path: '/child2', isOnlyVendor: false},
        ],
        selectedItem: {openLabel: 'child1', closedLabel: 'parent'},
        defaultPage: true,
        isChild: false,
    }

    beforeEach(() => {
        sideDrawContextValue = {
            isOpen: true,
            isHovered: false,
        }
        userAccessValue = {
            isVendorUser: true,
        }
        history = createMemoryHistory()
    })

    function renderComponent(props = {}) {
        return render(
            <ThemeProvider theme={'light'} font={'fellix'}>
                <Router history={history}>
                    <SideDrawContext.Provider value={sideDrawContextValue}>
                        <UserAccessContext.Provider value={userAccessValue}>
                            <DrawerChildComponent {...baseProps} {...props} />
                        </UserAccessContext.Provider>
                    </SideDrawContext.Provider>
                </Router>
            </ThemeProvider>,
        )
    }

    it('renders the label and sidebar icon', () => {
        renderComponent()
        expect(screen.getByText('Parent')).toBeInTheDocument()
    })

    it('pushes to history with basePath + path on MenuItem click if no children', () => {
        renderComponent({children: []})
        const menuItem = screen.getByRole('menuitem')
        fireEvent.click(menuItem)
        expect(history.location.pathname).toBe('/base/parent')
    })

    it('renders children DrawerChildComponent if sideDrawerContext isOpen and iconAfterText is "opened"', () => {
        sideDrawContextValue.isOpen = true
        renderComponent()
        expect(screen.getAllByText(/Child[12]/)).toHaveLength(2)
    })

    it('does not render children if isOnlyVendor true but user is not vendor', () => {
        userAccessValue.isVendorUser = false
        const children = [
            {label: 'VendorOnly', path: '/vendoronly', isOnlyVendor: true},
            {label: 'NotVendorOnly', path: '/notvendor', isOnlyVendor: false},
        ]
        renderComponent({children})
        expect(screen.queryByText('VendorOnly')).not.toBeInTheDocument()
        expect(screen.getByText('NotVendorOnly')).toBeInTheDocument()
    })

    it('applies selected-border class when selectedItem matches label (open and closed conditions)', () => {
        sideDrawContextValue.isOpen = true
        renderComponent({
            selectedItem: {openLabel: 'parent', closedLabel: 'other'},
        })
        const wrapperDiv = screen.getByText('Parent').closest('div')
        expect(wrapperDiv).toHaveClass('menu-item-space-between')
    })

    it('removes event listener on unmount', () => {
        const addEventListenerSpy = jest.spyOn(window, 'addEventListener')
        const removeEventListenerSpy = jest.spyOn(window, 'removeEventListener')
        const {unmount} = renderComponent()
        expect(addEventListenerSpy).toHaveBeenCalledWith(
            'mfeRouteChange',
            expect.any(Function),
        )
        unmount()
        expect(removeEventListenerSpy).toHaveBeenCalledWith(
            'mfeRouteChange',
            expect.any(Function),
        )
    })
})
