package main

import (
	"log"

	"threatlens/backend-go/internal/api"
	"threatlens/backend-go/internal/config"
	"threatlens/backend-go/internal/db"
)

func main() {
	cfg := config.Load()
	sqlDB, err := db.Connect(cfg.DBPath)
	if err != nil {
		log.Fatalf("db error: %v", err)
	}
	router := api.NewRouter(cfg, sqlDB)
	log.Printf("ThreatLens backend-go listening on :%s", cfg.Port)
	if err := router.Run(":" + cfg.Port); err != nil {
		log.Fatalf("server error: %v", err)
	}
}
