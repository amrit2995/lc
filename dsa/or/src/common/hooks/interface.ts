export interface UseFetchProps {
    url?: string
    handleOnTrigger?: (value: any, error: any) => any
    noCache?: boolean
}

export interface UseClickAwayProps {
    id: string
}

export interface NotificationProps {
    results: any[]
    count: number
}
