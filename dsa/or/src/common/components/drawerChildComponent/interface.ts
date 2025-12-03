import React from 'react'
import {ElementProps} from '../sideDrawer/interface'

export interface DrawerChildComponentProps {
    isChild: boolean
    label: string
    path: string
    children?: ElementProps[]
    selectedItem: SelectedItemProps
    onMenuItemSelected?: (item: string) => void
    defaultPage?: boolean
    isOnlyVendor?: boolean
    labelConfig?: Array<{paths: Array<string>; values: SelectedItemProps}>
}

export interface SelectedItemProps {
    openLabel: string
    closedLabel: string
}

export interface RouteChangeEventProps {
    detail: string
}

export interface SelectedWrapperProps {
    isChild: boolean
    hideBorders: boolean
    children: React.ReactNode
}
