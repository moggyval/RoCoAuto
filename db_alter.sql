-- db_alter.sql
-- Run this once in MySQL to support share links + calendar.

ALTER TABLE documents
  ADD COLUMN share_token VARCHAR(64) NULL,
  ADD UNIQUE INDEX uq_documents_share_token (share_token);

CREATE TABLE IF NOT EXISTS appointments (
  id VARCHAR(36) NOT NULL,
  ro_id VARCHAR(36) NOT NULL,
  title VARCHAR(255) NOT NULL,
  start_at DATETIME NOT NULL,
  end_at DATETIME NOT NULL,
  status VARCHAR(30) NOT NULL DEFAULT 'scheduled',
  notes TEXT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  INDEX idx_appt_ro_id (ro_id),
  CONSTRAINT fk_appt_ro FOREIGN KEY (ro_id) REFERENCES repair_orders(id)
);

ALTER TABLE customers
  ADD COLUMN deleted_at DATETIME NULL;

ALTER TABLE repair_orders
  ADD COLUMN deleted_at DATETIME NULL;

CREATE TABLE IF NOT EXISTS technicians (
  id VARCHAR(36) NOT NULL,
  name VARCHAR(120) NOT NULL,
  total_hours DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
);

ALTER TABLE jobs
  ADD COLUMN tech_id VARCHAR(36) NULL,
  ADD COLUMN completed_at DATETIME NULL,
  ADD INDEX idx_jobs_tech_id (tech_id),
  ADD CONSTRAINT fk_jobs_tech FOREIGN KEY (tech_id) REFERENCES technicians(id);
