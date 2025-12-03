import styled, {keyframes} from 'styled-components'
import exp from 'node:constants'

const indeterminate = keyframes`
  0% {
    left: -40%;
  }
  50% {
    left: 30%;
    width: 40%;
  }
  100% {
    left: 100%;
    width: 50%;
  }
`

export const ProgressBarContainer = styled.div`
    position: relative;
    width: 100%;
    height: 4px;
    background-color: #e0e0e0;
    overflow: hidden;
    border-radius: 2px;
`

export const ProgressBar = styled.div`
    position: absolute;
    height: 100%;
    width: 60%;
    background-color: #3f51b5;
    animation: ${indeterminate} 1s infinite;
    border-radius: 2px;
`

export const Subheader = styled.div`
    margin-left: 15px;
    margin-top: 10px;
    font-size: 1.25rem;
    font-weight: 600;
`

export const SearchPopper = styled.div<{anchorEl: HTMLElement | null}>`
    position: absolute;
    top: ${({anchorEl}) =>
        anchorEl
            ? anchorEl.getBoundingClientRect().bottom + window.scrollY
            : 0}px;
    left: ${({anchorEl}) =>
        anchorEl
            ? anchorEl.getBoundingClientRect().left + window.scrollX
            : 0}px;
    width: 600px;
    z-index: 9999;
    background-color: white;
    border-radius: 4px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    max-height: 400px;
    overflow-y: auto;
    padding: 8px;
    margin-top: 15px;
`

export const Anchor = styled.span`
    color: ${({theme}) => theme.color.text_interactive};
    font-weight: ${({theme}) => theme.font.weight.medium};
    text-decoration: white;

    &:hover {
        text-decoration: underline !important;
        text-decoration-color: ${({theme}) =>
            `${theme.color.text_interactive}!important`};
    }
`

export const Label = styled.span`
    text-overflow: ellipsis;
    white-space: nowrap;
    overflow: hidden;
    width: 100px;
`

export const Hr = styled.hr`
    border-color: rgba(0, 0, 0, 0.12);
    border-width: 0px 0px thin;
    margin: 0px;
    border-style: 'solid';
`

export const Ul = styled.ul`
    list-style-type: none;
    margin: 0px;
    padding: 5px 0px 0px 15px;
`

export const Li = styled.li`
    padding-bottom: 2px;
`
