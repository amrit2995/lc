import React, {SetStateAction} from 'react'

export type RoleName =
    | 'ADMINISTRATOR'
    | 'CAMPAIGN_TRAFFICKER'
    | 'CAMPAIGN_MANAGER'
export type VertexRoleName = 'VERTEX_ADMIN' | 'VERTEX_VIEWER'
export type HorizonRoleName = 'HORIZON_USER' | 'HORIZON_ADMIN'
export type RrdRoleName = 'RRD_USER' | 'RRD_ADMIN'
export type EntSocialRoleName = 'SOCIAL_USER' | 'SOCIAL_ADMIN'
export type EntEmailRoleName = 'EMAIL_USER' | 'EMAIL_ADMIN'

export interface SideDrawerProps {
    roleName?: RoleName
    vertexRoleName?: VertexRoleName
    horizonRoleName?: HorizonRoleName
    rrdRoleName?: RrdRoleName
    entSocialRoleName?: EntSocialRoleName
    entEmailRoleName?: EntEmailRoleName
}

export interface ElementProps {
    path?: string
    label: string
    children?: ElementProps[]
    defaultPage?: boolean
    isOnlyVendor?: boolean
}

export interface SideDrawerElementsProps<T> {
    onStaticConfig: (value: any) => void
    userAccess: any
    setIsUserHaveAccess: React.Dispatch<SetStateAction<boolean>>
    staticData: any
    tenantRoleKeys: Array<string>
}
