import {Theme} from '@backyard/design-tokens'
import {Button, IconButton, Tile, Typography} from '@backyard/react'
import Popover from '@backyard/react/Popover'
import React, {useContext, useEffect, useRef, useState} from 'react'
import {useHistory} from 'react-router-dom'
import LogoutContext from '../../context/LogoutContext'
import UserAccessContext from '../../context/UserAccessContext'
import AdvertisersContext from '../../context/AdvertisersContext'
import useClickAway from '../../hooks/useClickAway'
import {UserAccess} from '../../initialStates/user'
import {
    getBasePath,
    replaceUnderScore,
    toProperCase,
} from '../../utils/commonUtils'
import {logout} from '../../utils/kuber/session'
import {LogoutContextProps} from '../baseComponent/interface'
import Modal from '../modal'
import {ModalProps} from '../modal/interface'
import {VendorDetails} from './interface'
import {
    AvatarIcon,
    OverrideStyles,
    PaddingTop16,
    RoleName,
    RoleNameBorder,
    TileWrapper,
    UserInfoTile,
    UserInfoTile2,
} from './styles'
import {getUserInfoValueFromKey, roleKeys, stringAvatar} from './utils'

const UserProfile = (props: {displayNameConfig: any}) => {
    const history = useHistory()

    const userIconRef = useRef()
    const parentRef = useRef()
    const [open, setOpen] = useState(false)
    const [modal, setModal] = useState<ModalProps>()
    const vendorDetails: VendorDetails =
        useContext(AdvertisersContext)?.vendorDetails

    const outClicked = useClickAway(parentRef)
    const userAccess: UserAccess = useContext(UserAccessContext)
    const loggedOut: LogoutContextProps = useContext(LogoutContext)

    const closeModal = () => {
        setModal({isOpen: false})
    }

    useEffect(() => {
        if (outClicked) {
            setOpen(false)
        }
    }, [outClicked])

    const handleOnClick = () => {
        setOpen(!open)
    }

    const handleOnLogoutConfirmation = async () => {
        closeModal()
        loggedOut.onLoggedOut(true)
        const [, res] = await logout()
        const redirectURL = res.redirectUrl
        if (redirectURL?.includes(`${getBasePath()}/logout`)) {
            history.push(`${getBasePath()}/logout`)
        } else {
            window.location.replace(redirectURL)
        }
    }

    const handleLogout = () => {
        setModal({
            isOpen: true,
            acceptBtnLabel: 'Log out',
            declineBtnLabel: 'Close',
            onAccept: handleOnLogoutConfirmation,
            onClose: closeModal,
            onDecline: closeModal,
            title: 'Logout confirmation',
            body: (
                <>
                    <Typography>Are you sure you want to logout?</Typography>
                </>
            ),
        })
    }

    const avatarName = stringAvatar(userAccess?.fullName || 'Unknown User')

    return (
        <div ref={parentRef}>
            <Modal {...modal} />

            <OverrideStyles>
                <IconButton
                    color={Theme.color.marketing_dark_blue}
                    shape="circle"
                    size="small"
                    onClick={handleOnClick}
                    ref={userIconRef}
                    id="user-info"
                >
                    <UserInfoTile>
                        <>{avatarName}</>
                    </UserInfoTile>
                </IconButton>
                <Popover
                    keepMounted
                    open={open}
                    anchorEl={userIconRef.current}
                    placement="bottom-end"
                    pop={
                        <div
                            style={{
                                zIndex: Theme.zIndex.modal,
                            }}
                        >
                            <Tile variant="card">
                                <TileWrapper>
                                    <PaddingTop16>
                                        <UserInfoTile2>
                                            <Typography bold>
                                                <AvatarIcon>
                                                    {avatarName}
                                                </AvatarIcon>
                                            </Typography>
                                        </UserInfoTile2>
                                    </PaddingTop16>
                                    <PaddingTop16>
                                        <Typography variant="body_2">
                                            {userAccess?.fullName ||
                                                'Unknown User'}
                                        </Typography>
                                    </PaddingTop16>
                                    {!!vendorDetails?.brands && (
                                        <PaddingTop16>
                                            <Typography variant="body_2">
                                                <RoleName>
                                                    Brands :{' '}
                                                    {vendorDetails?.brands}
                                                </RoleName>
                                            </Typography>
                                        </PaddingTop16>
                                    )}
                                    {!!vendorDetails?.vbuIds && (
                                        <PaddingTop16>
                                            <Typography variant="body_2">
                                                <RoleName>
                                                    VBUs :{' '}
                                                    {vendorDetails?.vbuIds}
                                                </RoleName>
                                            </Typography>
                                        </PaddingTop16>
                                    )}

                                    {roleKeys(userAccess).map((key: string) => (
                                        <React.Fragment key={key}>
                                            <PaddingTop16>
                                                <Typography variant="body_2">
                                                    <RoleNameBorder>
                                                        <RoleName>
                                                            {toProperCase(
                                                                replaceUnderScore(
                                                                    getUserInfoValueFromKey(
                                                                        userAccess,
                                                                        key,
                                                                        props?.displayNameConfig,
                                                                    ),
                                                                ),
                                                            )}
                                                        </RoleName>
                                                    </RoleNameBorder>
                                                </Typography>
                                            </PaddingTop16>
                                        </React.Fragment>
                                    ))}
                                    {/* <LogoutButton>
                                        <Button
                                            onClick={handleLogout}
                                            fullWidth
                                        >
                                            Logout
                                        </Button>
                                    </LogoutButton> */}
                                    <Button
                                        style={{
                                            marginTop: '10px',
                                            borderRadius: 0,
                                        }}
                                        variant="tertiary"
                                        fullWidth
                                        color="red"
                                        size="small"
                                        onClick={handleLogout}
                                    >
                                        Logout
                                    </Button>
                                </TileWrapper>
                            </Tile>
                        </div>
                    }
                />
            </OverrideStyles>
        </div>
    )
}

UserProfile.propTypes = {}

export default React.memo(UserProfile)
