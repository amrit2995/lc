import React from 'react'
import {Link} from 'react-router-dom'
import {Anchor, Label} from './styles'
import {LinkWrapperProps} from './interface'

const LinkWrapper: React.FC<LinkWrapperProps> = ({
    to = null,
    label = null,
    className = null,
    stopPropagation = false,
    onClick = () => {},
    noStyle = false,
}) => {
    return (
        <span className={noStyle ? 'open-new-unstyled-tab' : 'open-new-tab'}>
            <Link
                style={{textDecoration: 'none'}}
                to={to || '#'}
                className={className}
                onClick={(e) => {
                    if (stopPropagation) {
                        e.stopPropagation()
                    }
                    onClick()
                }}
            >
                <span className={noStyle ? undefined : undefined}>
                    <Label>
                        {label && !noStyle && <Anchor>{label}</Anchor>}
                        {label && noStyle && <span>{label}</span>}
                    </Label>
                </span>
            </Link>
        </span>
    )
}

export default LinkWrapper
