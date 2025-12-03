import React, {useContext, useEffect, useState} from 'react'
import {
    Alert,
    Button,
    FileUpload,
    FormControl,
    FormHelperText,
    Search,
    Spinner,
    TextArea,
    TextField,
    Typography,
} from '@backyard/react'
// No icons needed
import {
    RemedyWrapper,
    RemedyTicketContainer,
    RemedyFormWrapper,
    ButtonWrapper,
    RemedyTicketWrapper,
    TicketContainerHeader,
    TicketsWrapper,
    SpinnerWrapper,
    MessageWrapper,
    NoTicketsContainer,
    SearchWrapper,
} from './styles'
import Ticket from './ticket'
import IRemedyTicket from './interface'
import {UserAccess} from '../../initialStates/user'
import UserAccessContext from '../../context/UserAccessContext'
import {
    createRemedyTicket,
    getRemedyTickets,
} from '../../utils/kuber/remedyTicket'

const INITIAL_TICKET_VALUES = {
    subject: '',
    description: '',
    attachments: [] as File[],
}

const validFilesExtensions = ['jpg', 'jpeg', 'png', 'mp4', 'mpeg']

const validator = (values: any) => {
    const errors = {
        subject: '',
        description: '',
    }
    if (!values.subject) {
        errors.subject = 'Please enter Ticket subject'
    }
    if (!values.description) {
        errors.description = 'Please enter detailed description.'
    }
    return {
        isError: !!(errors.subject || errors.description),
        errors,
    }
}

const validateAttachments = (files: Array<File>) => {
    for (let i = 0; i < files.length; i += 1) {
        if (
            !validFilesExtensions.includes(
                files[i].name.split('.').reverse()[0],
            )
        ) {
            return {
                isValid: false,
                message: 'Invalid file type',
            }
        }
        if (files[i].size / (1024 * 1024) > 10) {
            return {
                isValid: false,
                message: 'Each file should be less than 10MB',
            }
        }
    }
    return {
        isValid: true,
        message: '',
    }
}

const RemedyTicketManagement = () => {
    const userAccess: UserAccess = useContext(UserAccessContext)
    const [renderFileUpload, setRenderFileUpload] = useState(0)
    const [apiStatus, setApiStatus] = useState(null)
    const [getRemedyStatus, setGetRemedyStatus] = useState({
        isLoading: false,
        error: null,
    })
    const [tickets, setTickets] = useState<Array<IRemedyTicket>>([])
    const [searchQuery, setSearchQuery] = useState('')
    const [filteredTickets, setFilteredTickets] = useState<
        Array<IRemedyTicket>
    >([])

    // No refresh function needed
    const [newRemedyTicket, setNewRemedyTicket] = useState({
        ...INITIAL_TICKET_VALUES,
    })
    const [errors, setErrors] = useState({
        subject: '',
        description: '',
        attachments: '',
    })

    const onCreateHandler = async () => {
        const {isError, errors: ticketErrors} = validator(newRemedyTicket)
        if (isError) {
            setErrors(ticketErrors)
            return
        }
        const data = new FormData()
        data.append('subject', newRemedyTicket.subject)
        data.append('email', userAccess?.email)
        // Check if user is vendor, with safe handling of undefined values
        const isVendor = userAccess?.user_type
            ? userAccess?.user_type?.toLowerCase() === 'vendor'
            : false
        data.append('isVendor', isVendor.toString())
        data.append(
            'lowVBU',
            isVendor ? userAccess?.activeVbu : userAccess?.userId,
        )
        data.append('description', newRemedyTicket.description)
        if (newRemedyTicket.attachments.length) {
            for (let i = 0; i < newRemedyTicket.attachments.length; i += 1) {
                data.append(
                    `attachments_${i + 1}`,
                    newRemedyTicket.attachments[i],
                )
            }
        }
        // payloadParser(newRemedyTicket, newRemedyTicket.attachments)
        const [error] = await createRemedyTicket(data)
        if (error) {
            setApiStatus({
                type: 'error',
                message: `server couldn't respond this moment. Please try again later`,
            })
        } else {
            setApiStatus({
                type: 'success',
                message: `Successfully created`,
            })
            setNewRemedyTicket({
                subject: '',
                description: '',
                attachments: [] as File[],
            })
            setRenderFileUpload((prev) => prev + 1)
            setTimeout(() => {
                setApiStatus(null)
            }, 5000)
            fetchRemedyTickets()
        }
    }
    const onChangeHandler = (attr: string, e: any, value: any) => {
        if (attr === 'attachments') {
            const {isValid, message} = validateAttachments(e.files)
            if (!isValid) {
                setErrors((prev) => ({...prev, [attr]: message}))
                return
            }
            setErrors((prev) => ({...prev, [attr]: ''}))
            setNewRemedyTicket((prev) => ({
                ...prev,
                [attr]: e.files,
            }))
        } else if (typeof value === 'string') {
            setNewRemedyTicket((prev) => ({...prev, [attr]: value}))
        } else {
            setNewRemedyTicket((prev) => ({...prev, [attr]: value.value}))
        }
        setErrors((prev) => ({...prev, [attr]: ''}))
    }
    const fetchRemedyTickets = async () => {
        // Check if user is vendor, with safe handling of undefined values
        const isVendor = userAccess?.user_type
            ? userAccess?.user_type?.toLowerCase() === 'vendor'
            : false

        const [error, result] = await getRemedyTickets({
            isAdmin: userAccess?.roleName === 'ADMINISTRATOR',
            lowVBU: isVendor ? userAccess?.activeVbu : userAccess?.userId,
        })
        if (!error) {
            setGetRemedyStatus({isLoading: false, error: null})
            setTickets(result.data?.entries.reverse())
        } else {
            setGetRemedyStatus({isLoading: false, error})
            setApiStatus({
                type: 'error',
                message: 'Error in fetching data',
            })
        }
    }
    // Filter tickets function
    const filterTickets = (query: string) => {
        if (!query) {
            setFilteredTickets(tickets)
            return
        }

        const filtered = tickets.filter((ticket: any) => {
            const ticketId = ticket.values['Work Order ID'] || ''
            const description = ticket.values.Description || ''
            const status = ticket.values.Status || ''

            return (
                ticketId.toLowerCase().includes(query.toLowerCase()) ||
                description.toLowerCase().includes(query.toLowerCase()) ||
                status.toLowerCase().includes(query.toLowerCase())
            )
        })

        setFilteredTickets(filtered)
    }

    // Update filtered tickets when tickets change
    useEffect(() => {
        filterTickets(searchQuery)
    }, [tickets])

    useEffect(() => {
        setGetRemedyStatus({isLoading: true, error: null})
        fetchRemedyTickets()
    }, [])

    return (
        <RemedyWrapper>
            {apiStatus ? (
                <MessageWrapper>
                    <Alert type={apiStatus?.type}>{apiStatus?.message}</Alert>
                </MessageWrapper>
            ) : null}
            <Typography variant="h3">Ticket Management</Typography>
            <RemedyTicketContainer>
                <RemedyTicketWrapper>
                    <TicketContainerHeader>
                        <Typography variant="h4">Tickets</Typography>
                    </TicketContainerHeader>
                    <SearchWrapper>
                        <Search
                            placeholder="Search by Ticket Number or Description"
                            value={searchQuery}
                            onChange={(e) => {
                                const target = e.target as HTMLInputElement
                                const newQuery = target.value
                                setSearchQuery(newQuery)
                                filterTickets(newQuery)
                            }}
                            onClearClick={() => {
                                setSearchQuery('')
                                filterTickets('')
                            }}
                        />
                    </SearchWrapper>
                    {getRemedyStatus.isLoading ? (
                        <SpinnerWrapper>
                            <Spinner color="#123c9b" show inline />
                        </SpinnerWrapper>
                    ) : (
                        <TicketsWrapper>
                            {filteredTickets.length > 0 ? (
                                filteredTickets.map((ticket: any) => {
                                    const {values} = ticket
                                    return (
                                        <Ticket
                                            key={values.WorkOrderID}
                                            ticket={values}
                                        />
                                    )
                                })
                            ) : (
                                <NoTicketsContainer>
                                    <Typography variant="body_1">
                                        {searchQuery
                                            ? 'No tickets match your search'
                                            : 'No tickets found'}
                                    </Typography>
                                </NoTicketsContainer>
                            )}
                        </TicketsWrapper>
                    )}
                </RemedyTicketWrapper>
                <RemedyFormWrapper>
                    <Typography variant="h4">Create New Ticket</Typography>
                    <FormControl state={errors?.subject ? 'error' : null}>
                        <TextField
                            label="Subject"
                            maxLength={100}
                            name="subject"
                            onChange={onChangeHandler.bind(this, 'subject')}
                            state={errors?.subject ? 'error' : null}
                            value={newRemedyTicket.subject}
                        />
                        <FormHelperText>
                            {errors?.subject || 'Enter the subject for message'}
                        </FormHelperText>
                    </FormControl>
                    <FormControl state={errors?.description ? 'error' : null}>
                        <TextArea
                            label="Description"
                            state={errors?.description ? 'error' : null}
                            name="description"
                            helperText={
                                errors?.description ||
                                'Enter the detailed description'
                            }
                            value={newRemedyTicket.description}
                            onChange={onChangeHandler.bind(this, 'description')}
                        />
                    </FormControl>
                    <FileUpload
                        key={renderFileUpload % 2 ? 0 : 1}
                        heading="Attachments"
                        maxFiles={3}
                        value={newRemedyTicket.attachments}
                        caption="max 3 files each should be less than 10MB"
                        disabled={newRemedyTicket.attachments.length === 3}
                        name="attachments"
                        onChange={onChangeHandler.bind(this, 'attachments')}
                        multiple
                    />
                    <ButtonWrapper>
                        <Button size="small" onClick={onCreateHandler}>
                            Create
                        </Button>
                    </ButtonWrapper>
                </RemedyFormWrapper>
            </RemedyTicketContainer>
        </RemedyWrapper>
    )
}

export default RemedyTicketManagement
