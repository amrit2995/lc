/* eslint-disable camelcase */
export interface OIDCUserToken {
    access_token: string
    refresh_token: string
    scope: string
    id_token: string
    token_type: string
    useEntForgerock?: boolean | null
    hashToken: string
}

/* eslint-disable camelcase */
export interface UserInfo {
    sub: string
    given_name?: string
    family_name?: string
    vbuList?: string[]
    authorities?: string[]
    email?: string
    user_type?: string
    activeVbu?: string
}

export interface Tenant {
    label: string
    roleGroups: string[]
}

export interface UserSession {
    userId: string
    userDetails: UserDetails
    roleName?: string
    vertexRoleName?: string
    horizonRoleName?: string
    rrdRoleName?: string
    entSocialRoleName?: string
    entEmailRoleName?: string
    tenants?: Tenant[]
    advertisers?: string[]
    refreshToken?: string
    idToken?: string
    accessToken?: string
    isExternalUser?: boolean
    lastUpdatedAt?: number
    vendorMappings?: Record<string, any>
    allowAllAdvertisers?: boolean
    [key: string]: any
}

export interface ExternalMappings {
    source: string
    id: string
}

export interface AdvertiserDetails {
    id: string
    advertiserName: string
    externalMappings: ExternalMappings[]
    vbuIds: string[]
    brands: string[]
}

export interface MFEUserDetails {
    userId: string
    isExternalUser?: boolean
    horizonRoleName: string
    vertexRoleName: string
    roleName: string
    rrdRoleName: string
    entSocialRoleName: string
    entEmailRoleName: string
    tenants: Tenant[]
    userDetails: UserDetails
    advertiserDetails: AdvertiserDetails[]
}

export interface Handler {
    host: string
    path: string
    replacePath: string
    users: string[]
    roleKey: string
    token: string
    userInfoInjectionNeeded: boolean
}

export interface UserDetails {
    email?: string
    name?: string
}
