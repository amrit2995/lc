import React from 'react'
import TrackifyContext from '../../context/TrackifyContext'

const TrackifyContainer = (props) => {
    const track = (name: string, data: any) => {
        if (window?.Trackify) {
            window.Trackify.events?.trackEvent(name, data)
        }
    }
    const triggerTrackifyHandler = (event: {
        detail: {
            eventName: string
            eventData: any
        }
    }) => {
        try {
            track(event.detail.eventName, event.detail.eventData)
        } catch (error) {
            console.log(error)
        }
    }
    React.useEffect(() => {
        window.addEventListener('trackify', triggerTrackifyHandler)
        return () => {
            window.removeEventListener('trackify', triggerTrackifyHandler)
        }
    }, [])
    return (
        <TrackifyContext.Provider value={{TrackEvent: track}}>
            {props.children}
        </TrackifyContext.Provider>
    )
}

export default TrackifyContainer
