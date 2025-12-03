/* eslint-disable camelcase */
const roleData = {
    ADMINISTRATOR: {
        Overview: {
            path: '/dashboard/overview',
            label: 'Overview',
            children: [
                {
                    label: 'Pending Approvals',
                    path: '/dashboard/overview/approvals',
                    defaultPage: true,
                },
                {
                    label: 'Notifications',
                    path: '/dashboard/overview/notifications',
                },
            ],
        },
        Advertisers: {
            path: '/dashboard/advertisers/list',
            label: 'Advertisers',
        },
        Campaigns: {
            path: '/dashboard/campaigns',
            label: 'Orders',
            children: [
                {
                    label: 'Campaigns',
                    path: '/dashboard/campaigns/list',
                },
                {
                    label: 'Line Items',
                    path: '/dashboard/lineitems/list',
                },
            ],
        },
        Creatives: {
            path: '/dashboard/creatives/list',
            label: 'Creatives',
        },
        Taxonomy: {
            path: '/dashboard/adunits',
            label: 'Taxonomy',
            children: [
                {
                    label: 'Ad Units',
                    path: '/dashboard/taxonomy/listAdUnits',
                },
                {
                    label: 'Key-Values',
                    path: '/dashboard/taxonomy/listKeyValues',
                },
                {
                    label: 'Audiences',
                    path: '/dashboard/taxonomy/listAudiences',
                },
            ],
        },
        Admin: {
            path: '/dashboard/admin',
            label: 'Settings',
            children: [
                {
                    label: 'Global Settings',
                    path: '/dashboard/settings/global',
                },
                {
                    label: 'Companies',
                    path: '/dashboard/advertisers/companies',
                },
                {
                    label: 'Templates',
                    path: '/dashboard/lineitems/templates',
                },
                {
                    label: 'Access & Authorization',
                    path: '/dashboard/settings/access-authorization',
                },
                {
                    label: 'Wallets',
                    path: '/dashboard/wallet/list',
                },
                {
                    label: 'Rate Cards',
                    path: '/dashboard/settings/rates',
                },
                {
                    label: 'Change History',
                    path: '/dashboard/settings/change-history',
                },
                {
                    label: 'Feature Access',
                    path: '/dashboard/settings/access-history',
                },
            ],
        },
    },
    CAMPAIGN_TRAFFICKER: {
        Overview: {
            path: '/dashboard/overview',
            label: 'Overview',
            children: [
                {
                    label: 'Notifications',
                    path: '/dashboard/overview/notifications',
                    defaultPage: true,
                },
            ],
        },
        Advertisers: {
            path: '/dashboard/advertisers',
            label: 'Advertisers',
        },
        Campaigns: {
            path: '/dashboard/campaigns',
            label: 'Orders',
            children: [
                {
                    label: 'Campaigns',
                    path: '/dashboard/campaigns',
                },
                {
                    label: 'Line Items',
                    path: '/dashboard/lineitems',
                },
            ],
        },
        Creatives: {
            path: '/dashboard/creatives',
            label: 'Creatives',
        },
    },
    CAMPAIGN_MANAGER: {
        Overview: {
            path: '/dashboard/overview',
            label: 'Overview',
            children: [
                {
                    label: 'Pending Approvals',
                    path: '/dashboard/overview/approvals',
                    defaultPage: true,
                },
                {
                    label: 'Notifications',
                    path: '/dashboard/overview/notifications',
                },
            ],
        },
        Advertisers: {
            path: '/dashboard/advertisers',
            label: 'Advertisers',
        },
        Campaigns: {
            path: '/dashboard/campaigns',
            label: 'Orders',
            children: [
                {
                    label: 'Campaigns',
                    path: '/dashboard/campaigns',
                },
                {
                    label: 'Line Items',
                    path: '/dashboard/lineitems',
                },
            ],
        },
        Creatives: {
            path: '/dashboard/creatives',
            label: 'Creatives',
        },
        Admin: {
            path: '/dashboard/admin',
            label: 'Settings',
            children: [
                {
                    label: 'Companies',
                    path: '/dashboard/advertisers/companies',
                },
                {
                    label: 'Access & Authorization',
                    path: '/dashboard/settings/access-authorization',
                },
                {
                    label: 'Wallets',
                    path: '/dashboard/wallet',
                },
                {
                    label: 'Rate Cards',
                    path: '/dashboard/settings/rates',
                },
                {
                    label: 'Change History',
                    path: '/dashboard/settings/change-history',
                },
                {
                    label: 'Templates',
                    path: '/dashboard/lineitems/templates',
                },
                {
                    label: 'Feature Access',
                    path: '/dashboard/settings/access-history',
                },
            ],
        },
    },
    VERTEX_ADMIN: {
        Vertex: {
            path: '/dashboard/vertex',
            label: 'Vertex',
            children: [
                {
                    label: 'Product Search',
                    path: '/dashboard/vertex/productSearch',
                    defaultPage: true,
                },
                {
                    label: 'Offsite URL creation',
                    path: '/dashboard/vertex/utmMapping',
                },
                {
                    label: 'Offsite URL history',
                    path: '/dashboard/vertex/UtmMappingHistory',
                },
                {
                    label: 'Attribution',
                    path: '/dashboard/vertex/attribution',
                },
            ],
        },
    },
    HORIZON_USER: {
        Reporting: {
            label: 'Reports',
            children: [
                {
                    label: 'Display',
                    path: '/dashboard/reporting/display',
                    defaultPage: true,
                },
                {
                    label: 'Meta',
                    path: '/dashboard/reporting/meta',
                },
                {
                    label: 'Yahoo',
                    path: '/dashboard/reporting/yahoo',
                },
            ],
        },
    },
    HORIZON_ADMIN: {
        Reporting: {
            label: 'Reports',
            children: [
                {
                    label: 'Display',
                    path: '/dashboard/reporting/display',
                    defaultPage: true,
                },
                {
                    label: 'Meta',
                    path: '/dashboard/reporting/meta',
                },
                {
                    label: 'Yahoo',
                    path: '/dashboard/reporting/yahoo',
                },
            ],
        },
    },
}

const userInfoData = {
    uniqueid: null,
    user_type: null,
    given_name: 'Sai Sidharth',
    family_name: 'Giridharan',
    email: 'saisidharth.giridharan@<url>.com',
    authorities: [
        'confluence-users',
        'UG_SOUTHDEEP_HORIZON_ADMIN',
        'Pluralsight_IND2',
        'stash-users',
        'ATL_Bitbucket_E-MNP_Admin',
        'Callinline_jobcode_FR',
        'jira-users',
        'VG_SOUTHDEEP_VERTEX_VIEWER',
        'ATL_Bitbucket_E-MFE_Write',
        'Kronos_Corp_Ext_Access',
        'VG_SOUTHDEEP_RRD_ADMIN',
        'VG_SOUTHDEEP_VERTEX_ADMIN',
        'UG_SOUTHDEEP_VERTEX_VIEWER',
        'UG_SOUTHDEEP_ADMINISTRATOR',
        'VG_SOUTHDEEP_ADMINISTRATOR',
        'ATL_Bitbucket_E-MnM_Write',
        'WCM_sdsh_employee',
        'VG_SOUTHDEEP_HORIZON_ADMIN',
        'mrv_readonly',
        'portal_nonmanager',
    ],
    vbuList: null,
    lastLoginTime: null,
    activeVbu: null,
    sales_id: '4986110',
    memberOf: [
        'cn=confluence-users,ou=Groups,o=isd',
        'cn=UG_SOUTHDEEP_HORIZON_ADMIN,ou=Groups,o=isd',
        'cn=Pluralsight_IND2,ou=Groups,o=isd',
        'cn=stash-users,ou=Groups,o=isd',
        'cn=ATL_Bitbucket_E-MNP_Admin,ou=Groups,o=isd',
        'cn=Callinline_jobcode_FR,ou=Groups,o=isd',
        'cn=jira-users,ou=Groups,o=isd',
        'cn=VG_SOUTHDEEP_VERTEX_VIEWER,ou=Groups,o=isd',
        'cn=ATL_Bitbucket_E-MFE_Write,ou=Groups,o=isd',
        'cn=Kronos_Corp_Ext_Access,ou=Groups,o=isd',
        'cn=VG_SOUTHDEEP_RRD_ADMIN,ou=Groups,o=isd',
        'cn=VG_SOUTHDEEP_VERTEX_ADMIN,ou=Groups,o=isd',
        'cn=UG_SOUTHDEEP_VERTEX_VIEWER,ou=Groups,o=isd',
        'cn=UG_SOUTHDEEP_ADMINISTRATOR,ou=Groups,o=isd',
        'cn=VG_SOUTHDEEP_ADMINISTRATOR,ou=Groups,o=isd',
        'cn=ATL_Bitbucket_E-MnM_Write,ou=Groups,o=isd',
        'cn=WCM_sdsh_employee,ou=Groups,o=isd',
        'cn=VG_SOUTHDEEP_HORIZON_ADMIN,ou=Groups,o=isd',
        'cn=mrv_readonly,ou=Groups,o=isd',
        'cn=portal_nonmanager,ou=Groups,o=isd',
    ],
}

const fabrikConfigData = {
    vertex: {
        app: 'mnpt-vertex',
        remoteImporter: 'fabrik',
        url: 'http://localhost:3010/remoteEntry.js',
        scope: {
            productSearch: 'VertexComponent/ProductSearch',
            utmMapping: 'VertexComponent/UtmMappingTab',
            UtmMappingHistory: 'VertexComponent/UtmHistoryTab',
            qgen: 'VertexComponent/QGenSearch',
            attribution: 'VertexComponent/Attribution',
        },
        tab: {
            productSearch: 'Product Search',
            utmMapping: 'Utm Mapping',
            UtmMappingHistory: 'Utm History',
            qgen: 'QGen Search',
            attribution: 'Attribution',
        },
    },
    revenue: {
        app: 'mnpt_rdd',
        remoteImporter: 'fabrik',
        url: 'http://localhost:3010/remoteEntry.js',
        scope: {
            revenueRecognition:
                'RevenueDashboardComponent/RevenueDashboardComponent',
            channelPacing:
                'RevenueDashboardComponent/RevenueDashboardComponent',
            campaignPacing:
                'RevenueDashboardComponent/RevenueDashboardComponent',
        },
        tab: {
            revenueRecognition: 'Revenue Recognition',
            channelPacing: 'Channel Pacing',
            campaignPacing: 'Campaign Pacing',
        },
    },
    reporting: {
        app: 'horizon',
        remoteImporter: 'helix',
        url: 'http://localhost:4000/southdeep-horizon/remote.js',
        scope: {
            display: 'Horizon',
            meta: 'Horizon',
            yahoo: 'YahooHorizon',
        },
        tab: {
            display: 'Display',
            meta: 'Meta',
            yahoo: 'Yahoo',
        },
    },
}

const handlerConfig = {
    handlers: [
        {
            host: "",
            path: '/lormn/api',
            replacePath: '/southdeep-svc/presentation',
            users: ['ADMINISTRATOR', 'CAMPAIGN_TRAFFICKER'],
            roleKey: 'roleName',
        },
        {
            host: '<url>',
            path: '/vertex',
            replacePath: '/southdeep-vertex',
            users: ['VERTEX_ADMIN', 'VERTEX_VIEWER'],
            roleKey: 'vertexRoleName',
            bearerToken: 'hG*5$@L2v#9^tP&3iX!8oQ+rF6zA7y1S-cVnU4eW',
        },
    ],
}

export {fabrikConfigData, handlerConfig, roleData, userInfoData}
