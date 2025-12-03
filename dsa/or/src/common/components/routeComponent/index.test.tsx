import React from 'react'
import {render, screen} from '@testing-library/react'
import {MemoryRouter} from 'react-router-dom'
import RouteComponent from '.'

// eslint-disable-next-line react/no-multi-comp
const Home = (props: any) => (
    <div>
        Home Component
        {props.routes ? ' with nested routes' : ''}
    </div>
)
// eslint-disable-next-line react/no-multi-comp
const About = () => <div>About Component</div>

// eslint-disable-next-line react/no-multi-comp
const Nested = ({routes}: {routes?: any[]}) => (
    <div>
        Nested Component
        {routes && routes.length > 0 ? ' with children' : ''}
    </div>
)

describe('RouteComponent', () => {
    const routes = [
        {
            path: '/',
            exact: true,
            component: Home,
        },
        {
            path: '/about',
            component: About,
        },
        {
            path: '/nested',
            component: Nested,
            routes: [
                {
                    path: '/nested/child',
                    // eslint-disable-next-line react/no-multi-comp
                    component: () => <div>Child Component</div>,
                },
            ],
        },
    ]

    it('renders Home component on root path', () => {
        render(
            <MemoryRouter initialEntries={['/']}>
                <RouteComponent routes={routes} />
            </MemoryRouter>,
        )
        expect(screen.getByText(/Home Component/)).toBeInTheDocument()
    })

    it('renders About component on /about path', () => {
        render(
            <MemoryRouter initialEntries={['/about']}>
                <RouteComponent routes={routes} />
            </MemoryRouter>,
        )
        expect(screen.getByText('About Component')).toBeInTheDocument()
    })

    it('renders Nested component with routes prop on /nested path', () => {
        render(
            <MemoryRouter initialEntries={['/nested']}>
                <RouteComponent routes={routes} />
            </MemoryRouter>,
        )
        expect(screen.getByText(/Nested Component/)).toBeInTheDocument()
        expect(screen.getByText(/with children/)).toBeInTheDocument()
    })

    it('does not render components on unmatched path', () => {
        render(
            <MemoryRouter initialEntries={['/notfound']}>
                <RouteComponent routes={routes} />
            </MemoryRouter>,
        )
        expect(screen.queryByText(/Component/)).not.toBeInTheDocument()
    })
})
