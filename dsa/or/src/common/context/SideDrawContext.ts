import {createContext} from 'react'
import {SideDrawerContextType} from '../components/drawerComponent/interface'

const SideDrawContext = createContext<SideDrawerContextType | undefined>(
    undefined,
)

export default SideDrawContext
