import {ListSelector} from '@backyard/react'
import React, {useEffect, useRef, useState} from 'react'
import {toProperCase} from '../../utils/commonUtils'
import {getAdvertiserByVbuId} from '../../utils/kuber/advertisers'
import {VendorRoleMapFormProps} from './interface'
import VendorRoleMapFormWrapper from './styles'

const VendorRoleMapForm = ({
    contactId,
    vbuId,
    onListSelect,
}: VendorRoleMapFormProps) => {
    const [options, setOptions] = useState([])
    const [currentValue, setCurrentValue] = useState([])
    const [isAdvertiserDataLoad, setIsAdvertiserDataLoad] = useState(false)
    const ref = useRef({
        userVendorMapping: {},
        advertiserVendorMapping: {},
    })

    const handleOnListSelect = (
        _: React.MouseEvent<Element, MouseEvent>,
        value: string[],
    ) => {
        ref.current.userVendorMapping = {
            ...ref.current.userVendorMapping,
            [vbuId]: {reporting: value},
        }
        onListSelect(ref.current.userVendorMapping)
    }

    const getVendorAccessForAdvertiser = async () => {
        const [, vendorMapping] = await getAdvertiserByVbuId(vbuId, contactId)
        setIsAdvertiserDataLoad(true)
        if (vendorMapping) {
            ref.current.advertiserVendorMapping =
                vendorMapping?.advertiserVendorMapping?.reporting
            ref.current.userVendorMapping =
                vendorMapping.userVendorMapping?.reporting
            setOptions(
                vendorMapping?.advertiserVendorMapping?.reporting?.map(
                    (item: string) => ({
                        label: toProperCase(item),
                        value: item,
                    }),
                ),
            )
            const currentUserVendorMappingValue =
                vendorMapping.userVendorMapping?.[vbuId]?.reporting?.filter(
                    (access: string) => {
                        return vendorMapping?.advertiserVendorMapping?.reporting.includes(
                            access,
                        )
                    },
                )
            setCurrentValue(currentUserVendorMappingValue || [])
        }
    }

    useEffect(() => {
        getVendorAccessForAdvertiser()
    }, [])

    return (
        <VendorRoleMapFormWrapper>
            {isAdvertiserDataLoad && options?.length ? (
                <ListSelector
                    multiple
                    enableGlobalKeyDown
                    options={options}
                    value={currentValue || []}
                    onChange={handleOnListSelect}
                />
            ) : (
                <>Please contact Administrator!</>
            )}
        </VendorRoleMapFormWrapper>
    )
}

export default React.memo(VendorRoleMapForm)
