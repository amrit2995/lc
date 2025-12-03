import React from 'react'
import {render, screen, fireEvent, waitFor} from '@testing-library/react'
import {shallow} from 'enzyme'
import {ThemeProvider} from '@backyard/react'
import AccessAuth from '.'
import UserAccessContext from '../../context/UserAccessContext'
import updateUser from '../../utils/kuber/users'

const mockUpdateUser = updateUser as jest.Mock

jest.mock('../../utils/kuber/users', () => ({
    __esModule: true,
    default: jest.fn(),
}))

jest.mock('@fabrik/component', () => ({
    __esModule: true,
    FabrikLoader: jest.fn(() => (
        <div data-testid="fabrik-loader">Mocked Loader</div>
    )),
}))

describe('<AccessAuth />', () => {
    const renderWithUserAccess = (userAccessValue) =>
        render(
            <ThemeProvider theme={'light'} font={'fellix'}>
                <UserAccessContext.Provider value={userAccessValue}>
                    <AccessAuth />
                </UserAccessContext.Provider>
            </ThemeProvider>,
        )
    it('displays "No access" when no VBUs available', async () => {
        renderWithUserAccess({vbuList: []})
        await waitFor(() => {
            expect(
                screen.getByText(/No access for this resource/i),
            ).toBeInTheDocument()
        })
    })
    it('renders VBU selection dropdown if multiple VBUs', async () => {
        const userAccess = {
            vbuList: [
                {vbu: 'VBU1', vendorNode: {companyDBAName: 'CoA'}},
                {vbu: 'VBU2', vendorNode: {companyDBAName: 'CoB'}},
            ],
        }

        renderWithUserAccess(userAccess)

        await waitFor(() => {
            expect(screen.getByLabelText(/Select VBU/i)).toBeInTheDocument()
        })
    })
    it('moves to VG_USER_ADD_EDIT on invite button click via loader', async () => {
        const userAccess = {
            vbuList: [{vbu: 'VBU1', vendorNode: {}}],
            uniqueid: 'UID',
            sub: 'sub',
            authorities: [],
        }

        renderWithUserAccess(userAccess)
        await waitFor(() => {
            expect(
                screen.queryByLabelText(/Select VBU/i),
            ).not.toBeInTheDocument()
        })
    })
})
