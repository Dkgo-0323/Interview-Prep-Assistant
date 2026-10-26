-- Bounded to two latest attempts per record; no prompts/errors/tokens stored.
CREATE TABLE IF NOT EXISTS preparation_tasks (
    record_id uuid NOT NULL REFERENCES preparations(id) ON DELETE CASCADE,
    kind text NOT NULL CHECK (kind IN ('analysis', 'questions')),
    revision bigint NOT NULL,
    attempt uuid NOT NULL,
    status text NOT NULL CHECK (status IN ('running', 'completed', 'failed', 'interrupted')),
    updated_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (record_id, kind)
);
