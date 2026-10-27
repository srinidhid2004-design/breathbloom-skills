import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import App from './App.vue'

describe('BreathBloom foundation', () => {
  it('identifies the prototype and its safety boundary', () => {
    const wrapper = mount(App)

    expect(wrapper.get('h1').text()).toBe('BreathBloom coursework prototype')
    expect(wrapper.text()).toContain('fictional local prototype')
    expect(wrapper.text()).toContain('not therapy')
  })

  it('provides visible Practice, History, and Support areas', () => {
    const wrapper = mount(App)

    for (const id of ['practice', 'history', 'support']) {
      expect(wrapper.get(`nav a[href="#${id}"]`).exists()).toBe(true)
      expect(wrapper.get(`section#${id}`).isVisible()).toBe(true)
    }
  })
})
