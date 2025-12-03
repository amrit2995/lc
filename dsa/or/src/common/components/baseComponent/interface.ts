export interface AdvertiserContextProps {
    advertiserList: any[]
    vendorDetails: VendorDetails
}

export interface LogoutContextProps {
    isLoggedOut: boolean
    onLoggedOut: (value: boolean) => void
}
export interface VendorDetails {
    brands: string
    vbuIds: string
}

export interface IntegrationConfig {
    trackify?: {
        sourceId?: string
        sourceName?: string
        env?: string
        src?: string
    }
    ecko?: {
        key?: string
        value?: string
        src?: string
    }
}
