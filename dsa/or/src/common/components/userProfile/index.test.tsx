import React from 'react'
import {shallow} from 'enzyme'
import UserProfile from '.'

describe('<UserProfile />', () => {
    it('renders <UserProfile /> component', () => {
        const wrapper = shallow(<UserProfile />)
        expect(wrapper.length).toStrictEqual(1)
    })
})
