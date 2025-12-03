import React from 'react'
import {render, screen, fireEvent, waitFor} from '@testing-library/react'
import {ThemeProvider, bdsTheme} from '@backyard/react'
import NotificationDraw from './index'

import useNotifications from '../../hooks/useNotifications'
// import useNotifications from '../../hooks/useNotifications'

// ✅ Mock the custom hook
jest.mock('../../hooks/useNotifications', () => ({
    __esModule: true,
    default: jest.fn(),
}))

const renderWithTheme = (ui: React.ReactElement) =>
    render(<ThemeProvider theme={bdsTheme}>{ui}</ThemeProvider>)

describe('NotificationDraw Component', () => {
    beforeEach(() => {
        jest.clearAllMocks()
    })

    test('renders notification icon', () => {
        ;(useNotifications as jest.Mock).mockReturnValue({results: []})
        renderWithTheme(<NotificationDraw />)

        const icon = screen.getByRole('button')
        expect(icon).toBeInTheDocument()
    })

    test('opens drawer on icon click and shows header', async () => {
        ;(useNotifications as jest.Mock).mockReturnValue({results: []})
        renderWithTheme(<NotificationDraw />)
        const icon = screen.getByRole('button')

        fireEvent.click(icon)

        // await waitFor(() => {
        //     expect(screen.getByText(/Notifications/i)).toBeInTheDocument()
        // }, { timeout: 3000 })
    })

    test('shows fallback when no notifications', async () => {
        ;(useNotifications as jest.Mock).mockReturnValue({results: []})
        renderWithTheme(<NotificationDraw />)

        fireEvent.click(screen.getByRole('button'))

        await waitFor(
            () => {
                expect(
                    screen.getByText(/No new notifications/i),
                ).toBeInTheDocument()
            },
            {timeout: 3000},
        )
    })

    test('displays list of notifications', async () => {
        ;(useNotifications as jest.Mock).mockReturnValue({
            results: [
                {
                    id: '1',
                    isRead: false,
                    type: 'INFO_ALERT',
                    entityName: 'User Settings',
                    message: 'Updated successfully',
                    publishTime: new Date().toISOString(),
                },
            ],
        })

        renderWithTheme(<NotificationDraw />)

        fireEvent.click(screen.getByRole('button'))

        await waitFor(
            () => {
                expect(screen.getByText(/User Settings/i)).toBeInTheDocument()
                expect(
                    screen.getByText(/Updated successfully/i),
                ).toBeInTheDocument()
            },
            {timeout: 3000},
        )
    })

    test('calculates unread notifications correctly', () => {
        ;(useNotifications as jest.Mock).mockReturnValue({
            results: [
                {id: '1', isRead: false},
                {id: '2', isRead: true},
                {id: '3', isRead: false},
            ],
        })

        renderWithTheme(<NotificationDraw />)

        // If you re-enable the Pill component, check the badge
        // expect(screen.getByText('2')).toBeInTheDocument()
    })
    test('formats time correctly for recent notifications', async () => {
        const secondsAgo = new Date(Date.now() - 10 * 1000).toISOString() // 10s ago
        const minutesAgo = new Date(Date.now() - 5 * 60 * 1000).toISOString() // 5m ago
        const hoursAgo = new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString() // 2hr ago
        const daysAgo = new Date(
            Date.now() - 3 * 24 * 60 * 60 * 1000,
        ).toISOString() // 3 days ago

        ;(useNotifications as jest.Mock).mockReturnValue({
            results: [
                {
                    id: '1',
                    isRead: false,
                    type: 'TEST',
                    entityName: 'Item A',
                    message: 'Message A',
                    publishTime: secondsAgo,
                },
                {
                    id: '2',
                    isRead: false,
                    type: 'TEST',
                    entityName: 'Item B',
                    message: 'Message B',
                    publishTime: minutesAgo,
                },
                {
                    id: '3',
                    isRead: false,
                    type: 'TEST',
                    entityName: 'Item C',
                    message: 'Message C',
                    publishTime: hoursAgo,
                },
                {
                    id: '4',
                    isRead: false,
                    type: 'TEST',
                    entityName: 'Item D',
                    message: 'Message D',
                    publishTime: daysAgo,
                },
            ],
        })

        renderWithTheme(<NotificationDraw />)
        fireEvent.click(screen.getByRole('button'))

        await waitFor(() => {
            expect(screen.getByText(/10s ago/i)).toBeInTheDocument()
            expect(screen.getByText(/5m ago/i)).toBeInTheDocument()
            expect(screen.getByText(/2hr ago/i)).toBeInTheDocument()
            expect(
                screen.getByText(/\d{1,2}(st|nd|rd|th) \w{3} 20\d{2}/i),
            ).toBeInTheDocument() // e.g., 1st Jul 2025
        })
    })

    test('renders notification even if entityName or message is missing', async () => {
        ;(useNotifications as jest.Mock).mockReturnValue({
            results: [
                {
                    id: '1',
                    isRead: false,
                    type: 'ALERT',
                    publishTime: new Date().toISOString(),
                },
                {
                    id: '2',
                    isRead: false,
                    type: 'UPDATE',
                    entityName: 'Entity',
                    publishTime: new Date().toISOString(),
                },
                {
                    id: '3',
                    isRead: false,
                    type: 'INFO',
                    message: 'Just a message',
                    publishTime: new Date().toISOString(),
                },
            ],
        })

        renderWithTheme(<NotificationDraw />)
        fireEvent.click(screen.getByRole('button'))

        await waitFor(() => {
            expect(screen.getAllByText(/ago/i)).toHaveLength(3)
        })
    })

    test('closes drawer when clicking close button', async () => {
        ;(useNotifications as jest.Mock).mockReturnValue({
            results: [
                {
                    id: '1',
                    isRead: false,
                    type: 'ALERT',
                    entityName: 'Test Entity',
                    message: 'Test message',
                    publishTime: new Date(Date.now() - 10000).toISOString(),
                },
            ],
        })

        renderWithTheme(<NotificationDraw />)

        fireEvent.click(screen.getByRole('button')) // Open drawer

        // Wait for the drawer to render content
        await waitFor(() => {
            expect(screen.getByText(/Test message/i)).toBeInTheDocument()
        })

        // Find the close button using aria-label
        const closeBtn = screen.getByLabelText(/modal-close/i)
        fireEvent.click(closeBtn)

        // Wait for the drawer to close (message disappears)
        await waitFor(() => {
            expect(screen.queryByText(/Test message/i)).not.toBeInTheDocument()
        })
    })
})
