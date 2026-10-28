import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import App from './App.vue'

describe('FocusBloom foundation', () => {
  it('identifies the prototype and its safety boundary', () => {
    const wrapper = mount(App)

    expect(wrapper.get('h1').text()).toBe('FocusBloom coursework prototype')
    expect(wrapper.text()).toContain('fictional local prototype')
    expect(wrapper.text()).toContain('not therapy')
  })

  it('provides visible Focus Garden, Perspective Studio, History Garden, and Support areas', () => {
    const wrapper = mount(App)

    for (const id of ['focus-garden', 'perspective-studio', 'history-garden', 'support']) {
      expect(wrapper.get(`nav a[href="#${id}"]`).exists()).toBe(true)
      expect(wrapper.get(`section#${id}`).isVisible()).toBe(true)
    }
  })
})
