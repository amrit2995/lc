import React, {useEffect, useState} from 'react'

const useClickAway = (ref: React.MutableRefObject<any>) => {
    const [outClicked, setOutClicked] = useState<boolean>(false)
    useEffect(() => {
        const handleClickEvents = (event: MouseEvent) => {
            if (ref?.current && !ref?.current.contains(event.target)) {
                setOutClicked(true)
            } else {
                setOutClicked(false)
            }
        }
        document.addEventListener('click', handleClickEvents)
        return () => {
            document.removeEventListener('click', handleClickEvents)
        }
    }, [ref])

    return outClicked
}

export default useClickAway
