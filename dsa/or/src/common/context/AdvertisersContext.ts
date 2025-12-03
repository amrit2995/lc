import {createContext} from 'react'
import {AdvertiserContextProps} from '../components/baseComponent/interface'

const AdvertisersContext = createContext<AdvertiserContextProps | undefined>(
    undefined,
)

export default AdvertisersContext
