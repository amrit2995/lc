import React from 'react'
import {Typography} from '@backyard/react'
import _ from 'lodash'
import {
    AdaCompliant,
    Checkmark,
    Close,
    FolderOpenFilled,
    ThumbUpFilled,
} from '@backyard/icons'
import moment from 'moment'
import {
    Row,
    SubjectText,
    SubText,
    TicketCard,
    TicketInfoWrapper,
    StatusIcon,
    StatusWrapper,
} from './styles'
import IRemedyTicket from './interface'

const getIcons = (status: string) => {
    switch (status) {
        case 'New':
            return <FolderOpenFilled color="white" />
        case 'Pending':
            return (
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="20px"
                    height="20px"
                    viewBox="0 0 24 24"
                >
                    <path
                        fill="#fff"
                        d="M15 16.69V13h1.5v2.82l2.44 1.41l-.75 1.3zM19.5 3.5L18 2l-1.5 1.5L15 2l-1.5 1.5L12 2l-1.5 1.5L9 2L7.5 3.5L6 2L4.5 3.5L3 2v20l1.5-1.5L6 22l1.5-1.5L9 22l1.58-1.58c.14.19.3.36.47.53A7.001 7.001 0 0 0 21 11.1V2zM11.1 11c-.6.57-1.07 1.25-1.43 2H6v-2zm-2.03 4c-.07.33-.07.66-.07 1s0 .67.07 1H6v-2zM18 9H6V7h12zm2.85 7c0 .64-.12 1.27-.35 1.86c-.26.58-.62 1.14-1.07 1.57c-.43.45-.99.81-1.57 1.07c-.59.23-1.22.35-1.86.35c-2.68 0-4.85-2.17-4.85-4.85c0-1.29.51-2.5 1.42-3.43c.93-.91 2.14-1.42 3.43-1.42c2.67 0 4.85 2.17 4.85 4.85"
                    />
                </svg>
            )
        case 'Assigned':
            return (
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="20px"
                    height="20px"
                    viewBox="0 0 2048 2048"
                >
                    <path
                        fill="#fff"
                        d="m2011 1728l-318 317l-90-90l163-163h-614v-128h614l-163-163l90-90zm-624 192l128 128H256V256h512q0-53 20-99t55-82t81-55t100-20q53 0 99 20t82 55t55 81t20 100h512v1073l-128-128V384h-128v256H512V384H384v1536zM640 384v128h768V384h-256V256q0-27-10-50t-27-40t-41-28t-50-10q-27 0-50 10t-40 27t-28 41t-10 50v128z"
                    />
                </svg>
            )
        case 'Rejected':
            return (
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="20px"
                    height="20px"
                    viewBox="0 0 512 512"
                >
                    <rect
                        width="448"
                        height="80"
                        x="32"
                        y="48"
                        fill="#fff"
                        rx="32"
                        ry="32"
                    />
                    <path
                        fill="#fff"
                        d="M74.45 160a8 8 0 0 0-8 8.83l26.31 252.56a1.5 1.5 0 0 0 0 .22A48 48 0 0 0 140.45 464h231.09a48 48 0 0 0 47.67-42.39v-.21l26.27-252.57a8 8 0 0 0-8-8.83Zm248.86 180.69a16 16 0 1 1-22.63 22.62L256 318.63l-44.69 44.68a16 16 0 0 1-22.63-22.62L233.37 296l-44.69-44.69a16 16 0 0 1 22.63-22.62L256 273.37l44.68-44.68a16 16 0 0 1 22.63 22.62L278.62 296Z"
                    />
                </svg>
            )
        case 'Cancelled':
            return <Close color="white" />
        case 'Completed':
            return <ThumbUpFilled color="white" />
        case 'Closed':
            return <Checkmark color="white" />
        default:
            return <AdaCompliant color="white" />
    }
}

const Ticket: React.FC<{ticket: any}> = ({ticket}) => {
    return (
        <TicketCard>
            <TicketInfoWrapper>
                <Typography variant="h5">
                    Ticket #:<SubText>{ticket['Work Order ID']}</SubText>
                </Typography>
                <SubjectText>{ticket.Description}</SubjectText>
                <Row>
                    <Typography variant="footnote">
                        Create On:{' '}
                        {moment(ticket['Submit Date']).format('Do MMM YYYY')}
                    </Typography>
                    <Typography variant="footnote">
                        Create By:{' '}
                        {ticket['Customer Internet E-mail'] ===
                        'OneRingIntegrationUser@<url>.com'
                            ? ticket?.VendorEmail
                            : `${ticket['First Name']} ${ticket['Last Name']}`}
                    </Typography>
                </Row>
            </TicketInfoWrapper>

            <StatusWrapper>
                <StatusIcon status={ticket.Status}>
                    {getIcons(ticket.Status)}
                </StatusIcon>
                <Typography align="center" variant="h6">
                    {ticket.Status}
                </Typography>
            </StatusWrapper>
        </TicketCard>
    )
}

export default Ticket
