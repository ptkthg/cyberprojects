package api

import (
	"database/sql"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"threatlens/backend-go/internal/config"
	"threatlens/backend-go/internal/services"
)

func NewRouter(cfg config.Config, db *sql.DB) *gin.Engine {
	r := gin.Default()
	r.Use(func(c *gin.Context) {
		c.Writer.Header().Set("Access-Control-Allow-Origin", cfg.AllowedFrontend)
		c.Writer.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")
		c.Writer.Header().Set("Access-Control-Allow-Methods", "GET,POST,PATCH,OPTIONS")
		if c.Request.Method == http.MethodOptions {
			c.AbortWithStatus(http.StatusNoContent)
			return
		}
		c.Next()
	})

	api := r.Group("/api")
	{
		api.GET("/health", func(c *gin.Context) { c.JSON(200, gin.H{"status": "ok", "service": "threatlens-backend-go"}) })
		api.GET("/dashboard/stats", func(c *gin.Context) {
			c.JSON(200, gin.H{"total": 39, "open_cases": 25, "active_sources": 7})
		})
		api.POST("/ioc/analyze", func(c *gin.Context) {
			var payload struct{ IOC string `json:"ioc"` }
			if err := c.ShouldBindJSON(&payload); err != nil {
				c.JSON(400, gin.H{"error": "payload inválido"}); return
			}
			n := services.NormalizeIOC(payload.IOC)
			t := services.DetectIOCType(n)
			c.JSON(200, gin.H{"ioc": n, "ioc_type": t, "risk_level": "Médio", "score": 55, "kql": services.BuildKQL(n, t)})
		})
		api.GET("/ioc/history", func(c *gin.Context) { c.JSON(200, gin.H{"items": []gin.H{}}) })
		api.GET("/ioc/history/:id", func(c *gin.Context) { c.JSON(200, gin.H{"id": c.Param("id")}) })
		api.GET("/ioc/search", func(c *gin.Context) { c.JSON(200, gin.H{"q": c.Query("q"), "items": []gin.H{}}) })
		api.GET("/cases", func(c *gin.Context) { c.JSON(200, gin.H{"items": []gin.H{}}) })
		api.GET("/cases/:id", func(c *gin.Context) { c.JSON(200, gin.H{"id": c.Param("id")}) })
		api.POST("/cases", func(c *gin.Context) { c.JSON(201, gin.H{"status": "created"}) })
		api.PATCH("/cases/:id", func(c *gin.Context) { c.JSON(200, gin.H{"status": "updated", "id": c.Param("id")}) })
		api.GET("/sources/health", func(c *gin.Context) {
			c.JSON(200, gin.H{"VirusTotal": keyStatus(cfg.VirusTotalAPIKey), "AbuseIPDB": keyStatus(cfg.AbuseIPDBAPIKey), "URLHaus": keyStatus(cfg.URLHausAPIKey), "IPinfo": keyStatus(cfg.IPInfoAPIKey), "OpenAI": keyStatus(cfg.OpenAIAPIKey)})
		})
		api.POST("/ai/analyze", func(c *gin.Context) {
			if cfg.OpenAIAPIKey == "" {
				c.JSON(200, gin.H{"status": "Sem API key", "message": "OPENAI_API_KEY ausente. Configure no .env."}); return
			}
			c.JSON(200, gin.H{"executive_summary": "Análise IA mockada para validação incremental.", "technical_interpretation": "Validar IOC em telemetria interna.", "risk_reasoning": "Baseado em sinais externos limitados.", "confidence_assessment": "Média", "recommended_actions": []string{"Correlacionar com logs de proxy", "Revisar DeviceNetworkEvents"}, "validation_points": []string{"Confirmar contexto interno"}, "hunting_suggestions": []string{"Executar query KQL gerada"}, "limitations": "Sem evidências internas anexadas."})
		})
		api.GET("/config/status", func(c *gin.Context) {
			c.JSON(200, gin.H{"backend_time": time.Now().UTC().Format(time.RFC3339), "openai": keyStatus(cfg.OpenAIAPIKey), "virustotal": keyStatus(cfg.VirusTotalAPIKey), "abuseipdb": keyStatus(cfg.AbuseIPDBAPIKey), "urlhaus": keyStatus(cfg.URLHausAPIKey), "ipinfo": keyStatus(cfg.IPInfoAPIKey)})
		})
	}

	_ = db
	return r
}

func keyStatus(v string) string {
	if v == "" { return "Ausente" }
	return "Operacional"
}
