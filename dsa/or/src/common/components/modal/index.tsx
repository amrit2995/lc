import {
    Button,
    Modal,
    ModalBody,
    ModalController,
    ModalFooter,
    ModalHeader,
} from '@backyard/react'
import React from 'react'
import {ModalProps} from './interface'

const ModalComponent = (props: ModalProps) => {
    return (
        <React.Fragment>
            <ModalController
                open={props.isOpen}
                onClose={props.onClose}
                modal={
                    <Modal
                        closeProps={
                            props.hideCloseCrossBtn
                                ? {style: {display: 'none'}}
                                : {}
                        }
                    >
                        <ModalHeader>{props.title}</ModalHeader>
                        <ModalBody>{props.body}</ModalBody>
                        {(props.acceptBtnLabel || props.declineBtnLabel) && (
                            <ModalFooter
                                style={{
                                    display: 'flex',
                                    justifyContent: 'end',
                                }}
                            >
                                {props.declineBtnLabel && (
                                    <Button
                                        onClick={props.onDecline}
                                        size="medium"
                                        type="button"
                                        variant="secondary"
                                    >
                                        {props.declineBtnLabel}
                                    </Button>
                                )}
                                {props.acceptBtnLabel && (
                                    <Button
                                        onClick={props.onAccept}
                                        size="medium"
                                        type="button"
                                        variant="primary"
                                    >
                                        {props.acceptBtnLabel}
                                    </Button>
                                )}
                            </ModalFooter>
                        )}
                    </Modal>
                }
            />
        </React.Fragment>
    )
}

export default React.memo(ModalComponent)
