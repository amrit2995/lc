import {createContext, useContext} from 'react'

interface TrackifyContextType {
    TrackEvent: (eventName: string, eventData: any) => void
}
const TrackifyContext = createContext<TrackifyContextType>({
    TrackEvent: () => {},
})

export const useTrackify = () => useContext(TrackifyContext)

export default TrackifyContext
