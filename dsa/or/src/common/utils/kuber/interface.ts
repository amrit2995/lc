/* eslint-disable camelcase */
export interface InitSessionProps {
    client_id: string
    redirect_uri: string
    grant_type: string
    code_verifier: string
    state: string
    code: string
}

export interface ReportingVendorMappingProps {
    reporting: string[]
}

export interface HorizonRoleNameMappingProps {
    horizonRoleName: ReportingVendorMappingProps
}

export interface UpdateUserProps {
    userId: string
    advertiserIds: string[]
    vendorMappings: any
}
