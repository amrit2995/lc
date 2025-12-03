import {useEffect, useState} from 'react'
import getNotifications from '../utils/kuber/notifications'
import {NotificationProps} from './interface'

const notificationInterval = 300000
let notificationTimer: any = null
let notificationErr: boolean = false
const useNotifications = () => {
    const [notifications, setNotifications] = useState<NotificationProps>(null)

    const triggerOnIntervals = (cb: () => void) => {
        notificationTimer = setInterval(cb, notificationInterval)
    }

    const startNotifications = async () => {
        if (!notificationErr) {
            const [err, notificationResultAndCount] = await getNotifications()
            if (err) {
                notificationErr = true
                pauseNotification()
            }
            if (notificationResultAndCount?.results) {
                setNotifications(notificationResultAndCount)
                triggerOnIntervals(startNotifications)
            }
        }
    }

    const pauseNotification = () => {
        clearInterval(notificationTimer)
        notificationTimer = null
    }

    const handleOnPageVisibilityChange = (visibilityEvent: any) => {
        if (document.hidden) {
            pauseNotification()
        } else {
            startNotifications()
        }
    }

    useEffect(() => {
        startNotifications()
        document.addEventListener(
            'visibilitychange',
            handleOnPageVisibilityChange,
        )
    }, [])

    return notifications
}

export default useNotifications
