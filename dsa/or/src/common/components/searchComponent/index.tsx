import React, {useCallback, useEffect, useState} from 'react'
import debounce from 'lodash/debounce'
import {ClickAwayListener, TextField, Typography} from '@backyard/react'
import {SearchIcon} from '@backyard/icons'
import {ProgressBar, ProgressBarContainer, SearchPopper} from './styles'
import nameSearch from '../../utils/kuber/search'
import EntityFragment from './entityFragment'

const SearchComponent: React.FC = () => {
    const [anchorEl, setAnchorEl] = useState<HTMLElement | null>(null)
    const [loader, setLoader] = useState<boolean>(false)
    const [value, setValue] = useState<string>('')
    const [results, setResults] = useState<any[]>([])
    const open = Boolean(anchorEl)

    useEffect(() => {
        if (!value) {
            handleClear()
        }
    }, [value])

    useEffect(() => {
        return () => debouncedChangeHandler.cancel()
    }, [])

    const handleClear = () => {
        setLoader(false)
        setValue('')
        setResults([])
        setAnchorEl(null)
    }
    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        // eslint-disable-next-line no-shadow
        const {value} = e.target
        setValue(value)
        setAnchorEl(e.currentTarget)
        if (value) {
            setLoader(true)
            debouncedChangeHandler(value)
        }
    }

    const debouncedChangeHandler = useCallback(
        debounce(async (name: string) => {
            const [_, data] = await nameSearch(name)
            setResults(
                data?.creativeResults?.length ||
                    data?.displayLineItems?.length ||
                    data?.sponsoredLineItems?.length ||
                    data?.displayOrders?.length ||
                    data?.sponsoredOrders?.length ||
                    data?.advertisers?.length ||
                    data?.wallets?.length
                    ? data
                    : [],
            )
            setLoader(false)
        }, 500),
        [],
    )

    let content
    if (loader) {
        content = (
            <ProgressBarContainer>
                <ProgressBar />
            </ProgressBarContainer>
        )
    } else if (results.length === 0) {
        content = (
            <div style={{fontFamily: 'Fellix, Arial, sans-serif'}}>
                No results found!
            </div>
        )
    } else {
        content = (
            <>
                <Typography>
                    {results?.creativeResults && (
                        <EntityFragment
                            displayEntityType={'Creatives'}
                            entityType={'Creatives'}
                            data={results?.creativeResults}
                            handleClear={handleClear}
                        />
                    )}
                </Typography>
                <Typography>
                    {results?.displayLineItems && (
                        <EntityFragment
                            displayEntityType={'Display LineItems'}
                            entityType={'LineItems'}
                            data={results?.displayLineItems}
                            handleClear={handleClear}
                        />
                    )}
                </Typography>
                <Typography>
                    {results?.sponsoredLineItems && (
                        <EntityFragment
                            displayEntityType={'Sponsored LineItems'}
                            entityType={'LineItems'}
                            data={results?.sponsoredLineItems}
                            handleClear={handleClear}
                        />
                    )}
                </Typography>
                <Typography>
                    {results?.displayOrders && (
                        <EntityFragment
                            displayEntityType={'Display Campaigns'}
                            entityType={'Campaigns'}
                            data={results?.displayOrders}
                            handleClear={handleClear}
                        />
                    )}
                </Typography>
                <Typography>
                    {results?.sponsoredOrders && (
                        <EntityFragment
                            displayEntityType={'Sponsored Campaigns'}
                            entityType={'Campaigns'}
                            data={results?.sponsoredOrders}
                            handleClear={handleClear}
                        />
                    )}
                </Typography>
                <Typography>
                    {results?.advertisers && (
                        <EntityFragment
                            displayEntityType={'Advertisers'}
                            entityType={'Advertisers'}
                            data={results?.advertisers}
                            handleClear={handleClear}
                        />
                    )}
                </Typography>
                <Typography>
                    {results?.wallets && (
                        <EntityFragment
                            displayEntityType={'Wallet'}
                            entityType={'Wallet'}
                            data={results?.wallets}
                            handleClear={handleClear}
                        />
                    )}
                </Typography>
            </>
        )
    }

    return (
        <ClickAwayListener onClickAway={handleClear}>
            <div>
                <TextField
                    size="medium"
                    ref={anchorEl}
                    placeholder="Search"
                    wrapperProps={{
                        style: {
                            width: '615px',
                            WebkitTextFillColor: 'rgba(255, 255, 255, 1)',
                            caretColor: 'rgba(255, 255, 255, 1)',
                        },
                    }}
                    itemAfter={<SearchIcon />}
                    value={value}
                    onChange={handleChange}
                />

                {open && (
                    <SearchPopper anchorEl={anchorEl}>{content}</SearchPopper>
                )}
            </div>
        </ClickAwayListener>
    )
}

export default React.memo(SearchComponent)
