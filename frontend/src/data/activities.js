export const activityPresentations = {
  different_leaf: {
    title: 'Find the differently shaped leaf',
    prompt: 'Choose the leaf with a pointed tip.',
    options: [
      { id: 'round-left', label: 'Rounded leaf, left', symbol: '●' },
      { id: 'pointed', label: 'Pointed leaf, center', symbol: '◆', correct: true },
      { id: 'round-right', label: 'Rounded leaf, right', symbol: '●' },
    ],
    hint: 'The center leaf has a pointed diamond shape.',
  },
  ripple_path: {
    title: 'Follow the ripple path',
    prompt: 'Choose the path that follows 1 → 2 → 3.',
    options: [
      { id: 'path-a', label: 'Path 1, 3, 2', symbol: '1–3–2' },
      { id: 'path-b', label: 'Path 1, 2, 3', symbol: '1–2–3', correct: true },
      { id: 'path-c', label: 'Path 2, 1, 3', symbol: '2–1–3' },
    ],
    hint: 'The middle path keeps the numbers in order.',
  },
  flower_match: {
    title: 'Match the flower patterns',
    prompt: 'Choose the pair with the same visible pattern.',
    options: [
      { id: 'pair-a', label: 'Striped and dotted flowers', symbol: '▧  ⊙' },
      { id: 'pair-b', label: 'Two dotted flowers', symbol: '⊙  ⊙', correct: true },
      { id: 'pair-c', label: 'Plain and striped flowers', symbol: '○  ▧' },
    ],
    hint: 'The middle pair has dots on both flowers.',
  },
  flower_change: {
    title: 'Identify what changed',
    prompt: 'Choose the flower that changed from five petals to four.',
    options: [
      { id: 'flower-1', label: 'Flower one, five petals', symbol: '✿' },
      { id: 'flower-2', label: 'Flower two, four petals', symbol: '✤', correct: true },
      { id: 'flower-3', label: 'Flower three, five petals', symbol: '✿' },
    ],
    hint: 'Flower two has four visible petals.',
  },
  petal_sequence: {
    title: 'Reconstruct the petal sequence',
    prompt: 'Choose the sequence blue, green, blue.',
    options: [
      { id: 'seq-a', label: 'Blue, blue, green', symbol: 'B–B–G' },
      { id: 'seq-b', label: 'Blue, green, blue', symbol: 'B–G–B', correct: true },
      { id: 'seq-c', label: 'Green, blue, green', symbol: 'G–B–G' },
    ],
    hint: 'The requested sequence starts and ends with blue.',
  },
  clue_search: {
    title: 'Find the garden object',
    prompt: 'Find the object that is round, blue, and on the water.',
    options: [
      { id: 'reed', label: 'Tall green reed', symbol: '♒' },
      { id: 'stone', label: 'Gray garden stone', symbol: '⬭' },
      { id: 'ripple', label: 'Round blue ripple', symbol: '◎', correct: true },
    ],
    hint: 'The ripple is round, blue, and shown on water.',
  },
  garden_path: {
    title: 'Connect two garden locations',
    prompt: 'Choose the path from the gate to the blue pond.',
    options: [
      { id: 'route-a', label: 'Gate to bench', symbol: 'Gate → Bench' },
      { id: 'route-b', label: 'Gate to blue pond', symbol: 'Gate → Pond', correct: true },
      { id: 'route-c', label: 'Pond to tree', symbol: 'Pond → Tree' },
    ],
    hint: 'The middle path begins at the gate and ends at the pond.',
  },
}

export const activityLabels = Object.fromEntries(
  Object.entries(activityPresentations).map(([key, value]) => [key, value.title]),
)
