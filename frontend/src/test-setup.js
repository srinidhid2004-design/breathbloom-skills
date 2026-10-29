import { vi } from 'vitest'

if (!globalThis.crypto?.randomUUID) {
  Object.defineProperty(globalThis, 'crypto', { value: { randomUUID: vi.fn(() => '11111111-1111-4111-8111-111111111111') } })
}
