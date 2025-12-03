import {
    EntEmailRoleName,
    EntSocialRoleName,
    HorizonRoleName,
    RoleName,
    RrdRoleName,
    VertexRoleName,
} from '../components/sideDrawer/interface'
import {HorizonRoleNameMappingProps} from '../utils/kuber/interface'

export const user: User = {
    userAccess: null,
    users: [],
}

/* eslint-disable camelcase */
export interface Tenant {
    label: string
    roleGroups: string[]
}

export interface UserAccess {
    accessToken: string
    advertisers: string[]
    defaultAdvertiser: string
    horizonRoleName: HorizonRoleName
    roleName: RoleName
    rrdRoleName: RrdRoleName
    userId: string
    vertexRoleName: VertexRoleName
    entSocialRoleName?: EntSocialRoleName
    entEmailRoleName?: EntEmailRoleName
    tenants?: Tenant[]
    fullName: string
    email: string
    given_name?: string
    family_name?: string
    isVendorUser?: boolean
    isVendorAdmin?: boolean
    vbuList?: any[]
    uniqueid?: string
    authorities?: any[]
    sub?: string
    vendorMappings: HorizonRoleNameMappingProps
    user_type: string
    tenants?: Array<{label: string; roleGroups: Array<string>}>
    activeVbu: string
}

export interface User {
    userAccess: UserAccess
    users: any[]
}
