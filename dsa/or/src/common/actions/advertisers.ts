import {call, put} from 'redux-saga/effects'
import getAdvertisers from '../utils/kuber/advertisers'
import {START_TABLE_LOADER, STOP_TABLE_LOADER} from './apiHelper'

export const SET_ADVERTISERS = 'SET_ADVERTISERS'
export const GET_ADVERTISERS = 'GET_ADVERTISERS'
export const SET_CURRENT_ADVERTISER = 'SET_CURRENT_ADVERTISER'

export const getAdvertisersAction = function* (action) {
    yield put({
        type: START_TABLE_LOADER,
    })
    const [_, advertisers] = yield call(getAdvertisers, {})
    yield put({
        type: STOP_TABLE_LOADER,
    })
    yield put({
        type: SET_ADVERTISERS,
        payload: advertisers || [],
    })
}
