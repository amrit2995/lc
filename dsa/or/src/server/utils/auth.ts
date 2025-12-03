import {createHash, randomBytes, randomUUID} from 'crypto'
import {UserInfo, UserSession} from '../handlers/interfaces/sessionProps'
import secrets from '../secrets'
import logger from '../plugins/logger'

const {
    auth: {mutateToken},
} = secrets()

function generateSessionToken(input: string) {
    try {
        const salt = Buffer.from(generateSalt(), 'base64url')
        const hash = createHash('sha256')
        hash.update(salt)
        hash.update(Buffer.from(input))
        const byteData = hash.digest()

        return `${generateRandomString(5)}-${byteData.toString('base64url')}`
    } catch (error) {
        logger.error('Error at generateSessionToken', error)
        return randomUUID()
    }
}

function generateSalt() {
    const salt = randomBytes(16) // Salt length is 16 bytes (128 bits)
    return salt.toString('base64url')
}

function generateRandomString(length: number) {
    // Generates a random string of the given length
    return randomBytes(length).toString('base64url').slice(0, length)
}

const getAuthorizationFromRequest = (request: any) =>
    request?.cookies?.Authorization ?? request?.headers?.authorization

const saveUserToDb = (persistUserOn: string[], authorities: string[]) =>
    persistUserOn.some((item) => authorities.includes(item))

const isUserAdmin = (userSession: UserSession): boolean =>
    Object.keys(userSession).some(
        (key) =>
            /roleName/i.test(key) &&
            userSession[key]?.toUpperCase().includes('ADMIN'),
    )

const mutateUserInfo = (userInfo: UserInfo, request: any): UserInfo => {
    const authorities = getMutatedAuthorities(request)
    const userType = getMutatedUserType(request)

    const updatedUserInfo: UserInfo = {...userInfo}

    if (authorities?.length) {
        updatedUserInfo.authorities = authorities
    }

    if (userType) {
        // eslint-disable-next-line camelcase
        ;(updatedUserInfo as UserInfo).user_type = userType
    }

    return updatedUserInfo
}

const getMutatedUserType = (request: any): string | null => {
    const incomingMutateToken = request.headers?.['x-mutate-token']
    if (incomingMutateToken !== mutateToken) {
        return null
    }

    const userTypeHeader = request.headers?.['x-mutate-user-type']

    if (typeof userTypeHeader === 'string') {
        const trimmed = userTypeHeader.trim().toLowerCase()
        if (trimmed === 'vendor' || trimmed === 'employee') {
            return trimmed
        }
    }

    return null
}

const getMutatedAuthorities = (request: any): string[] | null => {
    const incomingMutateToken = request.headers?.['x-mutate-token']
    if (incomingMutateToken !== mutateToken) {
        return null
    }

    const rawAuthorities = request.headers?.['x-mutate-authorities']
    if (!rawAuthorities) {
        return null
    }

    let authorities: string[] | null = null

    if (typeof rawAuthorities === 'string') {
        authorities = rawAuthorities
            .split(',')
            .map((i) => i.trim())
            .filter(Boolean)
    } else if (Array.isArray(rawAuthorities)) {
        authorities = rawAuthorities
            .flatMap((val) => val.split(',').map((i: string) => i.trim()))
            .filter(Boolean)
    }

    return authorities && authorities.length > 0 ? authorities : null
}

const base64URLEncode = (input: any) =>
    Buffer.from(input)
        .toString('base64')
        .replace(/\+/g, '-')
        .replace(/\//g, '_')
        .replace(/=+$/, '')

const sha256 = (str: string) => createHash('sha256').update(str).digest()

const returnNanoId = (size: number): string =>
    randomBytes(size).toString('base64url').slice(0, size)

export {
    generateSessionToken,
    getAuthorizationFromRequest,
    saveUserToDb,
    isUserAdmin,
    mutateUserInfo,
    base64URLEncode,
    sha256,
    returnNanoId,
}
