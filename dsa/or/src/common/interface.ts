export interface Iroutes {
    path: string
    component: any
    routes?: Array<Iroutes>
    exact?: boolean
}
