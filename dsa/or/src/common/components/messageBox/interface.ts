export interface MessageBoxProps {
    type?: 'info' | 'error' | 'success' | 'warning'
    message?: string
    isOpen: boolean
}
