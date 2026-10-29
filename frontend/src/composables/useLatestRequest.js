import { onBeforeUnmount, ref } from 'vue'

export function useLatestRequest() {
  const activeId = ref(0)
  let controller = null

  function begin() {
    controller?.abort()
    controller = new AbortController()
    const id = activeId.value + 1
    activeId.value = id
    return { id, signal: controller.signal }
  }

  function isCurrent(id) {
    return activeId.value === id && !controller?.signal.aborted
  }

  function cancel() {
    activeId.value += 1
    controller?.abort()
    controller = null
  }

  onBeforeUnmount(cancel)
  return { begin, isCurrent, cancel }
}
