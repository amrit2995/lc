import {ElementProps} from '../sideDrawer/interface'

export interface DrawerComponentProps {
    elements?: ElementProps[]
}

export interface SidebarIconsProps {
    text?: string
}

export interface SideDrawerContextType {
    isOpen: boolean
    onChange?: () => void
    onHoverIn?: () => void
    onHoverOut?: () => void
    isHovered?: boolean
}
