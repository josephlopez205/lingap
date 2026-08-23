CREATE TABLE gaps (
  gap_id SERIAL PRIMARY KEY,
  lgu_id INT REFERENCES lgus(lgu_id),
  barangay_id INT REFERENCES barangays(barangay_id),
  sector TEXT CHECK (sector IN ('Health', 'Education', 'Infrastructure')),
  rule_id TEXT NOT NULL,
  severity_score NUMERIC(5,2),
  affected_population INT,
  evidence_data JSONB,
  centroid_lat NUMERIC(10,6),
  centroid_lng NUMERIC(10,6),
  status TEXT DEFAULT 'active',
  created_at TIMESTAMP DEFAULT now()
);

CREATE INDEX idx_gaps_lgu_id ON gaps(lgu_id);
CREATE INDEX idx_gaps_severity ON gaps(severity_score DESC);
