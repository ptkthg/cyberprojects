package db

import (
	"database/sql"
	_ "github.com/mattn/go-sqlite3"
)

func Connect(path string) (*sql.DB, error) {
	db, err := sql.Open("sqlite3", path)
	if err != nil {
		return nil, err
	}
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS analyses (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		ioc TEXT NOT NULL,
		ioc_type TEXT NOT NULL,
		risk_level TEXT NOT NULL,
		case_status TEXT NOT NULL,
		updated_at TEXT NOT NULL
	)`)
	if err != nil {
		return nil, err
	}
	return db, nil
}
