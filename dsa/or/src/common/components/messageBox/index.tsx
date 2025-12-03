import {Alert} from '@backyard/react'
import React from 'react'
import {MessageBoxProps} from './interface'

const MessageBox = (props: MessageBoxProps) => {
    if (props.isOpen) {
        return <Alert type={props.type}>{props.message}</Alert>
    }
    return null
}

MessageBox.propTypes = {}

export default React.memo(MessageBox)
