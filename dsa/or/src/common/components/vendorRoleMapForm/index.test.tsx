import React from 'react'
import {shallow} from 'enzyme'
import VendorRoleMapForm from '.'

describe('<VendorRoleMapForm />', () => {
    it('renders <VendorRoleMapForm /> component', () => {
        const wrapper = shallow(<VendorRoleMapForm />)
        expect(wrapper.length).toStrictEqual(1)
    })
})
