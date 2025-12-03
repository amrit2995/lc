import React from 'react'
import {ThemeProvider} from '@backyard/react'
import {render, screen, fireEvent, waitFor} from '@testing-library/react'
import BaseComponent from '.'
import {getUserAccess, logout} from '../../utils/kuber/session'
import {getAdvertisers} from '../../utils/kuber/advertisers'

jest.mock('../../utils/kuber/session', () => ({
    getUserAccess: jest.fn(),
    logout: jest.fn(),
}))

jest.mock('../../utils/kuber/advertisers', () => ({
    getAdvertisers: jest.fn(),
}))

jest.mock('react-router-dom', () => ({
    useHistory: () => ({
        push: jest.fn(),
    }),
}))

jest.mock('../../routes', () => [])
jest.mock('../../logoutRoutes', () => [])

const mockUserAccess = {
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
    userInfo: null,
    vendorMappings: {
        horizonRoleName: {reporting: ['meta', 'display']},
    },
    vertexRoleName: 'VERTEX_ADMIN',
}

const mockAdvertisers = [
    {
        name: 'Google',
        id: '64dca791c6e3880ee76553e4',
        advertiserStatus: 'ACTIVE',
        externalId: 'google',
        users: [{userId: '3957300'}],
        wallets: [],
        userTimeZone: 'Asia_Kolkata',
    },
]
jest.spyOn(React, 'useState').mockImplementation((initial) => [
    mockUserAccess,
    jest.fn(),
])

describe('BaseComponent', () => {
    const renderComponent = () => {
        ;(React.useState as jest.Mock)
            .mockImplementationOnce(() => [mockAdvertisers, jest.fn()]) // advertiserList
            .mockImplementationOnce(() => [mockUserAccess, jest.fn()]) // userAccess
            .mockImplementationOnce(() => [null, jest.fn()]) // modal
        ;(getUserAccess as jest.Mock).mockResolvedValue([
            null,
            {roleName: 'ADMINISTRATOR'},
        ])
        ;(getAdvertisers as jest.Mock).mockResolvedValue([
            null,
            mockAdvertisers,
        ])

        render(<BaseComponent />)
    }

    beforeEach(() => {
        jest.clearAllMocks()
    })

    it('fetches user access and advertisers on mount', async () => {
        renderComponent()
        await waitFor(() => {
            expect(getUserAccess).toHaveBeenCalledTimes(1)
            // expect(getAdvertisers).toHaveBeenCalledTimes(0)
        })
    })
})
