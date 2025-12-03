import {Dropdown, IconButton} from '@backyard/react'
import {Menu} from '@backyard/icons'
import styled from 'styled-components'
import {Theme} from '@backyard/design-tokens'
import {FlexItemProps} from './interface'

export const Overwrite = styled.div`
    height: 64px;
    width: 100%;
    position: fixed;
    z-index: 1201;
    top: 0;
    left: 0;
    box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2);
    background-color: #012169;
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;

    .shape--circle {
        border: none !important;
        outline: none !important;
    }

    .size--large {
        height: 32px !important;
        width: 32px !important;
    }

    .icon-overwrite > .btn-label > .icon {
        height: 40px !important;
        width: 40px !important;
    }
`

export const BtnRow = styled.div`
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
`
export const StyledIconButton = styled(IconButton)`
    width: 48px;
    height: 48px;
    margin-right: 16px;
    margin-left: 16px;
    --btn-icon: ${Theme.color.white} !important;
    --btn-hover: rgba(0, 0, 0, 0.04) !important;
    --btn-pressed: rgba(0, 0, 0, 0.04) !important;
`

export const StyledMenuIcon = styled(Menu)`
    width: 50px;
    height: 50px;
    color: ${Theme.color.white};
`
export const FlexItem = styled.div<FlexItemProps>`
    flex-grow: 1;
    align-items: ${({centerAlign}) => (centerAlign ? 'center' : 'initial')};
`

export const DropdownWrapper = styled.div`
    & label {
        color: white !important;
    }
`
