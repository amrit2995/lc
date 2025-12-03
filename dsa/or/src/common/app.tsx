/* eslint-disable no-underscore-dangle */

import compose from '@<url>/helix-core/dist/api/compose'
import helixReactrouter from '@<url>/helix-react-router-plugin'
import React from 'react'

import {ThemeVariables} from '@backyard/design-tokens/v3/light/_scProperties'
import {Fellix, Fonts, Gridv3, ThemeProvider} from '@backyard/react'
import {createGlobalStyle} from 'styled-components'
import clientRoutes from './routes'

import '../assets/app.css'
import LmnHome from './components/lmnHome'
import {Iroutes} from './interface'

// const store = {
//     rootReducer,
//     initialState,
//     saga: rootSaga,
// }

const GlobalCSS = createGlobalStyle`
   ${ThemeVariables}
   ${Fellix}
   ${Gridv3}
   ${Fonts}
`

const App = (props: any) => {
    const {routers}: {routers: Array<Iroutes>} = props

    return (
        <ThemeProvider theme={'light'} font={'fellix'}>
            <GlobalCSS />
            <LmnHome />
        </ThemeProvider>
    )
}

export default compose(helixReactrouter(clientRoutes))(React.memo(App))
