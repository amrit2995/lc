import React from 'react'
import {render, screen, fireEvent} from '@testing-library/react'
import {ThemeProvider, bdsTheme} from '@backyard/react'
import ModalComponent from './index'

const renderWithTheme = (ui: React.ReactElement) =>
    render(<ThemeProvider theme={bdsTheme}>{ui}</ThemeProvider>)

describe('ModalComponent', () => {
    const defaultProps = {
        isOpen: true,
        onClose: jest.fn(),
        onAccept: jest.fn(),
        onDecline: jest.fn(),
        title: 'Test Modal Title',
        body: 'Test modal body content',
        acceptBtnLabel: 'Accept',
        declineBtnLabel: 'Decline',
    }

    beforeEach(() => {
        jest.clearAllMocks()
    })

    test('renders modal title and body when open', () => {
        renderWithTheme(<ModalComponent {...defaultProps} />)
        expect(screen.getByText(/Test Modal Title/i)).toBeInTheDocument()
        expect(screen.getByText(/Test modal body content/i)).toBeInTheDocument()
    })

    test('renders accept and decline buttons when labels are provided', () => {
        renderWithTheme(<ModalComponent {...defaultProps} />)
        expect(screen.getByText(/Accept/i)).toBeInTheDocument()
        expect(screen.getByText(/Decline/i)).toBeInTheDocument()
    })

    test('calls onAccept when accept button is clicked', () => {
        renderWithTheme(<ModalComponent {...defaultProps} />)
        fireEvent.click(screen.getByText(/Accept/i))
        expect(defaultProps.onAccept).toHaveBeenCalled()
    })

    test('calls onDecline when decline button is clicked', () => {
        renderWithTheme(<ModalComponent {...defaultProps} />)
        fireEvent.click(screen.getByText(/Decline/i))
        expect(defaultProps.onDecline).toHaveBeenCalled()
    })

    test('does not render buttons if labels are not provided', () => {
        const props = {
            ...defaultProps,
            acceptBtnLabel: '',
            declineBtnLabel: '',
        }
        renderWithTheme(<ModalComponent {...props} />)
        // expect(screen.queryByRole('button')).not.toBeInTheDocument()
        expect(
            screen.queryByRole('button', {name: /Accept/i}),
        ).not.toBeInTheDocument()
        expect(
            screen.queryByRole('button', {name: /Decline/i}),
        ).not.toBeInTheDocument()
    })

    test('renders modal with close button hidden when hideCloseCrossBtn is true', () => {
        const props = {
            ...defaultProps,
            hideCloseCrossBtn: true,
        }
        const {container} = renderWithTheme(<ModalComponent {...props} />)

        // As Backyard hides the close icon via inline style, we can test it this way
        const closeButtons = container.querySelectorAll('[aria-label="Close"]')
        closeButtons.forEach((btn) => {
            expect((btn as HTMLElement).style.display).toBe('none')
        })
    })
})
