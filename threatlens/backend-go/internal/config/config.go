package config

import (
	"os"

	"github.com/joho/godotenv"
)

type Config struct {
	Port              string
	DBPath            string
	OpenAIAPIKey      string
	VirusTotalAPIKey  string
	AbuseIPDBAPIKey   string
	URLHausAPIKey     string
	IPInfoAPIKey      string
	AllowedFrontend   string
}

func Load() Config {
	_ = godotenv.Load()
	return Config{
		Port:            getOrDefault("PORT", "8080"),
		DBPath:          getOrDefault("DB_PATH", "./threatlens-go.db"),
		OpenAIAPIKey:    os.Getenv("OPENAI_API_KEY"),
		VirusTotalAPIKey: os.Getenv("VIRUSTOTAL_API_KEY"),
		AbuseIPDBAPIKey: os.Getenv("ABUSEIPDB_API_KEY"),
		URLHausAPIKey:   os.Getenv("URLHAUS_API_KEY"),
		IPInfoAPIKey:    os.Getenv("IPINFO_API_KEY"),
		AllowedFrontend: getOrDefault("FRONTEND_ORIGIN", "http://localhost:3000"),
	}
}

func getOrDefault(key, fallback string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return fallback
}
