import React from 'react'
import {render, screen} from '@testing-library/react'
import {ThemeProvider, bdsTheme} from '@backyard/react'
import MessageBox from './index'

// Helper to wrap with theme
const renderWithTheme = (ui: React.ReactElement) =>
    render(<ThemeProvider theme={bdsTheme}>{ui}</ThemeProvider>)

describe('MessageBox Component', () => {
    test('renders Alert when isOpen is true', () => {
        renderWithTheme(
            <MessageBox isOpen type="info" message="Info message" />,
        )
        expect(screen.getByText(/Info message/i)).toBeInTheDocument()
    })

    test('does not render anything when isOpen is false', () => {
        const {container} = renderWithTheme(
            <MessageBox isOpen={false} type="info" message="Hidden message" />,
        )
        expect(container.firstChild).toBeNull()
    })

    test('renders the correct message and assumes correct type is applied', () => {
        renderWithTheme(
            <MessageBox isOpen type="success" message="Success Message" />,
        )
        const alert = screen.getByText(/Success Message/i)
        expect(alert).toBeInTheDocument()
    })
})
