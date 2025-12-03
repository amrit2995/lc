/**
 * packages which doesn't have the types module to be declared here
 */
declare module '@backyard/design-tokens'
declare module '@fullstory/browser'
declare module '@backyard/design-tokens/*'
declare module '@<url>/helix-core/*'
declare module '@<url>/helix-react-router-plugin'
declare module '@<url>/helix-prometheus'
declare module '@hapi/joi'
declare module '@<url>/helix-i18next-plugin'
declare module '@<url>/helix-i18next-plugin/*'
declare module '@<url>/helix-i18next-plugin/*/*'
declare module '@<url>/*-i18next'
declare module '@<url>/helix-prometheus*'
declare module '@<url>/helix-redux*'

declare module '@<url>/helix-graphql-express-plugin'
declare module '*.svg' {
    const content: any
    export default content
}

declare module '*.png' {
    const value: string
    export default value
}

declare module '*.ico' {
    const value: string
    export default value
}
