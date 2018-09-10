CREATE TABLE IF NOT EXISTS entry (
  entry_id CHAR(10) NOT NULL,
  orth VARCHAR(200) NOT NULL,
  country CHAR(2) NOT NULL,
  dpt CHAR(2) NOT NULL,
  insee CHAR(5),
  localization_insee VARCHAR(250),
  localization_entry_id CHAR(10),
  localization_certainty ENUM('high', 'low'),
  def VARCHAR(200),
  PRIMARY KEY (entry_id),
  FOREIGN KEY (insee) REFERENCES insee_communes(insee_id),
  FOREIGN KEY (localization_insee) REFERENCES insee_communes(insee_id)
  );

CREATE INDEX IX_entry_localization_insee ON entry (localization_insee);

CREATE TABLE IF NOT EXISTS alt_orth (
  entry_id CHAR(10) NOT NULL,
  alt_orth VARCHAR(200) NOT NULL,
  FOREIGN KEY (entry_id) REFERENCES entry(entry_id)
);

CREATE TABLE IF NOT EXISTS keywords (
  entry_id CHAR(10) NOT NULL,
  term VARCHAR(400) NOT NULL,
  FOREIGN KEY (entry_id) REFERENCES entry(entry_id)
);

CREATE TABLE IF NOT EXISTS old_orth (
  id INT NOT NULL AUTO_INCREMENT,
  old_orth_id VARCHAR(13) NOT NULL UNIQUE,
  entry_id CHAR(10) NOT NULL,
  old_orth VARCHAR(250) NOT NULL,
  date_rich VARCHAR(100),
  date_nude VARCHAR(100),
  reference_rich TEXT,
  reference_nude TEXT,
  full_old_orth_html TEXT,
  full_old_orth_nude TEXT,
  PRIMARY KEY (id),
  FOREIGN KEY (entry_id) REFERENCES entry(entry_id)
);