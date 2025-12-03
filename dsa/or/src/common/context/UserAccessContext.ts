import {createContext} from 'react'
import {UserAccess} from '../initialStates/user'

const UserAccessContext = createContext<UserAccess | undefined>(undefined)

export default UserAccessContext
