import React, {createContext, useState, ReactNode, useContext} from 'react'

interface NavigationContextType {
    autoNavigate: boolean
    setAutoNavigate: (value: boolean) => void
}

// Create context with default values
export const NavigationContext = createContext<NavigationContextType>({
    autoNavigate: false,
    setAutoNavigate: () => {},
})

// Custom hook for using the navigation context
export const useNavigation = () => useContext(NavigationContext)

interface NavigationProviderProps {
    children: ReactNode
}

// Provider component
export const NavigationProvider: React.FC<NavigationProviderProps> = ({
    children,
}) => {
    const [autoNavigate, setAutoNavigate] = useState<boolean>(false)

    return (
        <NavigationContext.Provider value={{autoNavigate, setAutoNavigate}}>
            {children}
        </NavigationContext.Provider>
    )
}
