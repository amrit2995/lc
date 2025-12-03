// import React from 'react'
// import {shallow} from 'enzyme'
// import DrawerComponent from '.'

// describe('<DrawerComponent />', () => {
//     it('renders <DrawerComponent /> component', () => {
//         const wrapper = shallow(<DrawerComponent />)
//         expect(wrapper.length).toStrictEqual(1)
//     })
// })

import React from 'react'
import {render, screen, fireEvent} from '@testing-library/react'
import {createMemoryHistory} from 'history'
import {Router} from 'react-router-dom'
import {ThemeProvider} from '@backyard/react'
import DrawerComponent from '.'
import SideDrawContext from '../../context/SideDrawContext'
import useFetch from '../../hooks/useFetch'
import southDeepHighlighter from './utils'

// Mock useFetch hook
jest.mock('../../hooks/useFetch')

// Mock southDeepHighlighter util
jest.mock('./utils')

// Mock DrawerChildComponent to simplify testing
jest.mock('../drawerChildComponent', () => (props: any) => {
    return (
        <div data-testid="drawer-child" data-label={props.label}>
            {props.label}
        </div>
    )
})

describe('DrawerComponent', () => {
    let sideDrawContextValue
    let history
    const fetchReturnValue = {'south-deep-highlighter': {someKey: 'someValue'}}

    const elements = [
        {
            label: 'Element1',
            path: '/element1',
            children: [],
            defaultPage: true,
        },
        {
            label: 'Element2',
            path: '/element2',
            children: [],
            defaultPage: false,
        },
    ]

    beforeEach(() => {
        sideDrawContextValue = {
            isOpen: true,
            isHovered: false,
            onHoverIn: jest.fn(),
            onHoverOut: jest.fn(),
        }
        history = createMemoryHistory()
        // useFetch returns a value with the expected shape
        ;(useFetch as jest.Mock).mockReturnValue({value: [fetchReturnValue]})
        // southDeepHighlighter mock returns a fixed highlightObj
        ;(southDeepHighlighter as jest.Mock).mockReturnValue({
            openLabel: 'Element1',
        })
    })

    function renderComponent(props = {}) {
        return render(
            <ThemeProvider theme={'light'} font={'fellix'}>
                <Router history={history}>
                    <SideDrawContext.Provider value={sideDrawContextValue}>
                        <DrawerComponent elements={elements} {...props} />
                    </SideDrawContext.Provider>
                </Router>
            </ThemeProvider>,
        )
    }

    it('renders DrawerChildComponents with correct labels', () => {
        renderComponent()
        elements.forEach((el) => {
            expect(screen.getByText(el.label)).toBeInTheDocument()
        })
    })

    it('calls onHoverIn on mouse over', () => {
        renderComponent()
        const drawer = screen.getByRole('menu')
        fireEvent.mouseOver(drawer)
        expect(sideDrawContextValue.onHoverIn).toHaveBeenCalled()
    })

    it('calls onHoverOut on mouse leave', () => {
        renderComponent()
        const drawer = screen.getByRole('menu')
        fireEvent.mouseLeave(drawer)
        expect(sideDrawContextValue.onHoverOut).toHaveBeenCalled()
    })

    it('sets selectedItem state on history location change', () => {
        renderComponent()
        history.push('/new-path')
        const drawerChilds = screen.getAllByTestId('drawer-child')
        expect(drawerChilds[0]).toHaveAttribute('data-label', 'Element1')
    })
})
