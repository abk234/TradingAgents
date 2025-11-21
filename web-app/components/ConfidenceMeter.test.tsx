import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ConfidenceMeter } from './ConfidenceMeter'

describe('ConfidenceMeter', () => {
    it('renders correctly with label', () => {
        render(<ConfidenceMeter score={0.8} />)
        expect(screen.getByText('Confidence')).toBeDefined()
        expect(screen.getByText('80%')).toBeDefined()
    })

    it('hides label when showLabel is false', () => {
        render(<ConfidenceMeter score={0.5} showLabel={false} />)
        expect(screen.queryByText('Confidence')).toBeNull()
    })
})
