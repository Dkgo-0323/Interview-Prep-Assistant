CREATE TABLE IF NOT EXISTS accounts (
    id uuid PRIMARY KEY,
    github_id bigint NOT NULL UNIQUE CHECK (github_id > 0)
);
CREATE TABLE IF NOT EXISTS preparations (
    id uuid PRIMARY KEY,
    owner_id uuid NOT NULL REFERENCES accounts(id),
    title text NOT NULL CHECK (length(title) BETWEEN 1 AND 100),
    revision bigint NOT NULL DEFAULT 0,
    inputs jsonb NOT NULL DEFAULT '{}'::jsonb,
    results jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS preparations_owner ON preparations(owner_id, updated_at DESC);
