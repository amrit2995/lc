import styled from 'styled-components'

const flexColumn = styled.div`
    display: flex;
    flex-direction: column;
`
export const Row = styled.div`
    display: flex;
    gap: 12px;
    align-items: center;
    & > div {
        flex-grow: 1;
    }
`
export const MessageWrapper = styled.div`
    display: 'flex';
    gap: 16px;
`
export const RemedyWrapper = styled(flexColumn)`
    gap: 16px;
    padding-right: 80px;
`

export const RemedyTicketContainer = styled.div`
    display: grid;
    grid-template-columns: 45% auto;
    gap: 22px;
`

export const RemedyTicketWrapper = styled(flexColumn)`
    box-sizing: border-box;
    border: 1px solid var(--bds-color-border-hover-inverse);
    border-radius: 5px;
    gap: 8px;
`

export const RemedyFormWrapper = styled(flexColumn)`
    box-sizing: border-box;
    padding: 24px;
    border: 1px solid var(--bds-color-border-hover-inverse);
    border-radius: 5px;
    gap: 8px;
`
export const SearchWrapper = styled.div`
    display: flex;
    gap: 12px;
    padding: 0 24px;
    & > *:first-child {
        flex-grow: 1;
    }
`

export const ButtonWrapper = styled.div`
    display: flex;
    justify-content: end;
    flex-grow: 1;
    align-items: end;
`

export const TicketContainerHeader = styled.div`
    padding: 24px 0 0 24px;
`

export const TicketsWrapper = styled(flexColumn)`
    height: 634px;
    overflow-y: auto;
    & > div:last-child {
        border: none;
    }
`

export const SpinnerWrapper = styled.div`
    display: flex;
    justify-content: center;
    padding-top: 40px;
`

export const TicketCard = styled.div`
    display: flex;
    padding: 12px 24px;
    gap: 8px;
    border-bottom: 2px solid var(--bds-color-border-hover-inverse);
    align-items: center;
`

export const TicketInfoWrapper = styled(flexColumn)`
    display: flex;
    flex-grow: 1;
    /* gap: 2px; */
`
export const StatusWrapper = styled(flexColumn)`
    gap: 8px;
    align-items: center;
    width: 70px;
`
export const StatusIcon = styled.i<{
    status:
        | 'New'
        | 'Assigned'
        | 'Completed'
        | 'Pending'
        | 'Rejected'
        | 'Closed'
        | 'Cancelled'
        | 'In Progress'
        | 'Planning'
        | 'Waiting Approval'
}>`
    border-radius: 100px;
    height: 40px;
    width: 40px;
    display: flex;
    justify-content: center;
    align-items: center;
    background-color: var(
        ${({status}) => {
            const colors = {
                New: '--bds-color-surface-dark-blue-inverse',
                Assigned: '--bds-color-marketing-interactive',
                Pending: '--bds-color-surface-dark-blue-inverse',
                Completed: '--bds-color-surface-green',
                Rejected: '--bds-color-surface-red',
                Cancelled: '--bds-color-surface-red',
                Closed: '--bds-color-surface-green',
            }
            return colors[status] || '--bds-color-surface-gold'
        }}
    );
`

export const SubText = styled.span`
    font-weight: 400;
`

export const SubjectText = styled.p`
    font-weight: 600;
    margin: 0;
`

export const NoTicketsContainer = styled.div`
    padding: 24px;
    text-align: center;
`
