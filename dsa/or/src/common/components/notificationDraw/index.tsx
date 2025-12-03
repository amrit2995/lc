import {Bullet, ReminderOutlined} from '@backyard/icons'
import {
    ClickAwayListener,
    Drawer,
    DrawerBody,
    DrawerController,
    DrawerHeader,
    IconButton,
    Typography,
} from '@backyard/react'
import React, {useState} from 'react'

import {Theme} from '@backyard/design-tokens'
import moment from 'moment'

import useNotifications from '../../hooks/useNotifications'
import {
    displayTbcAfterCharLimit,
    replaceUnderScore,
    toProperCase,
} from '../../utils/commonUtils'
import {
    EntityStyle,
    Grid,
    InfoAndTime,
    NotificationLine,
    ReadUnreadIcon,
} from './styles'

const timeFormat = (time: any) => {
    const currentTime = moment()
    const publishTime = moment(time)
    const diffInSecs = currentTime.diff(publishTime, 'seconds')
    if (diffInSecs < 60) {
        return `${diffInSecs}s ago`
    }
    const diffInMins = currentTime.diff(publishTime, 'minutes')
    if (diffInMins < 60) {
        return `${diffInMins}m ago`
    }
    const diffInHors = currentTime.diff(publishTime, 'hours')
    if (diffInHors < 24) {
        return `${diffInHors}hr ago`
    }
    return publishTime.format('Do MMM YYYY')
}

const NotificationDraw = () => {
    const [open, setOpen] = useState<boolean>(false)
    const notifications = useNotifications()

    const notificationCount = () => {
        if (notifications?.results?.length) {
            return notifications?.results?.filter(
                (notification) => !notification.isRead,
            ).length
        }
        return 0
    }

    return (
        <>
            <div>
                {/* <IconMargin>
                    <Pill
                        color="red"
                        max={9}
                        value={notificationCount()}
                        shape="circle"
                        wrapperProps={{
                            style: {
                                cursor: 'pointer',
                            },
                        }}
                    >
                        <ReminderOutlined
                            size={Theme.sizes.size_48}
                            color={Theme.color.white}
                            onClick={() => setOpen(true)}
                        />
                    </Pill>
                </IconMargin> */}

                <IconButton
                    className="icon-overwrite"
                    color={Theme.color.marketing_dark_blue}
                    shape="circle"
                    // size="small"
                    onClick={() => setOpen(true)}
                >
                    <ReminderOutlined
                        // size={'40'}
                        color={Theme.color.white}
                    />
                </IconButton>
                <DrawerController
                    anchor="right"
                    hideOverlay
                    disablePortal
                    drawerStyle={{
                        zIndex: Theme.zIndex.drawer + 5,
                        overflowY: 'scroll',
                    }}
                    // wrap={{}}
                    open={open}
                    onClose={() => setOpen(false)}
                    onOpen={() => setOpen(true)}
                    drawer={
                        <Drawer shape="squared">
                            <ClickAwayListener
                                onClickAway={() => setOpen(false)}
                            >
                                <div>
                                    <DrawerHeader>Notifications</DrawerHeader>
                                    <DrawerBody>
                                        {notifications?.results?.length ? (
                                            <div>
                                                {notifications?.results?.map(
                                                    (notification) => (
                                                        <React.Fragment
                                                            key={
                                                                notification.id
                                                            }
                                                        >
                                                            <NotificationLine>
                                                                <button
                                                                    onClick={() => {}}
                                                                >
                                                                    <Grid>
                                                                        <ReadUnreadIcon>
                                                                            <Bullet
                                                                                color={
                                                                                    notification.isRead
                                                                                        ? Theme
                                                                                              .color
                                                                                              .neutral_02
                                                                                        : Theme
                                                                                              .color
                                                                                              .marketing_blue
                                                                                }
                                                                            />
                                                                        </ReadUnreadIcon>
                                                                        <InfoAndTime>
                                                                            <Typography>
                                                                                <EntityStyle>
                                                                                    {replaceUnderScore(
                                                                                        toProperCase(
                                                                                            notification.type ||
                                                                                                '',
                                                                                        ),
                                                                                    )}
                                                                                </EntityStyle>
                                                                                <span>
                                                                                    {notification.entityName
                                                                                        ? displayTbcAfterCharLimit(
                                                                                              notification.entityName,
                                                                                              30,
                                                                                          )
                                                                                        : ''}{' '}
                                                                                    {notification.message
                                                                                        ? displayTbcAfterCharLimit(
                                                                                              notification.message,
                                                                                              90,
                                                                                          )
                                                                                        : ''}
                                                                                </span>
                                                                            </Typography>
                                                                            <div>
                                                                                {notification?.publishTime && (
                                                                                    <Typography variant="footnote">
                                                                                        {timeFormat(
                                                                                            notification.publishTime,
                                                                                        )}
                                                                                    </Typography>
                                                                                )}
                                                                            </div>
                                                                        </InfoAndTime>
                                                                    </Grid>
                                                                    <div />
                                                                </button>
                                                            </NotificationLine>
                                                        </React.Fragment>
                                                    ),
                                                )}
                                            </div>
                                        ) : (
                                            <div>No new notifications</div>
                                        )}
                                    </DrawerBody>
                                </div>
                            </ClickAwayListener>
                        </Drawer>
                    }
                />
            </div>
        </>
    )
}

export default NotificationDraw
