import {Theme} from '@backyard/design-tokens'
import styled from 'styled-components'

export default styled.div`
    height: 100% !important;
    position: fixed;
    top: 64px;
    z-index: 1000;
    left: 0;
    .modal {
        padding-right: 0 !important;
        padding-left: 0 !important;
    }
    .modal-body {
        padding-right: 0 !important;
        padding-top: 0 !important;
    }
    .label {
        font-size: ${Theme.sizes.size_18} !important;
        line-height: ${Theme.sizes.size_36} !important;
    }
    .menu-item-label {
        width: 100% !important;
    }
    .menu-item-flex-start {
        width: 100%;
        display: flex;
        flex-direction: row;
        justify-content: flex-start;
        align-items: center;
        column-gap: 16px;
    }
    .menu-item-flex-center {
        width: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        font-size: 10px;
    }
    .menu-item-space-between {
        width: 100%;
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        align-items: center;
        font-size: 16px !important;
        font-family: Roboto, Helvetica, Arial, sans-serif !important;
    }
`
