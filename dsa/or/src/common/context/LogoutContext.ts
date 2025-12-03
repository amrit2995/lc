import {createContext} from 'react'
import {LogoutContextProps} from '../components/baseComponent/interface'

const LogoutContext = createContext<LogoutContextProps | undefined>(undefined)

export default LogoutContext
