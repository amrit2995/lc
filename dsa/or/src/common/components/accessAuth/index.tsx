import {Button, Dropdown, Spinner, Typography} from '@backyard/react'
import {FabrikLoader} from '@fabrik/component'
import React, {useContext, useEffect, useRef, useState} from 'react'
import UserAccessContext from '../../context/UserAccessContext'
import {UserAccess} from '../../initialStates/user'
import updateUser from '../../utils/kuber/users'
import MessageBox from '../messageBox'
import {MessageBoxProps} from '../messageBox/interface'
import Modal from '../modal'
import {ModalProps} from '../modal/interface'
import VendorRoleMapForm from '../vendorRoleMapForm'
import {PageTypes} from './interface'
import {
    PageWrapper,
    SpinnerWrapper,
    TitleWrapper,
    VBUSelectWrapper,
} from './styles'
import {getVgUserAddEditUrl, getVgUserListUrl} from './utils'

const AccessAuth = () => {
    const userAccess: UserAccess = useContext(UserAccessContext)

    const [page, setPage] = useState<PageTypes>('LOADING')
    const [message, setMessage] = useState<MessageBoxProps>()
    const [modal, setModal] = useState<ModalProps>()
    const ref = useRef({
        contactId: null,
        accessMap: {},
        vbuContext: '',
    })

    useEffect(() => {
        if (userAccess?.vbuList?.length) {
            if (userAccess.vbuList.length === 1) {
                setPage('VG_USER_LIST')
                const [firstElement] = userAccess.vbuList
                ref.current.vbuContext = firstElement.vbu
            } else {
                setPage('VBU_SELECTION_SCREEN')
            }
        } else {
            setPage('NO_ACCESS')
        }
    }, [userAccess?.vbuList])

    const closeMessageBox = () => {
        setTimeout(() => setMessage({isOpen: false}), 10000)
    }

    const closeModal = () => {
        setModal({isOpen: false})
    }

    const handleEditUserClicked = (contactId: string) => {
        ref.current.contactId = contactId
        setPage('VG_USER_ADD_EDIT')
    }

    const mapContactToRole = async (contactId: string) => {
        const [, response] = await updateUser({
            userId: contactId,
            advertiserIds: userAccess?.advertisers || [],
            vendorMappings: ref.current.accessMap,
        })
        closeModal()
        if (response) {
            setMessage({
                type: 'success',
                message: 'User updated successfully!',
                isOpen: true,
            })
            closeMessageBox()
        } else {
            setMessage({
                type: 'error',
                message: 'Unable to update user, try again later!',
                isOpen: true,
            })
            closeMessageBox()
        }
    }

    const handleOnVendorAccessSelect = (accessMap: any) => {
        ref.current.accessMap = accessMap
    }

    const handleVendorMappingClicked = (contactId: string) => {
        ref.current.contactId = contactId
        setModal({
            isOpen: true,
            acceptBtnLabel: 'Map role',
            declineBtnLabel: 'Close',
            onAccept: () => mapContactToRole(contactId),
            onClose: closeModal,
            onDecline: closeModal,
            title: 'Vendor role mapping',
            body: (
                <>
                    <VendorRoleMapForm
                        contactId={contactId}
                        onListSelect={handleOnVendorAccessSelect}
                        vbuId={ref.current.vbuContext}
                    />
                </>
            ),
        })
    }

    const handleInviteUserClicked = () => {
        ref.current.contactId = null
        setPage('VG_USER_ADD_EDIT')
    }

    const handleOnUserUpdated = (obj: {name: string}) => {
        ref.current.contactId = null
        setMessage({
            type: 'success',
            message: `${obj?.name || 'User'} details has been updated.`,
            isOpen: true,
        })
        closeMessageBox()
        setPage('VG_USER_LIST')
    }

    const handleOnUserInvited = (obj: {name: string}) => {
        ref.current.contactId = null
        setMessage({
            type: 'success',
            message: `${
                obj?.name || 'User'
            } has been sent an invitation to Lowe’s Vendor Gateway.`,
            isOpen: true,
        })
        closeMessageBox()
        setPage('VG_USER_LIST')
    }

    const handleOnCancelCreate = () => {
        ref.current.contactId = null
        setPage('VG_USER_LIST')
    }

    return (
        <>
            <TitleWrapper>
                <Typography variant="h4" regular>
                    Access & Authorization
                </Typography>
            </TitleWrapper>
            <PageWrapper>
                <>
                    <MessageBox {...message} />
                    <Modal {...modal} />
                    {page === 'LOADING' && (
                        <SpinnerWrapper data-testid="spinner">
                            <Spinner show inline />
                        </SpinnerWrapper>
                    )}
                    {page === 'NO_ACCESS' && (
                        <SpinnerWrapper>
                            <Typography>No access for this resource</Typography>
                        </SpinnerWrapper>
                    )}
                    {page === 'VBU_SELECTION_SCREEN' && (
                        <VBUSelectWrapper>
                            <Dropdown
                                label="Select VBU"
                                options={userAccess?.vbuList?.map((item) => ({
                                    label: `${item.vbu} - ${
                                        item?.vendorNode?.companyLegalName ||
                                        item?.vendorNode?.companyDBAName
                                    }`,
                                    value: item.vbu,
                                }))}
                                name="vbu"
                                onChange={(_, value) => {
                                    ref.current.vbuContext = `${value.value}`
                                }}
                            />
                            <Button
                                onClick={() => {
                                    setPage('VG_USER_LIST')
                                }}
                            >
                                Proceed
                            </Button>
                        </VBUSelectWrapper>
                    )}
                    {page === 'VG_USER_LIST' && (
                        <FabrikLoader
                            appName={'vg-user-list'}
                            // loader={ <></> }
                            loader={
                                <SpinnerWrapper>
                                    <Spinner show inline />
                                </SpinnerWrapper>
                            }
                            url={getVgUserListUrl()}
                            compProps={{
                                onInviteUsersClicked: handleInviteUserClicked,
                                onEditUserClicked: handleEditUserClicked,
                                parentApiBaseUrl: '/lormn',
                                isDeleteAllowed: true,
                                vbuContext: ref.current.vbuContext,
                                uniqueid: userAccess.uniqueid,
                                isLmnMapOption: true,
                                onLmnAction: handleVendorMappingClicked,
                            }}
                            scopeModule={'WrapperComponent/WrapperComponent'}
                        />
                    )}
                    {page === 'VG_USER_ADD_EDIT' && (
                        <FabrikLoader
                            appName={'vg-user-add-edit'}
                            loader={
                                <SpinnerWrapper>
                                    <Spinner show inline />
                                </SpinnerWrapper>
                            }
                            url={getVgUserAddEditUrl()}
                            compProps={{
                                onUserUpdated: handleOnUserUpdated,
                                onUserInvited: handleOnUserInvited,
                                handleCancelCreate: handleOnCancelCreate,
                                contactId: ref.current.contactId,
                                isApplicationAccess: true,
                                parentApiBaseUrl: '/lormn',
                                appAccessList: [
                                    'uam.vendor.lormn.title',
                                ],
                                isDeleteAllowed: true,
                                vbuContext: ref.current.vbuContext,
                                uniqueid: userAccess.uniqueid,
                                sub: userAccess.sub,
                                authorities: userAccess.authorities,
                            }}
                            scopeModule={
                                'UserCreationComponent/UserCreationComponent'
                            }
                        />
                    )}
                </>
            </PageWrapper>
        </>
    )
}

export default React.memo(AccessAuth)
