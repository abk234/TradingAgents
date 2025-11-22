/*
 * Copyright (c) 2024. All rights reserved.
 * Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.
 */

import { Construction } from "lucide-react"

interface ViewPlaceholderProps {
    title: string
}

export function ViewPlaceholder({ title }: ViewPlaceholderProps) {
    return (
        <div className="flex flex-col items-center justify-center h-full text-muted-foreground p-8 border-2 border-dashed border-border rounded-xl bg-card/50">
            <Construction className="w-16 h-16 mb-4 opacity-50" />
            <h3 className="text-xl font-semibold mb-2">{title}</h3>
            <p>This feature is currently under development.</p>
        </div>
    )
}
