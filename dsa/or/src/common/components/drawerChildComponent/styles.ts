import styled from 'styled-components'
import {SelectedWrapperProps} from './interface'

const borderBottom = '1px solid rgba(0, 0, 0, 0.12)'

export const SelectedWrapper = styled.div<SelectedWrapperProps>`
    .selected {
        outline: none !important;
    }

    .selected-border {
        border-left: ${({hideBorders}) =>
            hideBorders ? 'none' : '4px solid #126bd6 !important'};

        background-color: ${({hideBorders}) =>
            hideBorders ? 'transparent !important' : '#e6e9f0 !important'};

        border-bottom: ${({hideBorders, isChild}) =>
            hideBorders || isChild ? 'none' : '1px solid rgba(0, 0, 0, 0.12)'};

        ${({hideBorders}) =>
            hideBorders &&
            `
      .icon-wrapper {
        background-color: #d0e3fb;
        border-radius: 8px;
        padding: 8px 15px 8px 15px;
        display: flex;
        justify-content: center;
        align-items: center;
        transition: background-color 0.2s ease;
      }
    `}
    }

    .unselected-border {
        border-left: ${({isChild}) =>
            isChild ? '4px solid #e6e9f0 !important' : 'none'};
        background-color: transparent !important;
        border-bottom: ${({hideBorders, isChild}) =>
            hideBorders || isChild ? 'none' : '1px solid rgba(0, 0, 0, 0.12)'};
        .icon-wrapper {
            display: flex;
            justify-content: center;
            align-items: center;
        }
    }
`

export const ChildrenItemsWrapper = styled.div`
    .menu-item-space-between {
        font-size: 1rem !important;
        font-weight: 400;
        font-family: Roboto, Helvetica, Arial, sans-serif !important;
    }
    .btn-label {
        margin-left: 24px;
    }
`

export const SideDrawerCollapsed = styled.div``
