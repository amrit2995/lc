import styled from 'styled-components'

export const UserInfoTile = styled.div`
    position: relative;
    display: flex;
    -webkit-box-align: center;
    align-items: center;
    -webkit-box-pack: center;
    justify-content: center;
    flex-shrink: 0;
    width: 40px;
    height: 40px;
    font-size: 1.25rem;
    line-height: 1;
    user-select: none;
    background-color: black;
    color: rgb(255, 255, 255);
    border-radius: 50%;
    overflow: hidden;
    border-width: 1px;
    border-style: solid;
    border-color: rgb(255, 255, 255);
    border-image: initial;
`
export const UserInfoTile2 = styled.div`
    position: relative;
    display: flex;
    -webkit-box-align: center;
    align-items: center;
    -webkit-box-pack: center;
    justify-content: center;
    flex-shrink: 0;
    line-height: 1;
    border-radius: 50%;
    overflow: hidden;
    user-select: none;
    background-color: rgb(230, 233, 240);
    height: 70px;
    width: 70px;
    font-size: 30px;
    color: black;
`

export const OverrideStyles = styled.div`
    .button {
        outline: none;
    }
`
export const TileWrapper = styled.div`
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    background-color: #f5fafd;
    padding-top: 16px;
    width: 240px;
`

export const PaddingTop16 = styled.div`
    padding: 10px 16px 0 16px;
`

export const LogoutButton = styled.div`
    .button {
        background: white !important;
        border: white !important;
        width: 2cm !important;
    }
`
export const RoleNameBorder = styled.div`
    border: 1px solid rgba(0, 0, 0, 0.7);
    border-radius: 2px;
    padding-left: 5px;
    padding-right: 5px;
`

export const RoleName = styled.div`
    font-weight: 400;
    font-size: 14px;
    line-height: 24px;
    text-align: center;
    letter-spacing: 0.015em;
    color: rgba(0, 0, 0, 0.88);
`

export const AvatarIcon = styled.div`
    font-size: 30px;
`
