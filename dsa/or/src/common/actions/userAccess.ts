import {call, put} from 'redux-saga/effects'
import {getRoleNameFromAuthorities} from '../utils/commonUtils'
import {getUserAccess, verifyVBU} from '../utils/kuber/session'

export const SET_USER_ACCESS = 'SET_USER_ACCESS'
export const SET_VBU_DETAILS = 'SET_VBU_DETAILS'
export const FETCH_USER_ACCESS = 'FETCH_USER_ACCESS'
export const AUTHENTICATED_USER = 'AUTHENTICATED_USER'

export const getUserAccessAction = function* (action) {
    const [, access] = yield call(getUserAccess, {})
    if (access?.vbuList?.length) {
        const [, vbuDetails] = yield call(verifyVBU, {vbus: access?.vbuList})
        yield put({
            type: SET_VBU_DETAILS,
            payload: vbuDetails,
        })
    }
    yield put({
        type: SET_USER_ACCESS,
        payload: getRoleNameFromAuthorities(access) || {},
    })
}
