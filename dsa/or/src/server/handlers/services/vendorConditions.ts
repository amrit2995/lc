import secrets from '../../secrets'

const {forgerock} = secrets()
const {vendorUrls, enterpriseDetails, vendorDetails} = forgerock

const isVendorUser = (referrer: string) => {
    const referrerUrl = new URL(referrer)
    return vendorUrls.indexOf(referrerUrl.origin) >= 0
    // return true
}

const getForgeRockDetails = (useVendorForgeRock: boolean) => {
    if (useVendorForgeRock) {
        return vendorDetails
    }
    return enterpriseDetails
}

const isVendorUserFromReferer = (request: any) => {
    if (request?.headers?.referer) {
        return isVendorUser(request?.headers?.referer)
    }
    return false
}

export {getForgeRockDetails, isVendorUser, isVendorUserFromReferer}
