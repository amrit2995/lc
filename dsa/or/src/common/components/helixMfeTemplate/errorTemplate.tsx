import {Typography} from '@backyard/react'
import React from 'react'
import lormnlogo from '../../../assets/lmn-logo.png'
import {Cover, Icon, LogoContainer, RowWithMargin} from '../logout/styles'

const ErrorTemplate = () => (
    <>
        <Cover>
            <Icon>
                <LogoContainer alt="Oneroof logo" src={lormnlogo} />
            </Icon>
            <RowWithMargin>
                <Typography>
                    Error in loading template, please contact support
                </Typography>
            </RowWithMargin>
        </Cover>
    </>
)

export default React.memo(ErrorTemplate)
