import React from 'react'
import {shallow} from 'enzyme'
import NotificationDraw from '.'

describe('<NotificationDraw />', () => {
    it('renders <NotificationDraw /> component', () => {
        const wrapper = shallow(<NotificationDraw />)
        expect(wrapper.length).toStrictEqual(1)
    })
})
