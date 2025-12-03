import React from 'react'
import {render, screen, fireEvent, waitFor} from '@testing-library/react'
import RemedyTicketManagement from '.'
import UserAccessContext from '../../context/UserAccessContext'

const mockUserAccess = {
    fullName: 'Test User',
}

describe('RemedyTicketManagement', () => {
    beforeEach(() => {
        render(
            <UserAccessContext.Provider value={mockUserAccess}>
                <RemedyTicketManagement />
            </UserAccessContext.Provider>,
        )
    })

    it('renders the component with initial tickets', () => {
        expect(screen.getByText(/Ticket Management/i)).toBeInTheDocument()
        expect(screen.getByText(/Tickets/i)).toBeInTheDocument()
        expect(screen.getByText(/Create New Ticket/i)).toBeInTheDocument()

        // Check if mock tickets are rendered
        expect(screen.getByText('W000000008636891')).toBeInTheDocument()
        expect(screen.getByText('W000000008636892')).toBeInTheDocument()
        expect(screen.getByText('W000000008636893')).toBeInTheDocument()
    })

    it('shows validation errors when trying to create empty ticket', async () => {
        fireEvent.click(screen.getByRole('button', {name: /Create/i}))

        expect(
            await screen.findByText(/Please select topic/i),
        ).toBeInTheDocument()
        expect(screen.getByText(/Please select category/i)).toBeInTheDocument()
        expect(
            screen.getByText(/Please enter Ticket subject/i),
        ).toBeInTheDocument()
        expect(
            screen.getByText(/Please enter detailed description./i),
        ).toBeInTheDocument()
    })

    it('creates a new ticket when form is invalid', async () => {
        fireEvent.change(screen.getByLabelText(/Topic/i), {
            target: {value: 'Marketing'},
        })

        fireEvent.change(screen.getByLabelText(/Category/i), {
            target: {value: 'Testing'},
        })

        fireEvent.change(screen.getByLabelText(/Subject/i), {
            target: {value: 'New ticket subject'},
        })

        fireEvent.change(screen.getByLabelText(/Description/i), {
            target: {value: 'This is a detailed description'},
        })

        fireEvent.click(screen.getByRole('button', {name: /Create/i}))

        await waitFor(() => {
            expect(screen.getByText('New ticket subject')).toBeInTheDocument()
        })
    })
})
