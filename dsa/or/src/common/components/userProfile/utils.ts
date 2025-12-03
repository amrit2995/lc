import {UserAccess} from '../../initialStates/user'
import {lowerCase} from '../../utils/commonUtils'

const stringAvatar = (name: string) =>
    `${name.split(' ')[0][0].toUpperCase()}${name
        .split(' ')[1][0]
        .toUpperCase()}`

/**
 *
 * @param userInfo
 * @returns Array of keys that contain rolename
 */
const roleKeys = (userInfo: UserAccess) => {
    const keys = Object.keys(userInfo).filter((key) =>
        lowerCase(key).includes('rolename'),
    )
    return keys
}

const getUserInfoValueFromKey = (
    userAccess: UserAccess,
    key: string,
    displayNameConfig: any,
) => {
    if (userAccess && key) {
        const userAccessValue = userAccess[key as keyof typeof userAccess]
        if (userAccessValue) {
            const alternateName =
                displayNameConfig?.[userAccessValue as keyof any]
            if (alternateName) {
                return alternateName?.toString()
            }
            return userAccessValue.toString()
        }
        return ''
    }
    return ''
}

export {getUserInfoValueFromKey, roleKeys, stringAvatar}
