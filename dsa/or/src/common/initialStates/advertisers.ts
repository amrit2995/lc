export const advertiser: AdvertiserReducerState = {
    currentAdvertiser: null,
    advertiserList: [],
}

export interface AdvertiserReducerState {
    currentAdvertiser: AdvertiserState
    advertiserList: string[]
}

export interface AdvertiserState {
    advertiserStatus: string
    externalId: string
    id: string
    name: string
    userTimeZone: string
    users: any[]
    wallets: WalletState[]
}

export interface WalletState {
    advertiserId: string
    createdAt: string
    currentBalance: number
    externalId: string
    id: string
    initialBalance: number
    lastSyncedAt: string
    lastUpdatedAt: string
    name: string
    partnerData: any
    status: string
    walletThreshold: string
    walletTransactions: any[]
}
