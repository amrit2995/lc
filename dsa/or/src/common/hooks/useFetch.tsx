import {useEffect, useState} from 'react'
import {UseFetchProps} from './interface'
import {makeGetCall} from './useFetchUtils'

const useFetch = ({url, handleOnTrigger, noCache}: UseFetchProps) => {
    const [value, setValue]: any[] = useState('')
    const [error, setError]: any[] = useState('')

    useEffect(() => {
        triggerFetch()
    }, [url])

    const addToSession = (key: string, sessionValue: string) => {
        sessionStorage.setItem(key, JSON.stringify(sessionValue))
    }
    const getFromSession = (key: string) => {
        return sessionStorage.getItem(key)
    }

    const handleTrigger = async (triggerUrl: string) => {
        const [errResponse, response] = await makeGetCall(triggerUrl)
        if (response) {
            if (!noCache) {
                addToSession(url, response)
            }
            setValue(response)
            setError(null)
        }
        if (error) {
            setError(errResponse)
            setValue(null)
        }
        if (handleOnTrigger && typeof handleOnTrigger === 'function') {
            handleOnTrigger(response, error)
        }
    }

    const triggerFetch = () => {
        if (url) {
            const existingValue = noCache ? null : getFromSession(url)
            if (existingValue) {
                const parsedValue = JSON.parse(existingValue)
                setValue(parsedValue)
                setError(null)
                if (handleOnTrigger && typeof handleOnTrigger === 'function') {
                    handleOnTrigger(parsedValue, null)
                }
            } else {
                handleTrigger(url)
            }
        }
    }

    return {value, error}
}

export default useFetch
