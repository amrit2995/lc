import styled from 'styled-components'

export const IconMargin = styled.div`
    margin: 0px 20px 0px 20px;
`

export const Grid = styled.div`
    display: grid;
    grid-template-columns: 0.1fr 1fr;
`

export const EntityStyle = styled.span`
    font-weight: bold;
    margin-right: 8px;
`

export const NotificationLine = styled.div`
    button {
        border: none;
        border-bottom: 1px solid rgba(0, 0, 0, 0.12);
        min-height: 60px;
        padding: 16px 0px;
        width: 100%;
        background: #fff;
        cursor: pointer;
        display: flex;
        flex-direction: row;
        align-items: flex-start;

        &:hover {
            background: #f5f5f5;
        }
    }
`

export const ReadUnreadIcon = styled.div`
    padding: 4px;
`

export const InfoAndTime = styled.div`
    display: flex;
    flex-direction: column;
    align-items: flex-start;
`
