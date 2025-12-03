export interface EntityFragmentProps {
    displayEntityType: string
    entityType: string
    data: any[]
    handleClear: () => void
}

export interface LinkWrapperProps {
    to?: string | null
    label?: string | null
    className?: string | null
    stopPropagation?: boolean
    onClick?: () => void
    noStyle?: boolean
}
