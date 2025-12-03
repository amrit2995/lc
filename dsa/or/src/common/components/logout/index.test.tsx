import React from 'react'
import {render, screen} from '@testing-library/react'
import {ThemeProvider, bdsTheme} from '@backyard/react'
import Logout from './index'

describe('Logout Component', () => {
    test('renders text', () => {
        render(
            <ThemeProvider theme={bdsTheme}>
                <Logout />
            </ThemeProvider>,
        )
        const element = screen.getByText(/Successfully logged out!/i) // adjust based on your component text
        expect(element).toBeInTheDocument()
    })
})

jest.mock('@backyard/icons', () => ({
    CheckCircleFilled: () => <div data-testid="check-circle-icon" />,
}))

jest.mock('../../../assets/lmn-logo.png', () => 'logo-mock.png')

const renderWithTheme = (ui: React.ReactElement) =>
    render(<ThemeProvider theme={bdsTheme}>{ui}</ThemeProvider>)

describe('Logout Component2', () => {
    test('renders the logo image', () => {
        renderWithTheme(<Logout />)
        const logo = screen.getByAltText(/Oneroof logo/i)
        expect(logo).toBeInTheDocument()
        expect(logo).toHaveAttribute('src', 'logo-mock.png')
    })

    test('renders the success icon', () => {
        renderWithTheme(<Logout />)
        const icon = screen.getByTestId('check-circle-icon')
        expect(icon).toBeInTheDocument()
    })

    test('displays the logout success message', () => {
        renderWithTheme(<Logout />)
        const message = screen.getByText(/Successfully logged out!/i)
        expect(message).toBeInTheDocument()
    })
})
