import {findAll, findAllIn, findAllInObjectId} from '../../mongo/client'
import {Tenant} from '../interfaces/sessionProps'

const findAdvertisersByVbuIds = async (
    vbuIds: Array<string>,
): Promise<any[]> => {
    if (vbuIds?.length) {
        const advertisers = await findAllIn('advertiser', 'vbuIds', vbuIds)
        if (advertisers?.length) {
            return advertisers
        }
        return []
    }
    return []
}

const findAllAdvertisers = async (): Promise<string[]> => {
    const advertisers = await findAll('advertiser')
    if (advertisers?.length) {
        /* eslint-disable no-underscore-dangle */
        return advertisers.map((i) => i._id.toString())
    }
    return []
}

const findAdvertisersByVbuIdsAndReturnObjectIds = async (
    vbuIds: Array<string>,
): Promise<string[]> => {
    const advertisers = await findAdvertisersByVbuIds(vbuIds)
    if (advertisers?.length) {
        /* eslint-disable no-underscore-dangle */
        return advertisers.map((i) => i._id.toString())
    }
    return []
}

const generateVendorMappingsForAdvertiserIds = async (
    advertiserIds: Array<string>,
): Promise<any> => {
    const vendorMappings: Record<string, any> = Object.create(null)
    const advertisers = await findAllInObjectId(
        'advertiser',
        '_id',
        advertiserIds,
    )

    advertisers.forEach((advertiser: any) => {
        advertiser?.vbuIds?.forEach((vbu: string) => {
            if (!vendorMappings[vbu]) {
                vendorMappings[vbu] = {}
            }

            const mappings = advertiser.vendorMappings || {}
            Object.entries(mappings).forEach(([entity, value]) => {
                vendorMappings[vbu][entity] = value
            })
        })
    })
    return vendorMappings
}

const mapRoleNamesToRoles = (
    mapping: Record<string, Record<string, string>> & {roleKeys: string[]},
    authorities: string[],
) => {
    // const mappedAuthorities = new Set<string>()
    const roleKeysAndValues: Record<string, string> = {}

    mapping.roleKeys.forEach((key) => {
        const roleMap = mapping[key]
        if (!roleMap) return

        authorities.forEach((authority) => {
            const role = roleMap[authority]
            if (!role) return

            // mappedAuthorities.add(role)
            const existingRole = roleKeysAndValues[key]
            if (!existingRole || !existingRole.includes('ADMIN')) {
                roleKeysAndValues[key] = role
            }
        })
    })

    return roleKeysAndValues
}

const buildTenantInfo = (
    nucleusMapping: any,
    userRoles: Record<string, string>,
    isExternalUser: boolean,
): Tenant[] => {
    const tenants = nucleusMapping?.tenants || []
    const userTenants: Tenant[] = []

    // Process each tenant from the config
    tenants.forEach((tenant: any) => {
        const {label, roleGroups = []} = tenant
        // External users can only see LMN tenant, internal users cannot see LMN tenant
        const isLmnTenant = label === 'LMN'

        // Skip if: (external user and not LMN) OR (internal user and is LMN)
        if (isExternalUser ? !isLmnTenant : isLmnTenant) {
            return
        }

        const tenantRoles: string[] = []

        // Check if the user has any roles for this tenant
        roleGroups.forEach((roleGroup: string) => {
            const roleValue = userRoles[roleGroup]
            if (roleValue) {
                // Push the role key (roleGroup) instead of the role value
                tenantRoles.push(roleGroup)
            }
        })

        // If the user has roles for this tenant, add it to the user's tenants
        if (tenantRoles.length > 0) {
            userTenants.push({
                label,
                roleGroups: tenantRoles,
            })
        }
    })

    return userTenants
}

const buildUserRoles = (
    nucleusMapping: any,
    authorities: string[],
    isExternalUser: boolean,
) => {
    const internalRoles = mapRoleNamesToRoles(nucleusMapping, authorities)
    const vendorRoles = mapRoleNamesToRoles(
        nucleusMapping?.vendorRoleGroupMapping ?? {},
        authorities,
    )

    const combinedRoles = {
        ...internalRoles,
        ...vendorRoles,
    }

    // Build tenant information based on the user's roles
    const tenants = buildTenantInfo(
        nucleusMapping,
        combinedRoles,
        isExternalUser,
    )

    return {
        ...combinedRoles,
        tenants,
    }
}

const mapUserAdvertiserVendorAccess = (
    userSession: any,
    advertiser: any,
): any => {
    const vendorMappings = userSession?.vendorMappings || {}

    const accessMap: Record<string, Set<string>> = {}

    advertiser.vbuIds?.forEach((vbu: string) => {
        const vbuMapping = vendorMappings[vbu]
        if (!vbuMapping) return

        Object.entries(vbuMapping).forEach(([key, values]) => {
            if (!Array.isArray(values)) return
            const accessKey = `${key}ChannelAccess`

            if (!accessMap[accessKey]) {
                accessMap[accessKey] = new Set()
            }

            values.forEach((val: string) => accessMap[accessKey].add(val))
        })
    })

    const accessObject: Record<string, string[]> = {}
    Object.entries(accessMap).forEach(([key, valueSet]) => {
        accessObject[key] = Array.from(valueSet)
    })

    return accessObject
}

export {
    buildUserRoles,
    findAdvertisersByVbuIds,
    findAdvertisersByVbuIdsAndReturnObjectIds,
    generateVendorMappingsForAdvertiserIds,
    mapUserAdvertiserVendorAccess,
    findAllAdvertisers,
    mapRoleNamesToRoles,
}
