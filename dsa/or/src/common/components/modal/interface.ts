export interface ModalProps {
    isOpen: boolean
    onClose?: () => void
    onAccept?: () => void
    onDecline?: () => void
    declineBtnLabel?: string
    acceptBtnLabel?: string
    title?: string
    body?: any
    hideCloseCrossBtn?: boolean
}
