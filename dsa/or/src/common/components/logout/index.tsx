import {Theme} from '@backyard/design-tokens'
import {CheckCircleFilled} from '@backyard/icons'
import {Typography} from '@backyard/react'
import React from 'react'
import lormnlogo from '../../../assets/lmn-logo.png'
import {Cover, Icon, LogoContainer, RowWithMargin} from './styles'

const Logout = () => (
    <>
        <Cover>
            <Icon>
                <LogoContainer alt="Oneroof logo" src={lormnlogo} />
            </Icon>
            <Icon>
                <CheckCircleFilled color="green" size={Theme.sizes.size_100} />
            </Icon>
            <RowWithMargin>
                <Typography>Successfully logged out!</Typography>
            </RowWithMargin>
        </Cover>
    </>
)

Logout.propTypes = {}

export default React.memo(Logout)
