import styled from 'styled-components'

const closedCondition = (isHovered: boolean) => (isHovered ? '260' : '65')

export default styled.div`
    height: 100% !important;
    .orientation--vertical {
        max-width: ${(props: any) =>
            props.isOpen
                ? '260'
                : closedCondition(props.isHovered)}px !important;

        position: relative !important;
        border-right: 1px solid rgba(0, 0, 0, 0.12) !important;
        box-shadow: none !important;
        background-color: #f5f5f5 !important;
        padding-bottom: 64px;
    }
`
