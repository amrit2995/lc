import React, {useContext, useEffect, useState} from 'react'
import {useHistory} from 'react-router-dom'
import SideDrawContext from '../../context/SideDrawContext'
import {useNavigation} from '../../context/NavigationContext'
import useFetch from '../../hooks/useFetch'
import {UserAccess} from '../../initialStates/user'
import {getBasePath} from '../../utils/commonUtils'
import DrawerComponent from '../drawerComponent'
import {roleKeys} from '../userProfile/utils'
import {SideDrawerElementsProps} from './interface'
import SideDrawerWrapper from './styles'

const SideDrawer = (props: SideDrawerElementsProps<any>) => {
    const [sideDrawerElements, setSideDrawerElements] = useState([])
    const history = useHistory()
    const sideDrawContext = useContext(SideDrawContext)
    const {autoNavigate} = useNavigation()
    const onRbacFetch = (rbacData: any, rbacError: any) => {
        let accessObj: any = {}
        props.onStaticConfig(rbacData)
        const userAccessKeys =
            (props.tenantRoleKeys?.length && props.tenantRoleKeys) ||
            (props?.userAccess ? roleKeys(props.userAccess) : [])
        userAccessKeys?.forEach((key: string) => {
            const userAccesskey = props?.userAccess[key as keyof UserAccess]
            if (userAccesskey && rbacData) {
                const data = rbacData[userAccesskey as keyof any]
                if (data) {
                    accessObj = {
                        ...accessObj,
                        ...data,
                    }
                }
            }
        })
        const keys: string[] = Object.keys(accessObj)

        const keysOrder = rbacData.sideNavOrder || []

        const keysInOrder = keysOrder?.length
            ? keysOrder.filter((key: string) => keys.includes(key))
            : keys

        if (keysInOrder.length === 0) {
            history.push('/lormn/403')
            props.setIsUserHaveAccess(false)
            return
        }
        if (props.tenantRoleKeys.length && autoNavigate) {
            if (accessObj[keysInOrder[0]].children) {
                const defaultPath =
                    accessObj[keysInOrder[0]].children.find(
                        (sidebarOptions: any) => sidebarOptions.defaultPage,
                    )?.path || ''
                history.push(`/lormn${defaultPath}`)
            } else history.push(`/lormn${accessObj[keysInOrder[0]].path}`)
        }
        setSideDrawerElements(
            keysInOrder.map((key: string) => {
                return accessObj[key]
            }),
        )
    }

    useFetch({
        url: `${getBasePath()}/onering/nucleus?scope=rbac-config`,
        handleOnTrigger: onRbacFetch,
        noCache: true,
    })

    const styleWrapperProps = {
        isOpen: sideDrawContext.isOpen,
        isHovered: sideDrawContext.isHovered,
    }

    useEffect(() => {
        if (props.staticData && props.tenantRoleKeys)
            onRbacFetch(props.staticData, {})
    }, [props.tenantRoleKeys, props.staticData])

    return (
        <SideDrawerWrapper {...styleWrapperProps}>
            <DrawerComponent elements={sideDrawerElements} />
        </SideDrawerWrapper>
    )
}

export default React.memo(SideDrawer)
