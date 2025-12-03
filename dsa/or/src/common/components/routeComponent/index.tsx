import React from 'react'
import {Route, Switch, useHistory} from 'react-router-dom'
import {Iroutes} from '../../interface'
import {RouteProps} from './interface'

const RouteComponent = ({routes}: RouteProps) => {
    const history = useHistory()

    return (
        <>
            <Switch>
                {routes.map((route: Iroutes) => (
                    <Route
                        key={route.path}
                        path={route.path}
                        exact={route.exact || false}
                        render={() => (
                            <route.component routes={route.routes} {...route} />
                        )}
                    />
                ))}
            </Switch>
        </>
    )
}

export default React.memo(RouteComponent)
