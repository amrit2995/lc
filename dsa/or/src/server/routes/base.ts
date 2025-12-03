const basePath = process.env.BASE_PATH

export default [
    {
        method: 'GET',
        path: basePath,
    },
    {
        method: 'GET',
        path: `${basePath}/logout`,
    },
    {
        method: 'GET',
        path: `${basePath}/dashboard`,
    },
    {
        method: 'GET',
        path: `${basePath}/enterprise-social/:entity`,
    },
    {
        method: 'GET',
        path: `${basePath}/enterprise-social/:entity/view`,
    },
    {
        method: 'GET',
        path: `${basePath}/dashboard/:entity/:action`,
    },
    {
        method: 'GET',
        path: `${basePath}/dashboard/:entity/:action/:id`,
    },
    {
        method: 'GET',
        path: `${basePath}/403`,
    },
]
