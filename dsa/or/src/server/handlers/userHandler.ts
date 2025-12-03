import {findOne} from '../mongo/client'
import {processMFEUserDetails} from '../proxyMiddleware/handler'
import {get} from '../redis/utils'
import {MFEUserDetails, UserSession} from './interfaces/sessionProps'

const findUser = async (request: any, response: any) => {
    try {
        const userId = request?.params?.userId
        const userDetails = await findOne('user', 'userId', userId)
        if (!userDetails) {
            response.send({message: 'User not found!'})
        } else {
            response.send({...userDetails})
        }
    } catch (error) {
        request.log.error(error)
        response.status(500).send({message: 'Error in finding user!'})
    }
}

const getMFEUserInfo = async (req: any, res: any) => {
    const hashToken = req.params.sessionToken
    if (!hashToken) {
        return res.status(401).json({message: 'Missing Authorization token'})
    }
    try {
        const userSession: UserSession = await get(hashToken)
        const mfeUserDetails: MFEUserDetails = await processMFEUserDetails(
            userSession,
        )
        return res.status(200).json(mfeUserDetails)
    } catch (error) {
        req.log.error('getMFEUserInfo error:', error?.message)
        return res.status(403).json({message: 'Session not found or expired'})
    }
}

export {findUser, getMFEUserInfo}
